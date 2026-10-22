#!/usr/bin/env python3
"""Repository wrapper for standalone reading CLI."""
import runpy
from pathlib import Path
if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).resolve().parents[1]/'skills/tis-reading/scripts/reading.py'),run_name='__main__')
