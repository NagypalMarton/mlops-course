"""Build the serving image after checking the recorded release gate."""

from __future__ import annotations

import subprocess
from pathlib import Path

from week_09_serving import pipeline, registry
from week_09_serving.cli import bake_values
from week_09_serving.config import load_settings


def main() -> int:
    settings = load_settings()
    verdict = pipeline.read_gate(settings).get("verdict")
    run_id = pipeline.read_run_id(settings)
    try:
        champion = registry.champion_version(settings)
    except Exception:  # noqa: BLE001 -- registry is optional when building offline
        champion = None

    baked = bake_values(verdict, run_id, champion)
    print(
        "baking: "
        f"version={baked['MODEL_VERSION']} "
        f"run={baked['RUN_ID']} "
        f"gate={baked['GATE_VERDICT']} "
        f"source={baked['MODEL_SOURCE']}"
    )
    if baked["GATE_VERDICT"] != "GO":
        print()
        print(
            "REFUSING to build: "
            f"the recorded gate verdict is '{baked['GATE_VERDICT']}'."
        )
        print("Only a model with a GO verdict may be released, and an image is a release.")
        return 1

    project_root = Path(__file__).resolve().parents[1]
    command = [
        "docker",
        "build",
        "--progress=plain",
        "-f",
        "serve.Dockerfile",
        "-t",
        "diabetes-api:local",
        "--build-arg",
        f"MODEL_VERSION={baked['MODEL_VERSION']}",
        "--build-arg",
        f"RUN_ID={baked['RUN_ID']}",
        "--build-arg",
        f"GATE_VERDICT={baked['GATE_VERDICT']}",
        "--build-arg",
        f"MODEL_SOURCE={baked['MODEL_SOURCE']}",
        ".",
    ]
    return subprocess.run(command, cwd=project_root, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
