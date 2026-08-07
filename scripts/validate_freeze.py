#!/usr/bin/env python3
"""Fail closed when the frozen research configuration is incomplete."""
from __future__ import annotations
import argparse, json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("config", type=Path)
args = parser.parse_args()
config = json.loads(args.config.read_text(encoding="utf-8"))
required = ["features", "reference_window", "min_reference_dates", "view"]
missing = [key for key in required if key not in config]
if missing:
    raise SystemExit("freeze blocked: missing " + ", ".join(missing))
if config["reference_window"] < config["min_reference_dates"]:
    raise SystemExit("freeze blocked: reference_window must cover min_reference_dates")
if config["view"] == "industry_neutral" and not config.get("group_column"):
    raise SystemExit("freeze blocked: industry_neutral requires group_column")
print(json.dumps({"freeze_status": "pass", "algorithm_version": "ot1d-weighted-empirical-v2"}))
