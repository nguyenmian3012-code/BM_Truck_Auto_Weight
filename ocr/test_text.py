import unittest

import numpy as np

from ocr.lanes import split_lanes
from ocr.text import choose, join_lines, line_groups, normalize_plate


class TextTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_plate("51C-248.19"), "51C-248.19")
        self.assertEqual(normalize_plate("bien 51C24819"), "51C-24819")
        self.assertEqual(normalize_plate("70R-013.71"), "70R-013.71")
        self.assertEqual(normalize_plate("khong"), "")

    def test_two_lines(self):
        self.assertEqual(join_lines(["51C", "248.19"]), "51C-248.19")

    def test_char_rows(self):
        boxes = [
            {"xyxy": (40, 30, 55, 48)},
            {"xyxy": (10, 28, 24, 46)},
            {"xyxy": (12, 60, 28, 78)},
        ]
        rows = line_groups(boxes)
        self.assertEqual(len(rows), 2)
        self.assertLess(rows[0]["items"][0]["xyxy"][0], rows[0]["items"][1]["xyxy"][0])

    def test_conflict_and_agree(self):
        low = choose([{"plate": "51C-248.19", "confidence": 0.5, "lane": "F"}])
        self.assertEqual(low["status"], "unread")
        self.assertEqual(low["plate"], "")
        clash = choose([
            {"plate": "51C-248.19", "confidence": 0.9, "lane": "F"},
            {"plate": "70R-013.71", "confidence": 0.86, "lane": "R"},
        ])
        self.assertEqual(clash["reason"], "conflict")
        same = choose([
            {"plate": "51C-248.19", "confidence": 0.9, "lane": "F"},
            {"plate": "51C-248.19", "confidence": 0.82, "lane": "S"},
        ])
        self.assertEqual(same["status"], "ok")
        self.assertEqual(same["plate"], "51C-248.19")

    def test_split(self):
        img = np.zeros((300, 400, 3), dtype=np.uint8)
        img[:200, :180] = (20, 20, 20)
        img[:200, 180:] = (90, 90, 90)
        img[200:] = (180, 180, 180)
        img[:, 178:182] = 255
        img[198:202, :] = 255
        lanes = split_lanes(img)
        self.assertLess(abs(lanes["F"].shape[1] - 180), 8)
        self.assertLess(abs(lanes["F"].shape[0] - 200), 8)
        self.assertGreater(lanes["R"].shape[1], 200)
        self.assertGreater(lanes["S"].shape[0], 80)


if __name__ == "__main__":
    unittest.main()
