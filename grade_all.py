#!/usr/bin/env python3
# Minimal loop: runs the grader in Docker for every .ipynb in Submissions/.
# Your existing grader handles CSV output; this script only loops & runs.

import os
import platform
import subprocess
from pathlib import Path

IMAGE = os.environ.get("SAGE_DOCKER_IMAGE", "sagemath/sagemath:latest")
ROOT = Path(__file__).resolve().parent
SUBMISSIONS = ROOT / "Submissions"
GRADER = "/home/sage/work/grader/run_nbtests.py"
WORK_MOUNT = f"{ROOT.as_posix()}:/home/sage/work"

# Apple Silicon often needs amd64 since the Sage image may not have arm64
platform_flag = []
if platform.system().lower() == "darwin" and "arm" in platform.machine().lower():
    platform_flag = ["--platform", "linux/amd64"]

# find all .ipynb except checkpoints
files = sorted(
    p for p in SUBMISSIONS.rglob("*.ipynb")
    if ".ipynb_checkpoints" not in p.as_posix()
)

if not files:
    print("No .ipynb files found in Submissions/")
    raise SystemExit(0)

for nb in files:
    nb_in_container = f"/home/sage/work/{nb.relative_to(ROOT).as_posix()}"
    print(f"\n==> Grading {nb.name}")
    cmd = [
        "docker", "run", "--rm", "-i",
        *platform_flag,
        "-v", WORK_MOUNT,
        IMAGE,
        "sage", "-python", GRADER,
        "--nb", nb_in_container,
    ]
    # Stream output live
    subprocess.run(cmd, check=False)
