"""Ghép phiếu thành phiên. Cùng luật với worker/sessions.js. Không ghi database."""

import re
from datetime import datetime, timedelta

WINDOW_MS = 20 * 60 * 60 * 1000
REWEIGH_KG = 200
CARGO_MIN = 500


def round_step_20(kg):
    n = float(kg)
    q = n / 20
    lower = int(q)
    if q < lower:
        lower -= 1
    frac = q - lower
    return (lower + 1 if frac > 0.5 else lower) * 20


def ms_of(ts):
    s = str(ts or "").strip().replace("Z", "+00:00")
    m = re.match(
        r"(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})(?:\.\d+)?(?:([+-])(\d{2}):?(\d{2}))?",
        s,
    )
    if not m:
        return 0
    wall = datetime.strptime(m.group(1) + " " + m.group(2), "%Y-%m-%d %H:%M:%S")
    off = 0
    if m.group(3):
        off = int(m.group(4)) * 60 + int(m.group(5))
        if m.group(3) == "-":
            off = -off
    utc = wall - timedelta(minutes=off)
    return int((utc - datetime(1970, 1, 1)).total_seconds() * 1000)


def vn_day(ts):
    n = ms_of(ts)
    if not n:
        return str(ts or "")[:10]
    return (datetime(1970, 1, 1) + timedelta(milliseconds=n, hours=7)).strftime("%Y-%m-%d")


def num(v):
    try:
        n = float(v)
    except (TypeError, ValueError):
        return None
    if n != n:
        return None
    return n


def blank_session(row, note):
    return {
        "id": "x:" + str(row.get("id") or ""),
        "plate": "",
        "trailer_plate": "",
        "customer": row.get("customer") or "",
        "card": "",
        "status": "exception",
        "first_ticket_id": row.get("id"),
        "last_ticket_id": row.get("id"),
        "kg_in": num(row.get("kg")),
        "kg_out": None,
        "net_kg": None,
        "net_kg_rounded": None,
        "starch_pct": num(row.get("starch_pct")),
        "opened_at": row.get("ts") or "",
        "closed_at": None,
        "overnight": 0,
        "note": note,
    }


def finish(open_):
    has_out = bool(open_.get("out"))
    kg_in = open_["kgIn"]
    kg_out = open_["kgOut"] if has_out else None
    notes = []
    if open_.get("reweigh"):
        notes.append("cân lại, lấy lần cuối")
    trailer_in = str(open_.get("trailer") or "")
    trailer_out = str(open_.get("outTrailer") or "")
    if trailer_in and trailer_out and trailer_in != trailer_out:
        notes.append("remooc lệch")
    card = ""
    net = None
    status = "open"
    if has_out:
        diff = kg_in - kg_out
        net = abs(diff)
        if diff > CARGO_MIN:
            card = "nhap_mi"
        elif -diff > CARGO_MIN:
            card = "xuat_bot"
        else:
            card = "khac"
        status = "exception" if "remooc lệch" in notes else "closed"
    elif open_.get("reason") == "đang mở":
        status = "open"
        notes.append("đang mở")
    else:
        status = "exception"
        notes.append(open_.get("reason") or "chưa đủ lượt")
    overnight = 1 if has_out and vn_day(open_["in"].get("ts")) != vn_day(open_["out"].get("ts")) else 0
    out = open_.get("out") or {}
    starch = num(open_.get("starch"))
    if starch is None:
        starch = num(out.get("starch_pct"))
    return {
        "id": "s:" + str(open_["inId"]),
        "plate": open_["plate"],
        "trailer_plate": trailer_in or trailer_out,
        "customer": open_.get("customer") or out.get("customer") or "",
        "card": card,
        "status": status,
        "first_ticket_id": open_["inId"],
        "last_ticket_id": open_["lastId"],
        "kg_in": kg_in,
        "kg_out": kg_out,
        "net_kg": net,
        "net_kg_rounded": None if net is None else round_step_20(net),
        "starch_pct": starch,
        "opened_at": open_["in"].get("ts") or "",
        "closed_at": (out.get("ts") or "") if has_out else None,
        "overnight": overnight,
        "note": ". ".join(n for n in notes if n),
    }


def pair_tickets(rows, now_ms=None):
    now = now_ms if now_ms is not None else int(datetime.now().timestamp() * 1000)
    sessions = []
    by_plate = {}
    for row in rows or []:
        kg = num(row.get("kg"))
        if kg is None:
            continue
        plate = str(row.get("plate") or "").strip().upper()
        if not plate:
            sessions.append(blank_session(row, "thiếu biển"))
            continue
        item = dict(row)
        item["plate"] = plate
        item["kg"] = kg
        item["t"] = ms_of(row.get("ts"))
        by_plate.setdefault(plate, []).append(item)
    for plate, lst in by_plate.items():
        lst.sort(key=lambda r: (r["t"], str(r.get("id"))))
        open_ = None

        def push_open():
            nonlocal open_
            if not open_:
                return
            sessions.append(finish(open_))
            open_ = None

        for row in lst:
            if open_ and row["t"] - open_["lastT"] <= WINDOW_MS and abs(row["kg"] - open_["lastKg"]) < REWEIGH_KG:
                open_["lastKg"] = row["kg"]
                open_["lastId"] = row.get("id")
                open_["lastT"] = row["t"]
                open_["reweigh"] = 1
                if open_.get("out"):
                    open_["kgOut"] = row["kg"]
                    open_["out"] = row
                    open_["outTrailer"] = row.get("trailer_plate") or open_.get("outTrailer")
                else:
                    open_["kgIn"] = row["kg"]
                if row.get("customer"):
                    open_["customer"] = row.get("customer")
                if row.get("starch_pct") is not None:
                    open_["starch"] = row.get("starch_pct")
                continue
            if open_ and not open_.get("out") and row["t"] - open_["openedT"] <= WINDOW_MS:
                open_["out"] = row
                open_["kgOut"] = row["kg"]
                open_["lastKg"] = row["kg"]
                open_["lastId"] = row.get("id")
                open_["lastT"] = row["t"]
                open_["outTrailer"] = row.get("trailer_plate") or ""
                if row.get("customer") and not open_.get("customer"):
                    open_["customer"] = row.get("customer")
                if row.get("starch_pct") is not None:
                    open_["starch"] = row.get("starch_pct")
                continue
            if open_ and not open_.get("out"):
                open_["reason"] = "quá 20 giờ, chưa có lượt kia"
            push_open()
            open_ = {
                "plate": plate,
                "in": row,
                "inId": row.get("id"),
                "kgIn": row["kg"],
                "openedT": row["t"],
                "lastT": row["t"],
                "lastKg": row["kg"],
                "lastId": row.get("id"),
                "trailer": row.get("trailer_plate") or "",
                "outTrailer": "",
                "customer": row.get("customer") or "",
                "starch": row.get("starch_pct"),
                "reweigh": 0,
                "out": None,
                "kgOut": None,
                "reason": "",
            }
        if open_ and not open_.get("out"):
            open_["reason"] = "đang mở" if now - open_["openedT"] <= WINDOW_MS else "quá 20 giờ, chưa có lượt kia"
        push_open()
    return sessions
