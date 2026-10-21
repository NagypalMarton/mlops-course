"""Check and prepare files required by the CI Makefile targets."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def ensure_env() -> int:
    env_file = Path(".env")
    if not env_file.is_file():
        shutil.copyfile(".env.example", env_file)
        print("No .env found: copied .env.example.")
    return 0


def ensure_data() -> int:
    data_file = Path("data/measurements.csv")
    if not data_file.is_file():
        print("data/measurements.csv is missing. Build it from the committed batches:")
        print("    make data-v2")
        return 1
    return 0


def main() -> int:
    checks = {"env": ensure_env, "data": ensure_data}
    if len(sys.argv) != 2 or sys.argv[1] not in checks:
        options = ", ".join(checks)
        raise SystemExit(f"Usage: check_prerequisite.py <{options}>")
    return checks[sys.argv[1]]()


if __name__ == "__main__":
    raise SystemExit(main())
