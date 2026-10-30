import unittest

import bay


def run(script):
    state = bay.fresh()
    seen = []
    for hold, sample in script:
        ticks = int(round(hold / 0.2))
        for _ in range(ticks):
            bay.step(state, sample, 0.2)
            seen.append((state["mode"], dict(bay.lights_of(state)), bay.screen(state)["seconds"]))
    return state, seen


class Bay(unittest.TestCase):
    def test_full_truck(self):
        state, seen = run([
            (0.4, {"kg": 0}),
            (1.0, {"kg": 900}),
            (1.0, {"kg": 8000}),
            (1.0, {"kg": 18000}),
            (0.4, {"kg": 18600}),
            (4.2, {"kg": 18600}),
            (0.4, {"kg": 18600, "ocr": "ok", "plate": "70H-186.41", "customer": "Thu", "card": "nhap_mi", "visit": "vao"}),
            (1.4, {"kg": 18600}),
            (0.4, {"kg": 12000}),
            (3.2, {"kg": 12000}),
            (0.4, {"kg": 0}),
        ])
        modes = [row[0] for row in seen]
        self.assertIn("enter", modes)
        self.assertIn("count", modes)
        self.assertIn("go", modes)
        self.assertIn("leave", modes)
        self.assertEqual(state["mode"], "wait")
        self.assertEqual(state["plate"], "")
        self.assertEqual(bay.lights_of(state)["yellow"], False)
        enter = next(row for row in seen if row[0] == "enter")
        self.assertEqual(enter[1], {"red": False, "yellow": True, "green": False, "horn": False})
        count = next(row for row in seen if row[0] == "count")
        self.assertTrue(count[1]["red"])
        self.assertGreater(count[2], 0)
        go = [row for row in seen if row[0] == "go"]
        self.assertTrue(go[0][1]["horn"])
        self.assertTrue(go[0][1]["green"])
        self.assertFalse(go[-1][1]["horn"])
        leave = [row for row in seen if row[0] == "leave"]
        self.assertTrue(leave[0][1]["yellow"])
        self.assertFalse(leave[0][1]["green"])
        self.assertFalse(leave[-1][1]["yellow"])

    def test_unread_becomes_exception_then_go(self):
        state, seen = run([
            (0.4, {"kg": 20000}),
            (0.4, {"kg": 20000}),
            (4.2, {"kg": 20000, "ocr": "pending"}),
            (8.2, {"kg": 20000, "ocr": "pending"}),
            (0.4, {"kg": 20000, "ocr": "ok", "plate": "70C-117.68", "card": "xuat_bot", "visit": "ra"}),
        ])
        self.assertIn("exception", [row[0] for row in seen])
        self.assertEqual(state["mode"], "go")
        view = bay.screen(state)
        self.assertEqual(view["flow"], "Xuất bột")
        self.assertEqual(view["visit"], "Ra")
        self.assertEqual(view["plate"], "70C-117.68")

    def test_creep_restarts_the_count(self):
        state = bay.fresh()
        bay.step(state, {"kg": 15000}, 0.2)
        bay.step(state, {"kg": 18000}, 0.2)
        bay.step(state, {"kg": 18000}, 0.2)
        self.assertEqual(state["mode"], "count")
        bay.step(state, {"kg": 18000}, 1.0)
        self.assertLess(state["count"], 4)
        bay.step(state, {"kg": 19000}, 0.2)
        self.assertEqual(state["mode"], "enter")


if __name__ == "__main__":
    unittest.main()
