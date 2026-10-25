"""
run_ellura.py — launcher for the flat repo layout.

Flat layout (2026-10-24, GitHub push copy):
    FOUNDATION.md, ellura.py at the repo root
    core/, bridge/, sandbox/ as real packages at the repo root

ellura.py imports them as top-level packages
(`from core...`, `from bridge...`). Running this file from the repo
root puts the root on sys.path, so those imports resolve directly —
no FIRSTBREATH/ELLURA shim is needed, and none is used here.

Usage:  python3 run_ellura.py [--sovereign | --self-test | ...]
It forwards all arguments to ellura.py's CLI.
"""

import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

if HERE not in sys.path:
    sys.path.insert(0, HERE)

if __name__ == "__main__":
    sys.argv = [os.path.join(HERE, "ellura.py")] + sys.argv[1:]
    runpy.run_path(os.path.join(HERE, "ellura.py"), run_name="__main__")