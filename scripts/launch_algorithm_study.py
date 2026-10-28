"""Detach an already prepared experiment using its immutable source snapshot."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--env-file", type=Path, required=True)
    p.add_argument("--ca-file", type=Path)
    args = p.parse_args()
    output = args.output.resolve()
    frozen = output / "source/scripts/run_algorithm_study.py"
    if not frozen.is_file() or not (output / "plan.sha256.json").is_file():
        p.error("Prepare and qualify the experiment first")
    if (output / "completed.json").exists():
        p.error("This cohort is already complete")
    worker_path = output / "worker.json"
    if worker_path.exists():
        old = json.loads(worker_path.read_text())
        if old["status"] == "running":
            try:
                os.kill(old["pid"], 0)
            except ProcessLookupError:
                pass
            else:
                p.error("A worker is already running")
    command = [sys.executable, "-u", str(frozen), "run", "--output", str(output),
               "--env-file", str(args.env_file.resolve())]
    if args.ca_file:
        command += ["--ca-file", str(args.ca_file.resolve())]
    with (output / "worker.log").open("ab", buffering=0) as log:
        child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                 start_new_session=True, close_fds=True,
                                 cwd=str(output / "source"))
    time.sleep(1)
    if child.poll() is not None:
        p.error(f"Worker exited with code {child.returncode}; inspect {output / 'worker.log'}")
    print(json.dumps({"pid": child.pid, "detached": True, "output": str(output),
                      "log": str(output / "worker.log"), "source": "immutable snapshot"}, indent=2))


if __name__ == "__main__":
    main()
