import unittest

from flow import apply_stats, decide, empty_day, empty_profile


class FlowTest(unittest.TestCase):
    def test_heavy_arrival_is_cassava(self):
        got = decide(98890, "70H-082.61", None, "", "", False)
        self.assertEqual(got["visit"], "vao")
        self.assertEqual(got["card"], "nhap_mi")
        self.assertEqual(got["cargo"], "Củ mì")
        self.assertEqual(got["direction"], "Vào")
        self.assertEqual(got["confidence"], "medium")

    def test_light_exit_closes_cassava(self):
        got = decide(22000, "70H-082.61", True, "", "", False)
        self.assertEqual(got["visit"], "ra")
        self.assertEqual(got["card"], "nhap_mi")

    def test_light_arrival_is_not_starch_yet(self):
        got = decide(18000, "51C-111.11", None, "", "", False)
        self.assertEqual(got["visit"], "vao")
        self.assertEqual(got["card"], "khac")

    def test_heavy_exit_after_empty_is_starch(self):
        got = decide(56000, "51C-111.11", False, "", "", False)
        self.assertEqual(got["visit"], "ra")
        self.assertEqual(got["card"], "xuat_bot")

    def test_over_100_tons_stays_open(self):
        got = decide(86000, "50H-222.22", True, "", "", False)
        self.assertEqual(got["visit"], "lai")
        self.assertEqual(got["card"], "nhap_mi")

    def test_split_then_empty_closes(self):
        got = decide(18000, "50H-222.22", True, "", "", False)
        self.assertEqual(got["visit"], "ra")

    def test_export_overload_is_reweigh(self):
        got = decide(110000, "51C-111.11", False, "", "", False)
        self.assertEqual(got["visit"], "lai")
        self.assertEqual(got["card"], "xuat_bot")

    def test_legal_export_exit(self):
        got = decide(54000, "51C-111.11", False, "", "", False)
        self.assertEqual(got["visit"], "ra")
        self.assertEqual(got["card"], "xuat_bot")

    def test_route_wins(self):
        got = decide(18000, "60A-333.33", None, "xuat_bot", "", False)
        self.assertEqual(got["card"], "xuat_bot")
        self.assertEqual(got["familiarity"], "quen")
        self.assertEqual(got["confidence"], "high")

    def test_small_vehicle_round_trip(self):
        got = decide(9000, "65C-444.44", False, "", "", False)
        self.assertEqual(got["visit"], "ra")
        self.assertEqual(got["card"], "khac")

    def test_no_plate_does_not_open_a_session(self):
        got = decide(50000, "", None, "", "", False)
        self.assertEqual(got["visit"], "")
        self.assertEqual(got["card"], "")
        self.assertEqual(got["cargo"], "Có hàng")
        self.assertEqual(got["confidence"], "low")

    def test_two_sessions_count(self):
        profile, day = empty_profile(), empty_day()
        first = decide(50000, "70H-082.61", None, "", "", False)
        profile, day = apply_stats(profile, day, first, 50000)
        second = decide(20000, "70H-082.61", profile["open_loaded"], "", profile["flow"], False)
        profile, day = apply_stats(profile, day, second, 20000)
        third = decide(48000, "70H-082.61", profile["open_loaded"], "", profile["flow"], profile["n_vao"] + profile["n_ra"] >= 2)
        profile, day = apply_stats(profile, day, third, 48000)
        self.assertEqual(day["n_vao"], 2)
        self.assertEqual(profile["n_ra"], 1)
        self.assertEqual(profile["flow"], "nhap_mi")
        self.assertEqual(third["familiarity"], "quen")


if __name__ == "__main__":
    unittest.main()
