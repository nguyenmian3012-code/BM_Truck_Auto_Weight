"""Ghi đúng ô cho lượt 13:17. App đang mở sẽ tự gửi lên web."""

import os
import sqlite3
import sys

TICKET = "589c674b19174e308c397cd7905fc1ee"
PLATE = "70H-082.61"
TRAILER = "70RM-012.71"


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


def has_ticket(path):
    try:
        cx = sqlite3.connect(path, timeout=20)
    except sqlite3.Error:
        return False
    try:
        row = cx.execute("SELECT id FROM events WHERE id=?", (TICKET,)).fetchone()
    except sqlite3.Error:
        row = None
    cx.close()
    return row is not None


def main():
    paths = [path for path in candidates() if has_ticket(path)]
    if not paths:
        print("Khong thay phieu 13:17 trong so may nay.")
        print("File nay chay tren may can, noi BM Auto Can dang mo.")
        return 1
    path = paths[0]
    cx = sqlite3.connect(path, timeout=20)
    cx.execute(
        """
        CREATE TABLE IF NOT EXISTS yard (
          plate TEXT PRIMARY KEY,
          customer TEXT,
          yard_card TEXT,
          yard_note TEXT,
          familiarity TEXT,
          kg REAL,
          ts TEXT,
          ticket_id TEXT
        )
        """
    )
    cur = cx.execute(
        """
        UPDATE events SET
          plate=?,
          trailer_plate=?,
          customer='',
          yard_card='khac',
          yard_note='',
          familiarity='la',
          visit='vao',
          ocr_status='ok',
          class_synced=0
        WHERE id=? AND IFNULL(plate, '')=''
        """,
        (PLATE, TRAILER, TICKET),
    )
    if cur.rowcount != 1:
        got = cx.execute(
            "SELECT plate, trailer_plate, visit, yard_card, ocr_status FROM events WHERE id=?",
            (TICKET,),
        ).fetchone()
        cx.close()
        print("Khong ghi de. Phieu hien la:", got)
        return 0
    row = cx.execute("SELECT kg, ts FROM events WHERE id=?", (TICKET,)).fetchone()
    cx.execute(
        """
        INSERT INTO yard(plate, customer, yard_card, yard_note, familiarity, kg, ts, ticket_id)
        VALUES(?, '', 'khac', '', 'la', ?, ?, ?)
        ON CONFLICT(plate) DO UPDATE SET
          customer='', yard_card='khac', yard_note='', familiarity='la',
          kg=excluded.kg, ts=excluded.ts, ticket_id=excluded.ticket_id
        """,
        (PLATE, row[0], row[1], TICKET),
    )
    cx.commit()
    cx.close()
    print("Da ghi", PLATE, "remooc", TRAILER, "the Khac, luot vao.")
    print("So:", path)
    print("De app mo. Vai giay nua web o the Khac.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
