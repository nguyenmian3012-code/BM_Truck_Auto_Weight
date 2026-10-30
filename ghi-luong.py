"""Điền luồng cho phiếu hôm nay. App đang mở sẽ tự gửi lên web."""

import datetime
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "logic"))
from flow import apply_stats, decide, empty_day, empty_profile


def candidates():
    roots = []
    if os.environ.get("BM_DB"):
        roots.append(os.environ["BM_DB"])
    for key in ("PROGRAMDATA", "LOCALAPPDATA"):
        base = os.environ.get(key, "")
        if base:
            roots.append(os.path.join(base, "BmCancomp", "data", "cancomp.db"))
    seen = []
    for path in roots:
        if path and path not in seen and os.path.isfile(path):
            seen.append(path)
    return seen


def columns(cx):
    try:
        return {row[1] for row in cx.execute("PRAGMA table_info(events)").fetchall()}
    except sqlite3.Error:
        return set()


def pick(paths):
    best = None
    for path in paths:
        try:
            cx = sqlite3.connect(path, timeout=20)
        except sqlite3.Error as ex:
            print(path, "khong mo duoc", ex)
            continue
        cols = columns(cx)
        if "yard_card" not in cols or "plate" not in cols:
            print(path, "khong phai so phieu dang dung")
            cx.close()
            continue
        latest = cx.execute("SELECT MAX(ts) FROM events").fetchone()[0] or ""
        if best is None or latest > best[0]:
            if best:
                best[1].close()
            best = (latest, cx, path)
        else:
            cx.close()
    return best


def routes_of(cx):
    try:
        return {row[0]: row[1] or "" for row in cx.execute("SELECT plate, yard_card FROM routes")}
    except sqlite3.Error:
        return {}


def ensure(cx):
    cx.execute(
        """
        CREATE TABLE IF NOT EXISTS plate_stats (
          plate TEXT PRIMARY KEY,
          n_vao INTEGER DEFAULT 0,
          n_ra INTEGER DEFAULT 0,
          n_lai INTEGER DEFAULT 0,
          tare_kg REAL,
          tare_n INTEGER DEFAULT 0,
          gross_kg REAL,
          gross_n INTEGER DEFAULT 0,
          flow TEXT,
          open_loaded INTEGER,
          open_kg REAL,
          open_card TEXT,
          updated_at TEXT
        )
        """
    )
    cx.execute(
        """
        CREATE TABLE IF NOT EXISTS plate_day (
          plate TEXT,
          day TEXT,
          n_vao INTEGER DEFAULT 0,
          n_ra INTEGER DEFAULT 0,
          n_lai INTEGER DEFAULT 0,
          PRIMARY KEY (plate, day)
        )
        """
    )


def same(row, decision, note):
    return (
        (row["direction"] or "") == (decision["direction"] or "")
        and (row["visit"] or "") == decision["visit"]
        and (row["yard_card"] or "") == decision["card"]
        and (row["cargo_guess"] or "") == decision["cargo"]
        and (row["familiarity"] or "") == decision["familiarity"]
        and (row["yard_note"] or "") == note
    )


def main():
    chosen = pick(candidates())
    if not chosen:
        print("Khong thay so phieu. Chay file nay tren may can.")
        return 1
    _, cx, path = chosen
    ensure(cx)
    book = routes_of(cx)
    rows = cx.execute(
        """
        SELECT id, plate, kg, ts, direction, visit, yard_card, cargo_guess, familiarity, yard_note, sync
        FROM events
        WHERE source='kingbird' AND kg IS NOT NULL
        ORDER BY ts ASC, id ASC
        """
    ).fetchall()
    today = datetime.date.today().isoformat()
    profiles = {}
    days = {}
    changed = 0
    for raw in rows:
        row = {
            "id": raw[0],
            "plate": raw[1] or "",
            "kg": raw[2] or 0,
            "ts": raw[3] or "",
            "direction": raw[4] or "",
            "visit": raw[5] or "",
            "yard_card": raw[6] or "",
            "cargo_guess": raw[7] or "",
            "familiarity": raw[8] or "",
            "yard_note": raw[9] or "",
            "sync": raw[10] or "",
        }
        plate = row["plate"]
        day_key = row["ts"][:10]
        if not plate:
            if day_key != today:
                continue
            decision = decide(row["kg"], "", None, "", "", False)
            note = decision["reason"]
            if (row["cargo_guess"], row["yard_note"]) == (decision["cargo"], note):
                continue
            cx.execute(
                "UPDATE events SET cargo_guess=?, yard_note=?, sync='retry' WHERE id=?",
                (decision["cargo"], note, row["id"]),
            )
            changed += 1
            continue
        state = profiles.setdefault(plate, empty_profile())
        day = days.setdefault((plate, day_key), empty_day())
        route = book.get(plate, "")
        familiar = state["n_vao"] + state["n_ra"] >= 2 or bool(route)
        decision = decide(row["kg"], plate, state["open_loaded"], route, state["flow"], familiar)
        state, day = apply_stats(state, day, decision, row["kg"])
        profiles[plate] = state
        days[(plate, day_key)] = day
        if day_key != today:
            continue
        note = decision["reason"]
        if decision["visit"] == "vao" and day["n_vao"] > 1:
            note += ". phiên %d trong ngày" % day["n_vao"]
        if same(row, decision, note):
            continue
        cx.execute(
            """
            UPDATE events SET
              direction=?, visit=?, yard_card=?, cargo_guess=?, familiarity=?, yard_note=?,
              class_synced=0, sync='retry'
            WHERE id=?
            """,
            (
                decision["direction"],
                decision["visit"],
                decision["card"],
                decision["cargo"],
                decision["familiarity"],
                note[:180],
                row["id"],
            ),
        )
        if decision["visit"] == "ra":
            cx.execute("DELETE FROM yard WHERE plate=?", (plate,))
        elif decision["visit"] in ("vao", "lai"):
            cx.execute(
                """
                INSERT INTO yard(plate, customer, yard_card, yard_note, familiarity, kg, ts, ticket_id)
                VALUES(?, '', ?, '', ?, ?, ?, ?)
                ON CONFLICT(plate) DO UPDATE SET
                  yard_card=excluded.yard_card, familiarity=excluded.familiarity,
                  kg=excluded.kg, ts=excluded.ts, ticket_id=excluded.ticket_id
                """,
                (plate, decision["card"], decision["familiarity"], row["kg"], row["ts"], row["id"]),
            )
        changed += 1
    for plate, state in profiles.items():
        flag = None if state["open_loaded"] is None else (1 if state["open_loaded"] else 0)
        cx.execute(
            """
            INSERT INTO plate_stats
              (plate, n_vao, n_ra, n_lai, tare_kg, tare_n, gross_kg, gross_n, flow, open_loaded, open_kg, open_card, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(plate) DO UPDATE SET
              n_vao=excluded.n_vao, n_ra=excluded.n_ra, n_lai=excluded.n_lai,
              tare_kg=excluded.tare_kg, tare_n=excluded.tare_n,
              gross_kg=excluded.gross_kg, gross_n=excluded.gross_n,
              flow=excluded.flow, open_loaded=excluded.open_loaded,
              open_kg=excluded.open_kg, open_card=excluded.open_card, updated_at=excluded.updated_at
            """,
            (
                plate, state["n_vao"], state["n_ra"], state["n_lai"],
                state["tare_kg"], state["tare_n"], state["gross_kg"], state["gross_n"],
                state["flow"], flag, state["open_kg"], state["open_card"],
                datetime.datetime.now().isoformat(timespec="seconds"),
            ),
        )
    for (plate, day_key), day in days.items():
        cx.execute(
            """
            INSERT INTO plate_day(plate, day, n_vao, n_ra, n_lai)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(plate, day) DO UPDATE SET
              n_vao=excluded.n_vao, n_ra=excluded.n_ra, n_lai=excluded.n_lai
            """,
            (plate, day_key, day["n_vao"], day["n_ra"], day["n_lai"]),
        )
    cx.commit()
    print("So:", path)
    print("Da dien", changed, "phieu hom nay.")
    print("Xe co bien se hien dung the. App dang mo se tu gui len web.")
    cx.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
