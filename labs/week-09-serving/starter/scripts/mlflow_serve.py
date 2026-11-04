"""Run the MLflow model server with the project's .env file loaded."""

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
    model_name = env.get("MLFLOW_REGISTERED_MODEL_NAME", "diabetes-classifier")
    champion_alias = env.get("MLFLOW_CHAMPION_ALIAS", "champion")
    command = [
        "uv",
        "run",
        "mlflow",
        "models",
        "serve",
        "-m",
        f"models:/{model_name}@{champion_alias}",
        *sys.argv[1:],
    ]
    result = subprocess.run(command, cwd=project_root, env=env, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
