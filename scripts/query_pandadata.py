#!/usr/bin/env python3
"""Create a declared, read-only PandaData query manifest; never executes it."""
from __future__ import annotations
import argparse, json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("config", type=Path)
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()
config = json.loads(args.config.read_text(encoding="utf-8"))
args.out.write_text(json.dumps({"execution": "not_run", "transport": "direct_panda_data_if_authorized", "mcp_required": False, "declared_config": config}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
