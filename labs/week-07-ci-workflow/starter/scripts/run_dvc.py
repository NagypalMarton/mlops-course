"""Run DVC with the lab's dotenv configuration."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

from dotenv import load_dotenv


def main() -> int:
    load_dotenv()

    missing = [
        name
        for name in ("S3_ACCESS_KEY", "S3_SECRET_KEY")
        if not os.environ.get(name)
    ]
    if missing:
        names = ", ".join(missing)
        raise SystemExit(f"Missing required environment variable(s): {names}")

    os.environ["AWS_ACCESS_KEY_ID"] = os.environ["S3_ACCESS_KEY"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = os.environ["S3_SECRET_KEY"]
    os.environ["DVC_PAGER"] = "cat"

    dvc = shutil.which("dvc")
    if dvc is None:
        raise SystemExit("DVC is not installed in the project environment")

    return subprocess.run([dvc, *sys.argv[1:]], check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
