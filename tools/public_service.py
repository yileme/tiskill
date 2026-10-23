#!/usr/bin/env python3
"""Repository shim; installed skill carries its own runtime."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parents[1]/'skills/tis-public-service-english/scripts/public_service.py'),run_name='__main__')
