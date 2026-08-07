#!/usr/bin/env python3
"""Report direct panda_data availability without handling credentials."""
from __future__ import annotations
import importlib.util
import json

print(json.dumps({"panda_data_importable": importlib.util.find_spec("panda_data") is not None, "credentials_handled": False, "mcp_required": False}, indent=2))
