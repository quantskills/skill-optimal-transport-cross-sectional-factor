import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import normalize_panel


class PanelTests(unittest.TestCase):
    def test_normalize_deduplicates_and_excludes_bad_rows(self):
        rows = [
            {"date": "2024-01-01", "symbol": "A", "feature_a": 1},
            {"date": "2024-01-01", "symbol": "A", "feature_a": 2},
            {"date": "2024-01-01", "symbol": "B", "feature_a": None},
            {"date": "2024-01-01", "symbol": "C", "feature_a": 3, "weight": 0},
        ]
        result = normalize_panel.normalize(rows, ["feature_a"])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["symbol"], "A")
        self.assertEqual(result[0]["weight"], 1.0)


if __name__ == "__main__":
    unittest.main()
