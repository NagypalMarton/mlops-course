"""Run DVC with credentials loaded from the project .env file."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values


def main() -> int:
    values = dotenv_values(Path(".env"))
    environment = os.environ.copy()
    environment.update(
        {
            "AWS_ACCESS_KEY_ID": values.get("S3_ACCESS_KEY", ""),
            "AWS_SECRET_ACCESS_KEY": values.get("S3_SECRET_KEY", ""),
            "DVC_PAGER": "",
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
        }
    )
    arguments = sys.argv[1:]
    if arguments == ["remote-add"]:
        arguments = [
            "remote",
            "add",
            "-d",
            values["DVC_REMOTE_NAME"],
            f"s3://{values['DVC_BUCKET']}/{values['DVC_REMOTE_PATH']}",
        ]
    elif arguments == ["remote-modify-endpoint"]:
        arguments = [
            "remote",
            "modify",
            values["DVC_REMOTE_NAME"],
            "endpointurl",
            f"http://127.0.0.1:{values['S3_API_PORT']}",
        ]
    return subprocess.run(["uv", "run", "dvc", *arguments], env=environment).returncode


if __name__ == "__main__":
    raise SystemExit(main())
