"""Verify preserved files against the reorganization manifest without changing them."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tracked-only", action="store_true",
                        help="Verify only files originally tracked by Git (for fresh clones).")
    args = parser.parse_args()
    archive = Path(__file__).resolve().parent
    root = archive.parent
    manifest = json.loads((archive / "manifest.json").read_text())
    checked, failures = 0, []
    for entry in manifest["entries"]:
        destination = root / entry["archived"]
        for item in entry["files"]:
            if args.tracked_only and not item["tracked"]:
                continue
            path = destination / item["relative"] if item["relative"] else destination
            if not path.resolve().is_relative_to(archive):
                failures.append({"path": str(path), "error": "outside archive"})
                continue
            try:
                with path.open("rb") as handle:
                    digest = hashlib.file_digest(handle, "sha256").hexdigest()
                if digest != item["sha256"]:
                    failures.append({"path": str(path.relative_to(root)), "error": "hash mismatch"})
            except OSError as exc:
                failures.append({"path": str(path.relative_to(root)), "error": str(exc)})
            checked += 1
    print(json.dumps({"checked": checked, "failures": failures}, indent=2))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
