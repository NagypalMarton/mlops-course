"""Run DVC with credentials loaded from the project's .env file."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    env = dict(os.environ)
    if "S3_ACCESS_KEY" in env:
        env["AWS_ACCESS_KEY_ID"] = env["S3_ACCESS_KEY"]
    if "S3_SECRET_KEY" in env:
        env["AWS_SECRET_ACCESS_KEY"] = env["S3_SECRET_KEY"]
    env["DVC_PAGER"] = "cat"

    result = subprocess.run(
        ["uv", "run", "dvc", *sys.argv[1:]],
        cwd=project_root,
        env=env,
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
