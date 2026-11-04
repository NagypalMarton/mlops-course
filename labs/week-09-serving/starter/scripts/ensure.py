"""Check or create the local files required by Make targets."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def ensure_data(project_root: Path) -> int:
    if (project_root / "data" / "measurements.csv").is_file():
        return 0

    print("data/measurements.csv is missing -- it is DVC-tracked, so a fresh")
    print("clone does not have it. Rebuild it from the committed raw batches:")
    print("    make data-v2")
    print("(CI does exactly this, which is why it needs no object store.)")
    return 1


def ensure_env(project_root: Path) -> int:
    env_file = project_root / ".env"
    if env_file.is_file():
        return 0

    shutil.copyfile(project_root / ".env.example", env_file)
    print("no .env found -> copied .env.example (defaults; no secrets in this lab)")
    return 0


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"data", "env"}:
        print("usage: python scripts/ensure.py [data|env]", file=sys.stderr)
        return 2

    project_root = Path(__file__).resolve().parents[1]
    return ensure_data(project_root) if sys.argv[1] == "data" else ensure_env(project_root)


if __name__ == "__main__":
    raise SystemExit(main())
