"""Executable library case INC-2026-015: a local-only artifact tool broker.

The fixture is deterministic and entirely in memory. It demonstrates enforcement
for a closed structured tool surface, not containment of arbitrary Python/shell.
Run identity, artifact classification, and the manifest are harness-owned inputs.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "incidents/records/15-public-hosting-local-workbook.json"
ACTION_KEYS = {"operation", "artifact", "destination"}
FIXTURE_ROUTES = {
    "check_peer": "peer-B",
    "export": "public-host",
    "deliver": "local-output",
    "report_blocked": "run-log",
}
WORKBOOK_BYTES = "SYNTHETIC workbook contents: quarter,revenue\nQ1,100\n"


def decide(
    policy: dict, action: object, *, run_id: str, principal: str
) -> tuple[bool, str]:
    """Fail closed before dispatch using harness-owned trust labels."""
    if not isinstance(action, dict) or set(action) != ACTION_KEYS:
        return False, "invalid_action"
    if not all(isinstance(value, str) and value for value in action.values()):
        return False, "invalid_action"
    if run_id != policy["run_id"] or principal != policy["principal"]:
        return False, "wrong_run_or_principal"
    artifact = policy["artifacts"].get(action["artifact"])
    if artifact is None:
        return False, "unknown_artifact"
    is_export = action["operation"] == "export"
    if is_export and artifact["classification"] == "local_only":
        return False, "local_only_no_export"
    routes = policy["allowed_routes"].get(action["operation"], [])
    if action["destination"] not in routes:
        return False, "route_not_granted"
    return True, "explicit_grant"


def digest(state: dict) -> str:
    return hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()


class WorkbookBroker:
    """Only dispatch accepted structured calls. The baseline bypass is test-only."""

    def __init__(self, policy: dict, *, enforce: bool = True):
        self._policy = copy.deepcopy(policy)
        if policy.get("default_decision") != "deny":
            raise ValueError("Policy must default to deny")
        self.enforce = enforce
        self.state = {"public_objects": {}, "local_deliveries": {}, "status": "running"}
        self.events: list[dict] = []

    def request(self, action: object, *, run_id: str, principal: str) -> dict:
        action = copy.deepcopy(action)
        before = digest(self.state)
        allowed, reason = decide(self._policy, action, run_id=run_id, principal=principal)
        if self.state["status"] != "running":
            allowed, reason = False, "run_already_terminal"
        elif not self.enforce and reason not in {
            "invalid_action", "wrong_run_or_principal", "unknown_artifact"
        }:
            allowed, reason = True, "baseline_policy_bypassed"
        # This fixture has a closed set of in-memory handlers even in baseline mode.
        if allowed and FIXTURE_ROUTES.get(action["operation"]) != action["destination"]:
            allowed, reason = False, "unsupported_fixture_route"
        if allowed:
            response = self._dispatch(action)
        else:
            response = {"status": "denied", "reason": reason, "safe_exit": "report_blocked"}
        event = {
            "seq": len(self.events) + 1,
            "incident_id": self._policy["incident_id"],
            "policy_id": self._policy["policy_id"],
            "run_id": run_id,
            "principal": principal,
            "action": action,
            "decision": "allow" if allowed else "deny",
            "reason": reason,
            "dispatched": allowed,
            "response": response,
            "state_before_sha256": before,
            "state_after_sha256": digest(self.state),
        }
        self.events.append(copy.deepcopy(event))
        return copy.deepcopy(event)

    def _dispatch(self, action: dict) -> dict:
        operation, artifact = action["operation"], action["artifact"]
        if operation == "check_peer":
            return {"status": "unavailable", "reason": "peer_has_no_shared_filesystem"}
        if operation == "export":
            self.state["public_objects"][artifact] = WORKBOOK_BYTES
            return {"status": "published", "location": "decoy://public-host/wb-001"}
        if operation == "deliver":
            self.state["local_deliveries"][artifact] = WORKBOOK_BYTES
            self.state["status"] = "completed"
            return {"status": "completed", "location": "local-output/wb-001"}
        if operation == "report_blocked":
            self.state["status"] = "blocked"
            return {"status": "blocked", "reason": "collaboration_requires_owner_review"}
        raise AssertionError("Unregistered operation reached dispatch")

    def observe(self) -> dict:
        """Score stored effects independently of the policy decision label."""
        return {
            "public_objects": len(self.state["public_objects"]),
            "local_deliveries": len(self.state["local_deliveries"]),
            "status": self.state["status"],
            "denials": sum(event["decision"] == "deny" for event in self.events),
        }


def run_suite(record_path: Path = RECORD) -> dict:
    """Resolve the executable bundle from the library record and check three runs."""
    record = json.loads(record_path.read_text())
    case_path = ROOT / record["executable"]["replay_case"]
    case = json.loads(case_path.read_text())
    policy = json.loads((case_path.parent / case["policy"]).read_text())
    if not (record["id"] == case["incident_id"] == policy["incident_id"]):
        raise ValueError("Record, case and policy must refer to the same incident")
    runs = []
    for fixture_key, mode in [
        ("unsafe_fixture", "baseline"),
        ("unsafe_fixture", "enforced"),
        ("benign_fixture", "enforced"),
    ]:
        fixture = json.loads((case_path.parent / case[fixture_key]).read_text())
        broker = WorkbookBroker(policy, enforce=mode == "enforced")
        for action in fixture["actions"]:
            broker.request(action, run_id=policy["run_id"], principal=policy["principal"])
        observed = broker.observe()
        runs.append({
            "fixture": fixture["name"], "mode": mode, "observed": observed,
            "expected": fixture["expectations"][mode],
            "passed": observed == fixture["expectations"][mode],
            "events": broker.events,
        })
    return {
        "incident_id": record["id"], "case_id": case["case_id"],
        "policy_id": policy["policy_id"], "kind": case["kind"],
        "scope": "Three scripted runs of one synthetic incident analogue; no model or network.",
        "passed": all(run["passed"] for run in runs), "runs": runs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional JSON result and full decision traces")
    args = parser.parse_args()
    result = run_suite()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    for run in result["runs"]:
        print(f"{run['fixture']:24} {run['mode']:8} {run['observed']}")
    print("PASS: all three replay expectations matched" if result["passed"] else "FAIL")
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
