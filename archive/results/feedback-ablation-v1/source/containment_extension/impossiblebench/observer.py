"""Linux container observer. Runs as root; the actor runs as UID 1000.

This program is copied into a root-only directory inside each disposable container.
It never executes repository code and never follows repository symlinks. Its Unix
socket and evidence are inaccessible to the actor. Inotify records transient
changes; snapshots preserve file evidence for later semantic review.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import select
import socket
import stat
import struct
import sys
from pathlib import Path

AUDIT = Path("/opt/containment-audit")
ROOT = Path("/testbed")
EVENT_LIMIT = 100_000
FILE_LIMIT = 50_000
BYTE_LIMIT = 256 * 1024 * 1024
MASK = 0x2 | 0x4 | 0x8 | 0x40 | 0x80 | 0x100 | 0x200 | 0x400 | 0x800


def inventory() -> tuple[dict, bool]:
    files, consumed, complete = {}, 0, True
    stack = [ROOT]
    while stack:
        directory = stack.pop()
        try:
            for path in directory.iterdir():
                relative = path.relative_to(ROOT).as_posix()
                if path.name in {".git", "__pycache__", ".pytest_cache"}:
                    continue
                mode = path.lstat().st_mode
                if stat.S_ISLNK(mode):
                    files[relative] = {"symlink": os.readlink(path)}
                elif stat.S_ISDIR(mode):
                    stack.append(path)
                elif stat.S_ISREG(mode):
                    size = path.stat().st_size
                    consumed += size
                    if consumed > BYTE_LIMIT or len(files) >= FILE_LIMIT:
                        return files, False
                    # O_NOFOLLOW prevents a replacement symlink between lstat and open.
                    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
                    with os.fdopen(fd, "rb") as stream:
                        data = stream.read(BYTE_LIMIT + 1)
                    if len(data) > BYTE_LIMIT:
                        return files, False
                    files[relative] = {
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "size": len(data),
                        "mode": stat.S_IMODE(mode),
                    }
        except OSError:
            complete = False
    return files, complete


def serve() -> None:
    protected = json.loads((AUDIT / "protected.json").read_text())
    baseline, snapshot_complete = inventory()
    libc = ctypes.CDLL(None, use_errno=True)
    libc.inotify_init1.argtypes = [ctypes.c_int]
    libc.inotify_add_watch.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
    fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
    if fd < 0:
        raise OSError(ctypes.get_errno(), "inotify initialization failed")
    watches, events = {}, []
    complete = True

    def watch_inode(path: Path) -> None:
        nonlocal complete
        relative = path.relative_to(ROOT).as_posix()
        if not any(relative == p or relative.startswith(p + "/") for p in protected):
            return
        if path.is_symlink():
            complete = False
            return
        wd = libc.inotify_add_watch(fd, os.fsencode(path), MASK)
        if wd < 0:
            complete = False
        else:
            # Also observe writes through hard links outside the repository.
            watches[wd] = path

    def watch_tree(directory: Path) -> None:
        nonlocal complete
        if directory.is_symlink():
            return
        wd = libc.inotify_add_watch(fd, os.fsencode(directory), MASK)
        if wd < 0:
            complete = False
            return
        watches[wd] = directory
        try:
            for child in directory.iterdir():
                if child.is_dir() and not child.is_symlink():
                    watch_tree(child)
                elif child.is_file() or child.is_symlink():
                    watch_inode(child)
        except OSError:
            complete = False

    def drain() -> None:
        nonlocal complete
        while True:
            try:
                data = os.read(fd, 65536)
            except BlockingIOError:
                break
            offset = 0
            while offset < len(data):
                wd, mask, _cookie, length = struct.unpack_from("iIII", data, offset)
                offset += 16
                name = os.fsdecode(data[offset : offset + length].split(b"\0", 1)[0])
                offset += length
                if mask & 0x4000:  # IN_Q_OVERFLOW: no clean negative can be certified.
                    complete = False
                    continue
                parent = watches.get(wd)
                if parent is None:
                    continue
                path = parent / name if name else parent
                relative = path.relative_to(ROOT).as_posix()
                if mask & 0x8000:  # IN_IGNORED after deletion; parent event is retained.
                    watches.pop(wd, None)
                    continue
                if mask & 0x40000000 and mask & (0x100 | 0x80):
                    watch_tree(path)
                elif mask & (0x100 | 0x80) and path.is_file():
                    watch_inode(path)
                if mask & (0x400 | 0x800) and path == ROOT:
                    complete = False
                is_protected = any(
                    relative == p
                    or relative.startswith(p + "/")
                    or (mask & 0x40000000 and p.startswith(relative + "/"))
                    for p in protected
                )
                if len(events) >= EVENT_LIMIT:
                    complete = False
                else:
                    events.append(
                        {
                            "seq": len(events),
                            "path": relative,
                            "mask": mask,
                            "protected": bool(is_protected),
                        }
                    )

    watch_tree(ROOT)
    sock = socket.socket(socket.AF_UNIX)
    sock.bind(str(AUDIT / "control.sock"))
    os.chmod(AUDIT / "control.sock", 0o600)
    sock.listen(1)
    (AUDIT / "ready").write_text("ready")
    while True:
        readable, _, _ = select.select([fd, sock], [], [])
        if fd in readable:
            drain()
        if sock in readable:
            conn, _ = sock.accept()
            with conn:
                conn.settimeout(10)
                request = conn.recv(64).decode().strip()
                drain()
                response = {"complete": complete, "events": events, "protected_paths": protected}
                if request == "final":
                    current, current_complete = inventory()
                    changes = {}
                    for path in sorted(set(baseline) | set(current)):
                        if baseline.get(path) != current.get(path):
                            entry = {"before": baseline.get(path), "after": current.get(path)}
                            if path in current and "symlink" not in current[path]:
                                try:
                                    file_fd = os.open(ROOT / path, os.O_RDONLY | os.O_NOFOLLOW)
                                    with os.fdopen(file_fd, "rb") as stream:
                                        entry["content_prefix"] = stream.read(65536).decode(
                                            "utf-8", errors="replace"
                                        )
                                except OSError:
                                    current_complete = False
                            changes[path] = entry
                    response.update(
                        file_changes=changes,
                        snapshots_complete=snapshot_complete and current_complete,
                    )
                elif request != "events":
                    response = {"error": "unknown observer request"}
                conn.sendall(json.dumps(response).encode())


if __name__ == "__main__":
    if sys.argv[1:] != ["serve"]:
        raise SystemExit("Expected: observer.py serve")
    serve()
