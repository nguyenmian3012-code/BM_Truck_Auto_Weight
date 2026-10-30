import datetime
import os
import sqlite3
import sys


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
        return [row[1] for row in cx.execute("PRAGMA table_info(events)").fetchall()]
    except sqlite3.Error:
        return []


def pick(paths):
    best = None
    notes = []
    for path in paths:
        try:
            cx = sqlite3.connect(path, timeout=20)
        except sqlite3.Error as ex:
            notes.append(path + " | khong mo duoc: " + str(ex))
            continue
        cols = columns(cx)
        if "shot_path" not in cols:
            notes.append(path + " | khong co cot anh: " + ", ".join(cols))
            cx.close()
            continue
        count = cx.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        latest = cx.execute("SELECT MAX(ts) FROM events").fetchone()[0] or ""
        notes.append(path + " | " + str(count) + " phieu | " + str(latest))
        rank = (count, latest)
        if best is None or rank > best[0]:
            if best:
                best[1].close()
            best = (rank, cx, path)
        else:
            cx.close()
    return best, notes


def main():
    paths = candidates()
    if not paths:
        print("Khong thay so phieu tren may nay.")
        return 1
    chosen, notes = pick(paths)
    for line in notes:
        print(line)
    if not chosen:
        print("Khong co so nao co cot anh. Khong cai lai Python.")
        return 1
    _, cx, path = chosen
    day = datetime.date.today().isoformat()
    rows = cx.execute(
        """
        SELECT id, shot_path FROM events
        WHERE source='kingbird'
          AND IFNULL(shot_path, '') != ''
          AND (IFNULL(ts, '') LIKE ? OR IFNULL(created_at, '') LIKE ?)
        """,
        (day + "%", day + "%"),
    ).fetchall()
    n = 0
    for ticket_id, shot_path in rows:
        cut = shot_path.find(" (")
        file = (shot_path[:cut] if cut >= 0 else shot_path).strip()
        if file and os.path.isfile(file):
            cx.execute("UPDATE events SET shot_synced=0 WHERE id=?", (ticket_id,))
            n += 1
    cx.commit()
    cx.close()
    print("Dung so:", path)
    print("Da mo lai", n, "anh ngay", day)
    return 0


if __name__ == "__main__":
    sys.exit(main())
