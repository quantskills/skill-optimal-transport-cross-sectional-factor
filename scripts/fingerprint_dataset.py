#!/usr/bin/env python3
"""Fingerprint normalized panel content without including absolute paths."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("input", type=Path)
args = parser.parse_args()
rows = json.loads(args.input.read_text(encoding="utf-8"))
payload = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
print(json.dumps({"algorithm": "sha256", "row_count": len(rows), "fingerprint": hashlib.sha256(payload).hexdigest()}))
