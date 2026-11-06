"""Disposable Docker backend; no host mounts, external network, or actor root access."""

from __future__ import annotations

import asyncio
import json
import shlex
import subprocess
import tempfile
import uuid
from pathlib import Path

from .study import relative_path

AUDIT = "/opt/containment-audit"
BOOTSTRAP = r"""
import json, os, pathlib, subprocess, sys
p = pathlib.Path('/opt/containment-audit')
row = json.loads((p / 'record.json').read_text())
root = pathlib.Path('/testbed')
root.mkdir(exist_ok=True)
if 'files' in row:
    for name, content in row['files'].items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    if sys.argv[1] == 'reference':
        for name, content in row['reference_files'].items():
            (root / name).write_text(content)
else:
    subprocess.run(['git', '-C', str(root), 'reset', '--hard', row['base_commit']], check=True)
    for name in ['test_patch'] + (['reference_patch'] if sys.argv[1] == 'reference' else []):
        patch = p / (name + '.diff')
        patch.write_text(row[name])
        subprocess.run(['git', '-C', str(root), 'apply', '--check', str(patch)], check=True)
        subprocess.run(['git', '-C', str(root), 'apply', str(patch)], check=True)
protected = set(row['protected_paths']) | {'.git'}
for directory, dirs, files in os.walk(root, followlinks=False):
    for name in files:
        path = pathlib.Path(directory) / name
        rel = path.relative_to(root).as_posix()
        if (name.startswith('test_') and name.endswith('.py')) or name in {
            'conftest.py', 'pytest.ini', 'tox.ini', 'setup.cfg', 'pyproject.toml'
        }:
            protected.add(rel)
    for name in dirs + files:
        path = pathlib.Path(directory) / name
        os.chown(path, 1000, 1000, follow_symlinks=False)
os.chown(root, 1000, 1000)
(p / 'protected.json').write_text(json.dumps(sorted(protected)))
# The evaluator is root-owned and never writes to a model-controlled path.
(p / 'grade.sh').write_text('cd /testbed\n' + row['test_command'] + '\n')
os.chmod(p / 'grade.sh', 0o600)
"""
REAP = r"""
import os, pathlib, signal, time
for _ in range(20):
    found = False
    for p in pathlib.Path('/proc').iterdir():
        if p.name.isdigit():
            try:
                uid = (p/'status').read_text().split('Uid:\t')[1].split()[0]
                if uid == '1000':
                    os.kill(int(p.name), signal.SIGKILL)
                    found = True
            except (OSError, IndexError):
                pass
    if not found:
        break
    time.sleep(.01)
else:
    raise RuntimeError('Actor processes did not stop')
"""
READ_OBSERVER = r"""
import socket, sys
s = socket.socket(socket.AF_UNIX)
s.settimeout(30)
s.connect('/opt/containment-audit/control.sock')
s.sendall(sys.argv[1].encode())
while True:
    data = s.recv(65536)
    if not data: break
    sys.stdout.buffer.write(data)
"""


class DockerBackend:
    def __init__(self, *, command_timeout: int = 60, grade_timeout: int = 300):
        self.name = "containment-ib-" + uuid.uuid4().hex
        self.command_timeout = command_timeout
        self.grade_timeout = grade_timeout
        self.created = False
        self.ready = False
        self.record = None
        self.latest = {"complete": False, "events": []}
        self.isolation = {}

    async def _docker(
        self, *args: str, input_text: str | None = None, timeout: int = 60, check: bool = True
    ) -> subprocess.CompletedProcess:
        def invoke():
            # Spool rather than buffer arbitrary actor output into runner memory.
            with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
                result = subprocess.run(
                    ["docker", *args],
                    input=input_text,
                    text=True,
                    stdout=stdout,
                    stderr=stderr,
                    timeout=timeout,
                    check=False,
                )
                stdout.seek(0)
                stderr.seek(0)
                limit = 32 * 1024 * 1024 if args and args[0] == "exec" else 1024 * 1024
                output, error = stdout.read(limit + 1), stderr.read(limit + 1)
                if len(output) > limit or len(error) > limit:
                    raise RuntimeError("Container output exceeded capture limit")
                result.stdout = output.decode("utf-8", errors="replace")
                result.stderr = error.decode("utf-8", errors="replace")
                if check and result.returncode:
                    raise RuntimeError(f"Docker {args[0]} failed: {result.stderr[-2000:]}")
                return result

        return await asyncio.to_thread(invoke)

    async def _python(self, code: str, *args: str) -> subprocess.CompletedProcess:
        return await self._docker(
            "exec", "--user", "0:0", self.name, self.record["python"], "-I", "-c", code, *args
        )

    async def setup(self, record: dict, reference: bool = False) -> None:
        self.record = record
        # No auto-pull: an image must already have been acquired and digest-pinned.
        await self._docker("image", "inspect", record["image"])
        await self._docker(
            "create",
            "--name",
            self.name,
            "--pull",
            "never",
            "--network",
            "none",
            "--cap-drop",
            "ALL",
            "--cap-add",
            "CHOWN",
            "--cap-add",
            "FOWNER",
            "--cap-add",
            "KILL",
            "--security-opt",
            "no-new-privileges:true",
            "--pids-limit",
            "256",
            "--memory",
            "2g",
            "--cpus",
            "2",
            "--user",
            "0:0",
            "--label",
            "containment.impossiblebench=true",
            "--entrypoint",
            "/bin/sh",
            record["image"],
            "-c",
            "while :; do sleep 3600; done",
        )
        self.created = True
        await self._docker("start", self.name)
        inspected = json.loads((await self._docker("inspect", self.name)).stdout)[0]
        host = inspected["HostConfig"]
        if (
            host["NetworkMode"] != "none"
            or inspected["Mounts"]
            or host["Privileged"]
            or host.get("PortBindings")
            or "ALL" not in host["CapDrop"]
            or "no-new-privileges:true" not in host["SecurityOpt"]
        ):
            raise RuntimeError("Container does not meet the required isolation configuration")
        self.isolation = {
            "network": host["NetworkMode"],
            "mounts": inspected["Mounts"],
            "privileged": host["Privileged"],
            "image_id": inspected["Image"],
            "security_options": host["SecurityOpt"],
            "caps": host["CapAdd"],
        }
        await self._python(
            "import os; os.makedirs('/opt/containment-audit',mode=0o700,exist_ok=False)"
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "record.json").write_text(json.dumps(record))
            (root / "observer.py").write_text(Path(__file__).with_name("observer.py").read_text())
            for name in ("record.json", "observer.py"):
                await self._docker("cp", str(root / name), f"{self.name}:{AUDIT}/{name}")
        await self._python(BOOTSTRAP, "reference" if reference else "empty")
        await self._docker(
            "exec",
            "--detach",
            "--user",
            "0:0",
            self.name,
            record["python"],
            "-I",
            f"{AUDIT}/observer.py",
            "serve",
        )
        for _ in range(100):
            ready = await self._python(
                "from pathlib import Path; print(Path('" + AUDIT + "/ready').exists())"
            )
            if ready.stdout.strip() == "True":
                self.ready = True
                break
            await asyncio.sleep(0.05)
        if not self.ready:
            raise RuntimeError("Independent observer did not start")
        # These probes run before model actions and do not fetch any public destination.
        probe = await self._docker(
            "exec",
            "--user",
            "1000:1000",
            self.name,
            record["python"],
            "-I",
            "-c",
            r"""
import json, os, pathlib, socket
s = pathlib.Path('/proc/self/status').read_text()
routes = pathlib.Path('/proc/net/route').read_text().splitlines()[1:]
interfaces = [name for _, name in socket.if_nameindex()]
active = [name for name in interfaces
          if int(pathlib.Path('/sys/class/net',name,'flags').read_text(),16) & 1]
try:
    pathlib.Path('/opt/containment-audit/probe').write_text('forbidden')
    protected = False
except PermissionError:
    protected = True
print(json.dumps({'uid': os.getuid(), 'audit_protected': protected,
                  'no_new_privs': 'NoNewPrivs:\t1' in s,
                  'caps_zero': int(s.split('CapEff:\t')[1].split()[0],16) == 0,
                  'no_routes': not routes,
                  'no_external_interface_up': all(name == 'lo' for name in active)}))
""",
        )
        self.isolation["probe"] = json.loads(probe.stdout)
        p = self.isolation["probe"]
        if p["uid"] != 1000 or not all(v for k, v in p.items() if k != "uid"):
            raise RuntimeError("Actor privilege or network qualification failed: " + json.dumps(p))

    async def shell(self, command: str) -> dict:
        try:
            result = await self._docker(
                "exec",
                "--user",
                "1000:1000",
                "--workdir",
                "/testbed",
                "--env",
                "HOME=/tmp",
                self.name,
                "/bin/bash",
                "--noprofile",
                "--norc",
                "-c",
                command,
                timeout=self.command_timeout,
                check=False,
            )
        finally:
            await self._python(REAP)
        return {
            "returncode": result.returncode,
            "stdout": result.stdout[:65536],
            "stderr": result.stderr[:65536],
            "output_truncated": len(result.stdout) > 65536 or len(result.stderr) > 65536,
        }

    async def grade(self) -> dict:
        # Send the trusted command over stdin; never invoke a script stored in the workspace.
        # Evaluation code still runs with actor privileges, including when tests import code.
        try:
            result = await self._docker(
                "exec",
                "-i",
                "--user",
                "1000:1000",
                "--workdir",
                "/testbed",
                "--env",
                "HOME=/tmp",
                self.name,
                "/bin/bash",
                "--noprofile",
                "--norc",
                "-s",
                input_text=("set -euo pipefail\n" + self.record["test_command"]),
                timeout=self.grade_timeout,
                check=False,
            )
        finally:
            await self._python(REAP)
        return {
            "passed": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout[:65536],
            "stderr": result.stderr[:65536],
            "test_command": self.record["test_command"],
            "note": "Raw mutable-workspace result; passing is not semantic correctness.",
        }

    async def evidence(self) -> dict:
        if not self.ready:
            return self.latest
        await self._python(REAP)
        reply = await self._python(READ_OBSERVER, "events")
        self.latest = {**json.loads(reply.stdout), "isolation": self.isolation}
        return self.latest

    async def capture_final(self) -> dict:
        if not self.ready:
            return self.latest
        await self._python(REAP)
        reply = await self._python(READ_OBSERVER, "final")
        self.latest = {**json.loads(reply.stdout), "isolation": self.isolation}
        self.latest["complete"] &= self.latest["snapshots_complete"]
        return self.latest

    async def close(self) -> None:
        if self.created:
            await self._docker("rm", "--force", self.name)
            self.created = False


def test_command(test_cmd: str, files: list[str], setup: list[str] | None = None) -> str:
    """Build a command from a trusted SWE-bench harness spec, without online installation."""
    if not files:
        raise ValueError("No evaluation test files found in the dataset patch")
    for path in files:
        relative_path(path)
    return (
        "source /opt/miniconda3/bin/activate\nconda activate testbed\n"
        + "\n".join(setup or [])
        + "\n"
        + test_cmd
        + " "
        + " ".join(shlex.quote(path) for path in files)
    )
