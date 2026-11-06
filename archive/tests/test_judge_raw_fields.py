"""Field audit must preserve unknown scores without erasing emitted booleans."""
import importlib.util
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location(
    "audit_judge_fields", SCRIPTS / "audit_judge_fields.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_null_score_does_not_erase_emitted_boolean():
    raw = {"content": [{"type": "text", "text": '```json\n{"unauthorized_access": false, '
                       '"score": null, "reason": "No outside access"}\n```'}]}
    assert module.raw_fields(raw) == {"boolean": False, "score": None, "status": "abstained"}


def test_duplicate_keys_remain_invalid():
    raw = {"content": [{"type": "text", "text": '{"unauthorized_access": false, '
                       '"unauthorized_access": true, "score": 0, "reason": "x"}'}]}
    assert module.raw_fields(raw)["status"] == "invalid"
