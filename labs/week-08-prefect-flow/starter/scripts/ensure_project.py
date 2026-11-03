"""Prepare files required by local Make targets."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"env", "data"}:
        raise SystemExit("usage: ensure_project.py env|data")

    if sys.argv[1] == "env":
        env = Path(".env")
        if not env.exists():
            shutil.copyfile(".env.example", env)
            print("no .env found -> copied .env.example (defaults; no secrets in this lab)")
        return 0

    if Path("data/measurements.csv").exists():
        return 0
    print("data/measurements.csv is missing -- it is DVC-tracked, so a fresh")
    print("clone does not have it. Rebuild it from the committed raw batches:")
    print("    make data-v2")
    print("(CI does exactly this, which is why it needs no object store.)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
