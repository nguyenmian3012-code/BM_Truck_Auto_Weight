import os
import sqlite3
import threading
import time
import urllib.request
from datetime import datetime, timezone

from pair import calc_text, flag_light_outlier, pair_tickets, round_step_20
from server import PORT

now = int(datetime(2026, 11, 26, 8, 0, tzinfo=timezone.utc).timestamp() * 1000)
rows = [
    {"id": "a", "plate": "70H-072.04", "kg": 52040, "ts": "2026-11-25T06:00:00+07:00"},
    {"id": "b", "plate": "70H-072.04", "kg": 52080, "ts": "2026-11-25T06:02:00+07:00"},
    {"id": "c", "plate": "70H-072.04", "kg": 18110, "ts": "2026-11-25T09:00:00+07:00"},
]
got = pair_tickets(rows, now)
assert len(got) == 1, got
assert got[0]["status"] == "closed"
assert got[0]["card"] == "nhap_mi"
assert got[0]["kg_in"] == 52080
assert "cân lại" in got[0]["note"]
assert round_step_20(33970) == 33960
assert "nhập mì" in calc_text(got[0])
odd = flag_light_outlier(
    {"kg_in": 50000, "kg_out": 12000, "status": "closed", "note": "", "plate": "70H"},
    [18000, 18200, 17900, 18100],
)
assert odd["status"] == "exception"

db = os.path.join(os.path.dirname(__file__), "fixture.db")
if os.path.exists(db):
    os.remove(db)
cx = sqlite3.connect(db)
cx.execute(
    """CREATE TABLE events (
      id TEXT PRIMARY KEY, source TEXT, kg REAL, starch_pct REAL, ts TEXT,
      plate TEXT, trailer_plate TEXT, customer TEXT, ocr_status TEXT, ocr_reason TEXT,
      vehicle_type TEXT, direction TEXT, yard_card TEXT)"""
)
stamp = (datetime.now(timezone.utc) + __import__("datetime").timedelta(hours=7)).strftime("%Y-%m-%dT%H:%M:%S+07:00")
day = stamp[:10]
cx.execute(
    "INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
    ("a", "kingbird", 52000, None, stamp, "70C-077.40", "", "A", "ok", "", "", "vao", "nhap_mi"),
)
cx.commit()
cx.close()

os.environ["CANXE_DB"] = db
os.environ["CANXE_PORT"] = "8781"

import server

server.PORT = 8781


def serve():
    try:
        server.ThreadingHTTPServer(("127.0.0.1", 8781), server.Handler).serve_forever()
    except Exception as e:
        print("server failed", e)


threading.Thread(target=serve, daemon=True).start()
time.sleep(0.4)
html = urllib.request.urlopen("http://127.0.0.1:8781/?ngay=" + day, timeout=5).read().decode()
assert "70C-077.40" in html
assert "Xe nhập mì" in html
phieu = urllib.request.urlopen("http://127.0.0.1:8781/phieu?ngay=" + day, timeout=5).read().decode()
assert "OCR Result" in phieu
print("localweb selftest ok")
