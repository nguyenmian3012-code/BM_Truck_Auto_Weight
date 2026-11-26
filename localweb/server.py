"""Trang cân xe nội bộ. Chỉ đọc SQLite của AutoCan. Không gửi Cloudflare, không ghi D1."""

import os
import sqlite3
from datetime import datetime, timedelta
from html import escape as html_escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from pair import pair_tickets, vn_day

HOST = os.environ.get("CANXE_HOST", "0.0.0.0")
PORT = int(os.environ.get("CANXE_PORT", "8780"))


def db_candidates():
    found = []
    env = os.environ.get("CANXE_DB", "")
    if env:
        found.append(env)
    found.append(r"C:\ProgramData\BmCancomp\data\cancomp.db")
    local = os.environ.get("LOCALAPPDATA", "")
    if local:
        found.append(os.path.join(local, "BmCancomp", "data", "cancomp.db"))
    found.append(os.path.join(os.path.dirname(__file__), "fixture.db"))
    return found


def open_db():
    for path in db_candidates():
        if path and os.path.isfile(path):
            cx = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True, timeout=3)
            cx.row_factory = sqlite3.Row
            return cx, path
    return None, ""


def today_vn():
    return (datetime.utcnow() + timedelta(hours=7)).strftime("%Y-%m-%d")


def next_day(day):
    d = datetime.strptime(day, "%Y-%m-%d") + timedelta(days=1)
    return d.strftime("%Y-%m-%d")


def prev_day(day):
    d = datetime.strptime(day, "%Y-%m-%d") - timedelta(days=1)
    return d.strftime("%Y-%m-%d")


def esc(s):
    return html_escape(str(s if s is not None else ""), quote=True)


def kg(n):
    if n is None or n == "":
        return ""
    try:
        v = float(n)
    except (TypeError, ValueError):
        return ""
    return f"{v:,.0f}".replace(",", ".")


def load_rows(cx, since):
    sql = """
      SELECT id, source, kg, starch_pct, ts, plate, trailer_plate, customer,
             ocr_status, ocr_reason, vehicle_type, direction, yard_card
      FROM events
      WHERE IFNULL(source,'')='kingbird' AND kg IS NOT NULL AND ts>=?
      ORDER BY ts ASC, id ASC
    """
    try:
        return [dict(r) for r in cx.execute(sql, (since,)).fetchall()]
    except sqlite3.OperationalError:
        sql = """
          SELECT id, source, kg, starch_pct, ts, plate, trailer_plate, customer
          FROM events
          WHERE IFNULL(source,'')='kingbird' AND kg IS NOT NULL AND ts>=?
          ORDER BY ts ASC, id ASC
        """
        return [dict(r) for r in cx.execute(sql, (since,)).fetchall()]


def on_day(row, day):
    ts = str(row.get("ts") or "")
    return ts.startswith(day) or vn_day(ts) == day


def sessions_on(day, sessions):
    out = []
    for s in sessions:
        opened = str(s.get("opened_at") or "")
        closed = str(s.get("closed_at") or "")
        if opened.startswith(day) or closed.startswith(day) or vn_day(opened) == day or vn_day(closed) == day:
            out.append(s)
    out.sort(key=lambda s: str(s.get("opened_at") or ""), reverse=True)
    return out


PAGE = """<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
body{{font:14px/1.45 system-ui,sans-serif;margin:24px;background:#2a0a12;color:#f6eee6}}
a{{color:#d4af37}} table{{border-collapse:collapse;width:100%}}
td,th{{border-bottom:1px solid #6b2a34;padding:8px;text-align:left}}
.cards{{display:flex;gap:12px;flex-wrap:wrap}}
.card{{background:#4a1820;border-radius:12px;padding:14px 18px;min-width:140px}}
.card b{{display:block;font-size:28px;font-weight:600}}
form{{display:flex;gap:8px;align-items:center;margin:8px 0}}
input{{background:#4a1820;color:#f6eee6;border:1px solid #6b2a34;padding:8px;border-radius:8px}}
small{{color:#e7c7b0}}
</style>
<p><a href="/?ngay={day}">Hôm nay</a> · <a href="/phieu?ngay={day}">Phiếu</a> · <a href="/sessions?ngay={day}">Phiên</a>
 · <small>nội bộ · không ghi D1 · {db}</small></p>
{body}
"""


def shell(title, day, db, body):
    name = os.path.basename(db) if db else "chưa thấy cancomp.db"
    return PAGE.format(title=esc(title), day=esc(day), db=esc(name), body=body).encode("utf-8")


def day_nav(day, path):
    return (
        f'<form action="{esc(path)}"><a href="{esc(path)}?ngay={esc(prev_day(day))}">← Hôm trước</a>'
        f'<input type="date" name="ngay" value="{esc(day)}"><button>Xem</button>'
        f'<a href="{esc(path)}?ngay={esc(next_day(day))}">Hôm sau →</a></form>'
    )


def render_home(day, rows, sessions, db):
    today_rows = [r for r in rows if on_day(r, day)]
    today = sessions_on(day, sessions)
    mi = [s for s in today if s["status"] == "closed" and s["card"] == "nhap_mi"]
    bot = [s for s in today if s["status"] == "closed" and s["card"] == "xuat_bot"]
    opens = [s for s in today if s["status"] == "open"]

    def tons(lst):
        return f"{sum(float(s['net_kg'] or 0) for s in lst) / 1000:.1f}".replace(".", ",")

    cards = (
        '<div class="cards">'
        f'<div class="card">Xe nhập mì<b>{len(mi)}</b></div>'
        f'<div class="card">Xe xuất bột<b>{len(bot)}</b></div>'
        f'<div class="card">Tấn mì<b>{tons(mi)}</b></div>'
        f'<div class="card">Tấn bột<b>{tons(bot)}</b></div>'
        "</div>"
    )
    body_rows = "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
        % (esc(s["plate"]), esc(s["card"]), esc(kg(s["kg_in"])), esc(s["note"]))
        for s in opens
    )
    body = (
        f"<h1>Cân xe {esc(day)}</h1>{cards}<p>{len(today_rows)} phiếu trong ngày · {len(opens)} phiên đang mở.</p>"
        + day_nav(day, "/")
        + "<h2>Đang trong nhà máy</h2><table><tr><th>Biển</th><th>Loại</th><th>Kg vào</th><th>Ghi chú</th></tr>"
        + (body_rows or "<tr><td colspan=4>Không có xe đang mở.</td></tr>")
        + "</table>"
    )
    return shell("Cân xe " + day, day, db, body)


def render_phieu(day, rows, db):
    today = [r for r in rows if on_day(r, day)]
    today.sort(key=lambda r: str(r.get("ts") or ""), reverse=True)
    lines = []
    for r in today:
        when = str(r.get("ts") or "").replace("T", " ")[:16]
        reason = r.get("ocr_reason") or r.get("ocr_status") or ""
        lines.append(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (
                esc(when),
                esc(r.get("plate") or ""),
                esc(kg(r.get("kg"))),
                esc(r.get("plate") or ""),
                esc(reason),
                esc(r.get("yard_card") or r.get("direction") or ""),
            )
        )
    body = (
        f"<h1>Phiếu {esc(day)}</h1><p>{len(today)} lần cân. Đọc từ sổ AutoCan trên máy này.</p>"
        + day_nav(day, "/phieu")
        + "<table><tr><th>Giờ</th><th>OCR Result</th><th>Kg</th><th>Biển</th><th>Lỗi / Lý do</th><th>Hàng</th></tr>"
        + ("".join(lines) or "<tr><td colspan=6>Không có phiếu ngày này.</td></tr>")
        + "</table>"
    )
    return shell("Phiếu " + day, day, db, body)


def render_sessions(day, sessions, db):
    today = sessions_on(day, sessions)
    mi = [s for s in today if s["status"] == "closed" and s["card"] == "nhap_mi"]
    bot = [s for s in today if s["status"] == "closed" and s["card"] == "xuat_bot"]
    tons = lambda lst: f"{sum(float(s['net_kg'] or 0) for s in lst) / 1000:.1f}"
    lines = []
    for s in today:
        opened = str(s.get("opened_at") or "").replace("T", " ")[:16]
        closed = str(s.get("closed_at") or "").replace("T", " ")[:16]
        lines.append(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (
                esc(s["status"]),
                esc(s["plate"]),
                esc(s["card"]),
                esc(kg(s["kg_in"])),
                esc(kg(s["kg_out"])),
                esc(kg(s["net_kg"])),
                esc(kg(s["net_kg_rounded"])),
                esc(opened),
                esc(closed),
                esc(s["note"]),
            )
        )
    body = (
        f"<h1>Phiên {esc(day)}</h1>"
        f"<p>{len(mi)} xe nhập mì · {tons(mi)} t · {len(bot)} xe xuất bột · {tons(bot)} t</p>"
        + day_nav(day, "/sessions")
        + "<table><tr><th>Trạng thái</th><th>Biển</th><th>Loại</th><th>Kg vào</th><th>Kg ra</th><th>Net</th><th>Net 20</th><th>Mở</th><th>Đóng</th><th>Ghi chú</th></tr>"
        + ("".join(lines) or "<tr><td colspan=10>Không có phiên ngày này.</td></tr>")
        + "</table>"
    )
    return shell("Phiên " + day, day, db, body)


def missing(day):
    paths = "<br>".join(esc(p) for p in db_candidates())
    body = (
        "<h1>Chưa thấy sổ cân</h1>"
        "<p>Trang này chỉ đọc file SQLite của AutoCan. Không tạo phiếu mới.</p><p>"
        + paths
        + "</p>"
    )
    return shell("Chưa thấy sổ", day, "", body)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        qs = parse_qs(url.query)
        day = (qs.get("ngay") or [today_vn()])[0]
        if not re_day(day):
            day = today_vn()
        if url.path == "/health":
            cx, path = open_db()
            n = 0
            if cx:
                try:
                    n = cx.execute("SELECT COUNT(*) FROM events").fetchone()[0]
                except sqlite3.Error:
                    n = -1
                cx.close()
            raw = ('{"ok":%s,"db":"%s","events":%d}' % ("true" if path else "false", esc(path).replace("\\", "/"), n)).encode()
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("cache-control", "no-store")
            self.end_headers()
            self.wfile.write(raw)
            return
        cx, path = open_db()
        if not cx:
            body = missing(day)
        else:
            since = prev_day(prev_day(day)) + "T00:00:00+07:00"
            try:
                rows = load_rows(cx, since)
            except sqlite3.Error as e:
                cx.close()
                body = shell("Lỗi sổ", day, path, "<h1>Không đọc được sổ</h1><p>%s</p>" % esc(e))
                self._html(body)
                return
            cx.close()
            sessions = pair_tickets(rows)
            if url.path in ("/", "/index.html"):
                body = render_home(day, rows, sessions, path)
            elif url.path == "/phieu":
                body = render_phieu(day, rows, path)
            elif url.path == "/sessions":
                body = render_sessions(day, sessions, path)
            else:
                self.send_response(404)
                self.send_header("content-type", "text/plain;charset=utf-8")
                self.end_headers()
                self.wfile.write(b"khong co")
                return
        self._html(body)

    def _html(self, body):
        self.send_response(200)
        self.send_header("content-type", "text/html;charset=utf-8")
        self.send_header("cache-control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return


def re_day(day):
    return len(day) == 10 and day[4] == "-" and day[7] == "-" and day.replace("-", "").isdigit()


def main():
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print("Trang noi bo http://127.0.0.1:%d/  (may khac trong mang: cong %d)" % (PORT, PORT), flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
