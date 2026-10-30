import datetime
import os
import sqlite3
import sys

path = os.environ.get("BM_DB", "")
if not path or not os.path.isfile(path):
    print("Khong thay so phieu")
    sys.exit(1)
day = datetime.date.today().isoformat()
cx = sqlite3.connect(path, timeout=20)
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
print("Da mo lai", n, "anh ngay", day)
