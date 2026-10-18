"""Run DVC with the project's dotenv configuration on every supported shell."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values


def main() -> int:
    project_dir = Path(__file__).resolve().parents[1]
    values = dotenv_values(project_dir / ".env")
    environment = os.environ.copy()

    for name, value in values.items():
        if value is not None:
            environment.setdefault(name, value)

    if "S3_ACCESS_KEY" in environment:
        environment["AWS_ACCESS_KEY_ID"] = environment["S3_ACCESS_KEY"]
    if "S3_SECRET_KEY" in environment:
        environment["AWS_SECRET_ACCESS_KEY"] = environment["S3_SECRET_KEY"]
    environment["DVC_PAGER"] = "cat"

    completed = subprocess.run(
        ["dvc", *sys.argv[1:]],
        cwd=project_dir,
        env=environment,
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
