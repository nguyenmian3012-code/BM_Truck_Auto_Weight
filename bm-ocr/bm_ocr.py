"""BM-OCR. Xem ảnh và biển của từng lượt cân. Không thay app cân.

Chạy trên máy cân, chỉ nghe 127.0.0.1:8771.
Sổ cân vẫn là cancomp.db. Sửa biển ghi ngược vào sổ đó để app gửi lên web.
"""

import json
import os
import re
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8771
OCR_URL = os.environ.get("BM_OCR_URL", "http://127.0.0.1:8765/read")
PLATE_RE = re.compile(r"^\d{2}[A-Z]{1,2}-\d{3,5}(?:\.\d{2})?$")
KINDS = {
    "missing-shot": "Sót ảnh",
    "unread": "Không đọc được biển",
    "bad-plate": "Biển không đúng dạng",
    "wrong": "Đọc sai",
    "conflict": "Hai camera không khớp",
}
FLOW = {"nhap_mi": "Nhập mì", "xuat_bot": "Xuất bột", "khac": "Khác"}
VISIT = {"vao": "Vào", "ra": "Ra"}

DB_PATH = ""
REVIEW_PATH = ""


def normalize_plate(raw):
    found = re.search(
        r"\d{2}[A-Z]{1,2}-?\d{3,5}(?:\.\d{2})?",
        re.sub(r"[^0-9A-Z.\-]", "", str(raw or "").upper()),
    )
    if not found:
        return ""
    plate = found.group(0)
    if re.match(r"^\d{2}[A-Z]{1,2}\d", plate) and "-" not in plate:
        plate = re.sub(r"^(\d{2}[A-Z]{1,2})(\d)", r"\1-\2", plate, count=1)
    return plate if PLATE_RE.match(plate) else ""


def shot_exists(path):
    return bool(path) and os.path.isfile(path)


def auto_kind(row):
    plate = (row["plate"] or "").strip()
    status = (row["ocr_status"] or "").strip().lower()
    if not shot_exists(row["shot_path"]):
        return "missing-shot"
    if not plate or status in {"", "pending", "unread", "reading"}:
        return "unread"
    if not PLATE_RE.match(plate):
        return "bad-plate"
    return ""


def exception_kind(row, review):
    kind = auto_kind(row)
    if kind == "missing-shot":
        return kind
    corrected = (review or {}).get("corrected") or ""
    state = (review or {}).get("state") or ""
    if state == "resolved" and corrected and corrected == (row["plate"] or ""):
        return ""
    if state == "open":
        return (review or {}).get("kind") or kind or "wrong"
    return kind


def candidate_dbs():
    forced = os.environ.get("BM_OCR_DB")
    if forced:
        return [forced]
    found = []
    for key in ("PROGRAMDATA", "LOCALAPPDATA"):
        root = os.environ.get(key)
        if root:
            found.append(os.path.join(root, "BmCancomp", "data", "cancomp.db"))
    return found


def pick_db(paths):
    best, best_ts = "", ""
    for path in paths:
        if not os.path.isfile(path):
            continue
        try:
            cx = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=2)
            cols = {r[1] for r in cx.execute("PRAGMA table_info(events)")}
            if "shot_path" not in cols:
                cx.close()
                continue
            row = cx.execute("SELECT MAX(ts) FROM events").fetchone()
            cx.close()
        except sqlite3.Error:
            continue
        ts = (row[0] if row else "") or ""
        if not best or ts >= best_ts:
            best, best_ts = path, ts
    return best


def connect(path, write=False):
    cx = sqlite3.connect(path, timeout=5)
    cx.row_factory = sqlite3.Row
    if not write:
        cx.execute("PRAGMA query_only=ON")
    return cx


def ensure_review(path):
    cx = sqlite3.connect(path, timeout=5)
    cx.execute(
        """
        CREATE TABLE IF NOT EXISTS review (
          ticket_id TEXT PRIMARY KEY,
          kind TEXT,
          guess TEXT,
          corrected TEXT,
          note TEXT,
          state TEXT,
          updated_at TEXT
        )
        """
    )
    cx.commit()
    cx.close()


def reviews_for(ids):
    if not ids or not REVIEW_PATH:
        return {}
    cx = sqlite3.connect(REVIEW_PATH, timeout=5)
    cx.row_factory = sqlite3.Row
    marks = ",".join("?" for _ in ids)
    rows = cx.execute(
        f"SELECT ticket_id, kind, guess, corrected, note, state FROM review WHERE ticket_id IN ({marks})",
        ids,
    ).fetchall()
    cx.close()
    return {r["ticket_id"]: dict(r) for r in rows}


def save_review(ticket_id, kind, guess, corrected, note, state):
    cx = sqlite3.connect(REVIEW_PATH, timeout=5)
    cx.execute(
        """
        INSERT INTO review(ticket_id, kind, guess, corrected, note, state, updated_at)
        VALUES(?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(ticket_id) DO UPDATE SET
          kind=excluded.kind,
          guess=excluded.guess,
          corrected=excluded.corrected,
          note=excluded.note,
          state=excluded.state,
          updated_at=excluded.updated_at
        """,
        (ticket_id, kind, guess or "", corrected or "", note or "", state, datetime.now().isoformat(timespec="seconds")),
    )
    cx.commit()
    cx.close()


def clock(ts):
    text = str(ts or "")
    return text[11:19] if len(text) >= 19 else text


def public_row(row, review):
    kind = exception_kind(row, review)
    return {
        "id": row["id"],
        "time": clock(row["ts"]),
        "kg": row["kg"],
        "plate": row["plate"] or "",
        "trailer": row["trailer_plate"] or "",
        "customer": row["customer"] or "",
        "card": row["yard_card"] or "",
        "flow": FLOW.get(row["yard_card"] or "", ""),
        "visit": VISIT.get(row["visit"] or "", ""),
        "status": row["ocr_status"] or "",
        "kind": kind,
        "kindLabel": KINDS.get(kind, ""),
        "hasShot": shot_exists(row["shot_path"]),
        "guess": (review or {}).get("guess") or "",
        "note": (review or {}).get("note") or "",
        "reviewState": (review or {}).get("state") or "",
    }


def day_rows(day):
    cx = connect(DB_PATH)
    rows = cx.execute(
        """
        SELECT id, kg, ts, plate, trailer_plate, customer, yard_card, visit,
               ocr_status, shot_path, pack_dir
        FROM events
        WHERE source = 'kingbird' AND substr(ts, 1, 10) = ?
        ORDER BY ts DESC
        """,
        (day,),
    ).fetchall()
    cx.close()
    marks = reviews_for([r["id"] for r in rows])
    return [public_row(r, marks.get(r["id"])) for r in rows]


def one_row(ticket_id):
    cx = connect(DB_PATH)
    row = cx.execute(
        """
        SELECT id, kg, ts, plate, trailer_plate, customer, yard_card, visit,
               ocr_status, shot_path, pack_dir
        FROM events WHERE id = ?
        """,
        (ticket_id,),
    ).fetchone()
    cx.close()
    if row is None:
        return None
    review = reviews_for([ticket_id]).get(ticket_id)
    item = public_row(row, review)
    item["lanes"] = ["shot", "F", "R", "S"]
    return item


def image_path(ticket_id, kind):
    cx = connect(DB_PATH)
    row = cx.execute("SELECT shot_path, pack_dir FROM events WHERE id = ?", (ticket_id,)).fetchone()
    cx.close()
    if row is None:
        return None
    if kind == "shot":
        path = row["shot_path"] or ""
    elif kind in {"F", "R", "S"} and row["pack_dir"]:
        path = os.path.join(row["pack_dir"], kind + ".jpg")
    else:
        return None
    if not path or not os.path.isfile(path):
        return None
    real = os.path.realpath(path)
    if not real.lower().endswith(".jpg"):
        return None
    roots = []
    for raw in (row["shot_path"], row["pack_dir"]):
        if raw:
            roots.append(os.path.realpath(os.path.dirname(raw) if raw == row["shot_path"] else raw))
    if not any(real == root or real.startswith(root + os.sep) for root in roots):
        return None
    return real


def route_for(cx, plate, trailer):
    for key in (plate, trailer):
        if not key:
            continue
        found = cx.execute(
            "SELECT customer, yard_card FROM routes WHERE plate = ?",
            (key,),
        ).fetchone()
        if found:
            return found["customer"] or "", found["yard_card"] or ""
    return "", ""


def apply_plate(ticket_id, plate, trailer, kind, guess, note):
    plate = normalize_plate(plate)
    trailer = normalize_plate(trailer)
    if trailer == plate:
        trailer = ""
    if not plate:
        raise ValueError("bien khong dung dang")
    cx = sqlite3.connect(DB_PATH, timeout=5)
    cx.row_factory = sqlite3.Row
    cols = {r[1] for r in cx.execute("PRAGMA table_info(events)")}
    customer, card = ("", "")
    if "routes" in {r[0] for r in cx.execute("SELECT name FROM sqlite_master WHERE type='table'")}:
        customer, card = route_for(cx, plate, trailer)
    familiarity = "quen" if customer or card else "la"
    sets = ["plate = ?", "ocr_status = 'ok'"]
    args = [plate]
    if "trailer_plate" in cols:
        sets.append("trailer_plate = ?")
        args.append(trailer)
    if "customer" in cols:
        sets.append("customer = ?")
        args.append(customer)
    if "yard_card" in cols:
        sets.append("yard_card = ?")
        args.append(card if card in FLOW else ("khac" if familiarity == "la" else ""))
    if "familiarity" in cols:
        sets.append("familiarity = ?")
        args.append(familiarity)
    if "class_synced" in cols:
        sets.append("class_synced = 0")
    args.append(ticket_id)
    cur = cx.execute(f"UPDATE events SET {', '.join(sets)} WHERE id = ?", args)
    cx.commit()
    changed = cur.rowcount
    cx.close()
    if changed != 1:
        raise ValueError("khong thay phieu")
    save_review(ticket_id, kind or "wrong", guess, plate, note, "resolved")
    return plate


def reread(ticket_id):
    cx = connect(DB_PATH)
    row = cx.execute(
        "SELECT id, plate, pack_dir FROM events WHERE id = ?",
        (ticket_id,),
    ).fetchone()
    cx.close()
    if row is None:
        raise ValueError("khong thay phieu")
    paths = []
    pack = row["pack_dir"] or ""
    for lane in ("F", "R", "S"):
        file = os.path.join(pack, lane + ".jpg")
        if os.path.isfile(file):
            paths.append({"lane": lane, "path": os.path.realpath(file)})
    if not paths:
        save_review(ticket_id, "unread", "", row["plate"] or "", "khong co anh goc F R S", "open")
        raise ValueError("khong co anh goc")
    body = json.dumps({"paths": paths}).encode("utf-8")
    req = urllib.request.Request(OCR_URL, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=25) as res:
            found = json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as ex:
        detail = ex.read().decode("utf-8", "replace")[:180]
        save_review(ticket_id, "unread", "", row["plate"] or "", detail or "bo doc tu choi", "open")
        raise ValueError("bo doc tu choi") from ex
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as ex:
        save_review(ticket_id, "unread", "", row["plate"] or "", "bo doc chua chay", "open")
        raise ValueError("bo doc chua chay") from ex
    plate = normalize_plate(found.get("plate"))
    trailer = normalize_plate(found.get("trailerPlate"))
    try:
        conf = float(found.get("confidence") or 0)
    except (TypeError, ValueError):
        conf = 0.0
    saved = row["plate"] or ""
    note = f"tin {conf:.2f}"
    if not plate or conf < 0.8:
        save_review(ticket_id, "unread", plate, saved, note, "open")
        return {"applied": False, "kind": "unread", "guess": plate, "confidence": conf}
    if saved and saved != plate:
        save_review(ticket_id, "conflict", plate, saved, note, "open")
        return {"applied": False, "kind": "conflict", "guess": plate, "confidence": conf}
    apply_plate(ticket_id, plate, trailer, "unread", plate, note)
    return {"applied": True, "kind": "", "guess": plate, "confidence": conf}


PAGE = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BM-OCR</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  body { margin: 0; font: 16px/1.4 system-ui, sans-serif; background: #14110e; color: #f4efe6; }
  header { display: flex; justify-content: space-between; gap: 12px; align-items: center; padding: 12px 16px; border-bottom: 1px solid #3a3228; }
  h1 { font-size: 22px; margin: 0; letter-spacing: .04em; }
  button, input { font: inherit; border-radius: 10px; border: 1px solid #5c5144; background: #2a241c; color: inherit; min-height: 42px; padding: 8px 12px; }
  button { cursor: pointer; }
  button.ok { background: #1d6b3a; border-color: #1d6b3a; }
  button.bad { background: #8a3418; border-color: #8a3418; }
  main { display: grid; grid-template-columns: 320px 1fr; min-height: calc(100vh - 58px); }
  aside { border-right: 1px solid #3a3228; overflow: auto; }
  .row { display: block; width: 100%; text-align: left; border: 0; border-bottom: 1px solid #2c261f; border-radius: 0; background: transparent; padding: 10px 12px; }
  .row.on { background: #2e2618; }
  .row b { color: #e6c15a; font-size: 18px; }
  .badg { color: #e7a15a; font-size: 12px; }
  .fine { color: #b7aa9a; font-size: 13px; }
  section { padding: 16px; }
  img.shot { width: 100%; max-height: 52vh; object-fit: contain; background: #000; border-radius: 12px; }
  .lanes { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 8px; }
  .lanes img { width: 100%; height: 120px; object-fit: cover; background: #000; border-radius: 8px; }
  .plate { font-size: 56px; margin: 8px 0; letter-spacing: .03em; }
  .ex { background: #3a2414; border: 1px solid #a86a28; border-radius: 12px; padding: 10px 12px; }
  .tools { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
  #plate { font-size: 28px; width: 280px; }
  #msg { min-height: 1.4em; color: #e7a15a; }
  @media (max-width: 800px) { main { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<header>
  <h1>BM-OCR</h1>
  <div class="fine" id="meta"></div>
  <label class="fine"><input id="only" type="checkbox" style="min-height:0"> Chỉ ngoại lệ</label>
</header>
<main>
  <aside id="list"></aside>
  <section id="detail"><p class="fine">Chọn một lượt.</p></section>
</main>
<script>
let rows = [];
let current = "";
function kg(n){ return n == null ? "—" : Number(n).toLocaleString("vi-VN") + " kg"; }
async function load(){
  const res = await fetch("/api/sessions", {cache:"no-store"});
  const data = await res.json();
  rows = data.rows || [];
  const open = rows.filter(r => r.kind).length;
  document.getElementById("meta").textContent = (data.day || "") + " · " + rows.length + " lượt · " + open + " ngoại lệ";
  paintList();
  if (current) paintDetail();
}
function paintList(){
  const only = document.getElementById("only").checked;
  const host = document.getElementById("list");
  host.innerHTML = "";
  rows.filter(r => !only || r.kind).forEach(r => {
    const b = document.createElement("button");
    b.className = "row" + (r.id === current ? " on" : "");
    b.innerHTML = "<div class='fine'>" + r.time + " · " + kg(r.kg) + "</div><b>" + (r.plate || "Chưa có biển") + "</b>" + (r.kindLabel ? "<div class='badg'>" + r.kindLabel + "</div>" : "");
    b.onclick = () => { current = r.id; paintList(); paintDetail(); };
    host.appendChild(b);
  });
}
function img(kind){
  return "/img?id=" + encodeURIComponent(current) + "&kind=" + kind;
}
function paintDetail(){
  const r = rows.find(x => x.id === current);
  const host = document.getElementById("detail");
  if (!r) { host.innerHTML = "<p class='fine'>Chọn một lượt.</p>"; return; }
  host.innerHTML =
    (r.kindLabel ? "<p class='ex'>" + r.kindLabel + (r.note ? " · " + r.note : "") + "</p>" : "") +
    "<div class='fine'>" + r.time + " · " + kg(r.kg) + " · " + (r.flow || "Chưa có luồng") + " · " + (r.visit || "Chưa rõ vào/ra") + "</div>" +
    "<div class='plate'>" + (r.plate || "—") + "</div>" +
    "<div class='fine'>Rơ-moóc " + (r.trailer || "—") + " · " + (r.customer || "Chưa có khách") + (r.guess ? " · Máy đoán " + r.guess : "") + "</div>" +
    (r.hasShot ? "<img class='shot' alt='Ảnh ghép' src='" + img("shot") + "'>" : "<p class='ex'>Không có ảnh ghép trên máy.</p>") +
    "<div class='lanes'><img alt='F' src='" + img("F") + "'><img alt='R' src='" + img("R") + "'><img alt='S' src='" + img("S") + "'></div>" +
    "<div class='tools'><input id='plate' placeholder='Biển đúng' value='" + (r.guess || r.plate || "") + "'><input id='trailer' placeholder='Rơ-moóc' value='" + (r.trailer || "") + "'><button class='ok' id='yes'>Đúng</button><button class='bad' id='fix'>Sai, ghi biển này</button><button id='again'>Đọc lại</button></div>" +
    "<p id='msg'></p>";
  document.getElementById("yes").onclick = () => post("/api/resolve", {id: current, plate: r.plate || r.guess, trailer: r.trailer, kind: "wrong"});
  document.getElementById("fix").onclick = () => post("/api/resolve", {id: current, plate: document.getElementById("plate").value, trailer: document.getElementById("trailer").value, kind: "wrong"});
  document.getElementById("again").onclick = () => post("/api/reread", {id: current});
}
async function post(url, body){
  const msg = document.getElementById("msg");
  msg.textContent = "Đang làm…";
  const res = await fetch(url, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body)});
  const data = await res.json();
  msg.textContent = data.error || (data.applied === false ? "Chưa ghi. Xem ngoại lệ." : "Đã ghi. App cân sẽ gửi lên web.");
  await load();
}
document.getElementById("only").onchange = paintList;
load();
setInterval(load, 4000);
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/api/sessions":
            if not DB_PATH:
                self._json(200, {"day": "", "rows": [], "error": "khong thay so can"})
                return
            day = datetime.now().strftime("%Y-%m-%d")
            try:
                self._json(200, {"day": day, "db": DB_PATH, "rows": day_rows(day)})
            except sqlite3.Error as ex:
                self._json(500, {"error": str(ex)})
            return
        if path == "/img":
            query = self.path.split("?", 1)[1] if "?" in self.path else ""
            got = dict(part.split("=", 1) for part in query.split("&") if "=" in part)
            from urllib.parse import unquote
            ticket = unquote(got.get("id", ""))
            kind = unquote(got.get("kind", ""))
            file = image_path(ticket, kind) if DB_PATH else None
            if not file:
                self._send(404, b"", "text/plain")
                return
            with open(file, "rb") as handle:
                self._send(200, handle.read(), "image/jpeg")
            return
        self._send(404, b"", "text/plain")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "json"})
            return
        ticket = str(body.get("id") or "")
        try:
            if self.path == "/api/resolve":
                plate = apply_plate(ticket, body.get("plate"), body.get("trailer"), body.get("kind"), body.get("guess"), "sua tay")
                self._json(200, {"ok": True, "plate": plate})
                return
            if self.path == "/api/reread":
                self._json(200, reread(ticket))
                return
        except ValueError as ex:
            self._json(400, {"error": str(ex)})
            return
        except sqlite3.Error as ex:
            self._json(500, {"error": str(ex)})
            return
        self._send(404, b"", "text/plain")

    def _json(self, status, obj):
        self._send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _send(self, status, raw, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, fmt, *args):
        return


def main():
    global DB_PATH, REVIEW_PATH
    DB_PATH = pick_db(candidate_dbs())
    if DB_PATH:
        REVIEW_PATH = os.path.join(os.path.dirname(DB_PATH), "bm-ocr.db")
        ensure_review(REVIEW_PATH)
        print("So can:", DB_PATH)
    else:
        print("Chua thay cancomp.db. Mo BM Auto Can tren may nay roi bam lai.")
    try:
        server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:
        print("BM-OCR dang mo san: http://127.0.0.1:%d/" % PORT)
        return 0
    print("BM-OCR: http://127.0.0.1:%d/" % PORT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
