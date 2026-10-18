#!/usr/bin/env python3
"""Repository launcher for the independently installed business tool."""
import runpy
from pathlib import Path
if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[1]/"skills/tis-client-service/scripts/business.py"),run_name="__main__")
