import os
import sqlite3
import tempfile
import unittest

import bm_ocr


def row(**kw):
    base = {
        "plate": "",
        "ocr_status": "",
        "shot_path": "",
    }
    base.update(kw)
    return base


class Rules(unittest.TestCase):
    def test_plate(self):
        self.assertEqual(bm_ocr.normalize_plate("70h186.41"), "70H-186.41")
        self.assertEqual(bm_ocr.normalize_plate("xe 70RH-020.24."), "70RH-020.24")
        self.assertEqual(bm_ocr.normalize_plate("abc"), "")

    def test_missing_shot_wins(self):
        path = os.path.join(tempfile.gettempdir(), "khong-co-anh-nay.jpg")
        item = row(plate="70H-186.41", ocr_status="ok", shot_path=path)
        self.assertEqual(bm_ocr.auto_kind(item), "missing-shot")

    def test_unread_and_bad(self):
        real = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        real.close()
        self.addCleanup(os.remove, real.name)
        self.assertEqual(bm_ocr.auto_kind(row(shot_path=real.name, ocr_status="pending")), "unread")
        self.assertEqual(bm_ocr.auto_kind(row(shot_path=real.name, plate="ABC", ocr_status="ok")), "bad-plate")
        self.assertEqual(bm_ocr.auto_kind(row(shot_path=real.name, plate="70C-117.68", ocr_status="ok")), "")

    def test_resolved_stays_closed_until_plate_changes(self):
        real = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        real.close()
        self.addCleanup(os.remove, real.name)
        item = row(shot_path=real.name, plate="70H-050.99", ocr_status="ok")
        review = {"state": "resolved", "corrected": "70H-050.99", "kind": "wrong"}
        self.assertEqual(bm_ocr.exception_kind(item, review), "")
        item["plate"] = ""
        item["ocr_status"] = "pending"
        self.assertEqual(bm_ocr.exception_kind(item, review), "unread")

    def test_apply_writes_queue(self):
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.addCleanup(os.remove, path)
        cx = sqlite3.connect(path)
        cx.execute(
            """
            CREATE TABLE events (
              id TEXT PRIMARY KEY, plate TEXT, trailer_plate TEXT, customer TEXT,
              yard_card TEXT, familiarity TEXT, ocr_status TEXT, class_synced INTEGER
            )
            """
        )
        cx.execute("CREATE TABLE routes (plate TEXT PRIMARY KEY, customer TEXT, yard_card TEXT, note TEXT)")
        cx.execute("INSERT INTO events(id, ocr_status, class_synced) VALUES('t1','pending',1)")
        cx.execute("INSERT INTO routes(plate, customer, yard_card, note) VALUES('70H-186.41','Thu','nhap_mi','')")
        cx.commit()
        cx.close()
        review = path + ".review"
        self.addCleanup(lambda: os.path.exists(review) and os.remove(review))
        bm_ocr.DB_PATH = path
        bm_ocr.REVIEW_PATH = review
        bm_ocr.ensure_review(review)
        self.addCleanup(setattr, bm_ocr, "DB_PATH", "")
        self.addCleanup(setattr, bm_ocr, "REVIEW_PATH", "")
        plate = bm_ocr.apply_plate("t1", "70H186.41", "70RH-020.24", "wrong", "70H-186.40", "test")
        self.assertEqual(plate, "70H-186.41")
        cx = sqlite3.connect(path)
        got = cx.execute("SELECT plate, trailer_plate, customer, yard_card, class_synced, ocr_status FROM events").fetchone()
        cx.close()
        self.assertEqual(got, ("70H-186.41", "70RH-020.24", "Thu", "nhap_mi", 0, "ok"))


if __name__ == "__main__":
    unittest.main()
