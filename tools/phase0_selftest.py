#!/usr/bin/env python3
"""Thin alias for `tools/selftest_all.py` (kept so existing docs/links work)."""
import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.argv[0] = str(Path(__file__).resolve().parent / "selftest_all.py")
    runpy.run_path(sys.argv[0], run_name="__main__")
