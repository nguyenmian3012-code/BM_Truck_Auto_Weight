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
n = cx.execute(
    """
    UPDATE events
    SET shot_synced=0
    WHERE source='kingbird'
      AND IFNULL(shot_path, '') != ''
      AND (IFNULL(ts, '') LIKE ? OR IFNULL(created_at, '') LIKE ?)
    """,
    (day + "%", day + "%"),
).rowcount
cx.commit()
print("Da mo lai", n, "anh ngay", day)
