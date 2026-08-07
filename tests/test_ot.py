import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import compute_1d_ot as ot


class TransportTests(unittest.TestCase):
    def test_exact_wasserstein_one(self):
        self.assertAlmostEqual(ot.wasserstein_1([(0, 1)], [(2, 1)]), 2.0)

    def test_weighted_duplicate_support(self):
        value = ot.wasserstein_1([(0, 1), (0, 1)], [(1, 1)])
        self.assertAlmostEqual(value, 1.0)

    def test_midpoint_transport_target(self):
        current = [(2, 1)]
        reference = [(0, 1), (4, 1)]
        q = ot.weighted_midpoint_quantile(current, 2)
        self.assertAlmostEqual(ot.weighted_quantile(reference, q), 0.0)

    def test_invalid_and_zero_weights_are_excluded(self):
        self.assertEqual(ot._clean_pairs([{"x": 1, "weight": 0}, {"x": 2, "weight": 1}], "x"), [(2.0, 1.0)])

    def test_point_in_time_and_insufficient_history(self):
        rows = [
            {"date": "2024-01-01", "symbol": "A", "industry": "I", "feature_a": 1},
            {"date": "2024-01-01", "symbol": "B", "industry": "I", "feature_a": 2},
            {"date": "2024-01-02", "symbol": "A", "industry": "I", "feature_a": 3},
            {"date": "2024-01-02", "symbol": "B", "industry": "I", "feature_a": 4},
        ]
        values, diagnostics = ot.compute(rows, ["feature_a"], reference_window=10, min_reference_dates=1, group_key="industry")
        later = [row for row in values if row["date"] == "2024-01-02"]
        self.assertTrue(all(row["reference_end"] == "2024-01-01" for row in later))
        self.assertEqual(diagnostics[-1]["reference_end"], "2024-01-01")

    def test_industry_view_does_not_mix_groups(self):
        rows = [
            {"date": "2024-01-01", "symbol": "A", "industry": "I1", "feature_a": 1},
            {"date": "2024-01-01", "symbol": "B", "industry": "I1", "feature_a": 2},
            {"date": "2024-01-01", "symbol": "C", "industry": "I2", "feature_a": 100},
            {"date": "2024-01-01", "symbol": "D", "industry": "I2", "feature_a": 101},
            {"date": "2024-01-02", "symbol": "A", "industry": "I1", "feature_a": 2},
            {"date": "2024-01-02", "symbol": "B", "industry": "I1", "feature_a": 3},
            {"date": "2024-01-02", "symbol": "C", "industry": "I2", "feature_a": 101},
            {"date": "2024-01-02", "symbol": "D", "industry": "I2", "feature_a": 102},
        ]
        values, diagnostics = ot.compute(rows, ["feature_a"], min_reference_dates=1, group_key="industry")
        current = [row for row in values if row["date"] == "2024-01-02"]
        self.assertEqual({row["group"] for row in current}, {"I1", "I2"})
        self.assertTrue(all(row["transport_pressure"] is not None for row in current))

    def test_constant_reference_fails_closed(self):
        rows = [
            {"date": "2024-01-01", "symbol": "A", "feature_a": 1},
            {"date": "2024-01-01", "symbol": "B", "feature_a": 1},
            {"date": "2024-01-02", "symbol": "A", "feature_a": 1},
            {"date": "2024-01-02", "symbol": "B", "feature_a": 2},
        ]
        values, _ = ot.compute(rows, ["feature_a"], min_reference_dates=1, view="global_cross_section")
        later = [row for row in values if row["date"] == "2024-01-02"]
        self.assertTrue(all(row["transport_pressure"] is None for row in later))


if __name__ == "__main__":
    unittest.main()
