#!/usr/bin/env python3
"""Validate and normalize a JSON date-by-symbol panel."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path


def normalize(rows, required_features):
    output = []
    seen = set()
    for row in rows:
        key = (row.get("date"), row.get("symbol"))
        if not row.get("date") or not row.get("symbol") or key in seen:
            continue
        if any(row.get(feature) is None or not math.isfinite(float(row[feature])) for feature in required_features):
            continue
        weight = row.get("weight", 1.0)
        if weight is None or not math.isfinite(float(weight)) or float(weight) < 0:
            continue
        item = dict(row)
        item["weight"] = float(weight)
        output.append(item)
        seen.add(key)
    return sorted(output, key=lambda row: (row["date"], row["symbol"]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--feature", action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    rows = json.loads(args.input.read_text(encoding="utf-8"))
    args.out.write_text(json.dumps(normalize(rows, args.feature), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
