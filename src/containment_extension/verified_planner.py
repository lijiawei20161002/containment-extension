"""Validated contracts and finite, permission-constrained recovery search.

The planner consumes public transition descriptions, current observations and
permissions. It never reads benchmark labels and never controls tool dispatch.
"""
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import heapq
import itertools
import json


def compile_office_contract(contract, state):
    """Compile estimated structural arguments to the actual public tool semantics.

    Calendar creation accepts a combined date/time, not a separate nested date.
    Preserve the estimate's date rather than choosing a date from scoring labels.
    The public runtime supplies its documented default year when none is present.
    """
    from .sabench_study import APICall, runtime, write_operation_from_call
    result, changes, errors = deepcopy(contract), [], []
    for index, write in enumerate(result["writes"]):
        name, args = write["tool_name"], deepcopy(write["arguments"])
        tool, action = runtime.split_api_name(name)
        if name == "calendar_create":
            nested = args.get("fields", {})
            if not isinstance(nested, dict):
                errors.append({"write": index, "reason": "fields must be an object"})
                continue
            # Only promote fields actually consumed by calendar creation.
            for key in ("title", "time", "start", "start_time", "duration", "duration_minutes", "attendees", "date"):
                if key in nested:
                    if key in args and args[key] != nested[key]:
                        errors.append({"write": index, "reason": f"Conflicting {key} values"})
                    else:
                        args[key] = nested[key]
            unknown = set(nested) - {"title", "time", "start", "start_time", "duration", "duration_minutes", "attendees", "date"}
            if unknown:
                errors.append({"write": index, "reason": "Unsupported create fields: " + ",".join(sorted(unknown))})
            args.pop("fields", None)
            clock = str(args.get("time") or args.get("start") or args.get("start_time") or "")
            date = str(args.pop("date", ""))
            if date:
                # Do not guess when two complete date specifications conflict.
                try:
                    parsed = datetime.fromisoformat(clock)
                except ValueError:
                    args["time"] = date + " " + clock
                else:
                    if date not in {parsed.date().isoformat(), parsed.strftime("%b %d"), parsed.strftime("%B %d")}:
                        errors.append({"write": index, "reason": "Separate date conflicts with full timestamp"})
            op = write_operation_from_call(APICall(tool, action, args))
            try:
                datetime.fromisoformat(str(op.fields["time"]))
            except ValueError:
                errors.append({"write": index, "reason": "Creation needs a complete date and time"})
            if not op.fields.get("title"):
                errors.append({"write": index, "reason": "Creation needs a title"})
            duration = op.fields.get("duration")
            if type(duration) is not int or duration <= 0:
                errors.append({"write": index, "reason": "Duration must be a positive integer"})
            args["time"] = op.fields["time"]
        args = runtime.normalize_write_args(tool, action, args, state)
        op = write_operation_from_call(APICall(tool, action, args))
        if op is None:
            errors.append({"write": index, "reason": "Not a supported write"})
            continue
        # Validate executable targets without inferring any new permission.
        if action not in {"create", "send", "draft_save"}:
            from sabench_re.state import entity_attrs
            if entity_attrs(state, op.entity_id) is None:
                errors.append({"write": index, "reason": "Target is absent from the visible workspace"})
        if args != write["arguments"]:
            changes.append({"write": index, "before": write["arguments"], "after": args})
        from .office_arguments import validate_office_arguments
        errors.extend({"write": index, **issue} for issue in validate_office_arguments(name, args))
        write.update(arguments=args, operation=op.to_dict())
    if errors:
        # A failed compiler never silently turns the raw proposal into advice.
        return {"valid": False, "contract": None, "changes": changes, "errors": errors}
    return {"valid": True, "contract": result, "changes": changes, "errors": []}


@dataclass(frozen=True)
class Action:
    name: str
    label: str
    requires: frozenset[str]
    forbids: frozenset[str]
    adds: frozenset[str]
    deletes: frozenset[str]
    permission_requires: frozenset[str]
    permitted: bool = True
    cost: int = 1

    @classmethod
    def from_dict(cls, raw):
        fields = {k: frozenset(raw.get(k, [])) for k in
                  ("requires", "forbids", "adds", "deletes", "permission_requires")}
        if type(raw.get("cost", 1)) is not int or raw.get("cost", 1) <= 0:
            raise ValueError("Actions need a positive integer resource cost")
        return cls(raw["name"], raw["label"], **fields,
                   permitted=raw.get("permitted", True), cost=raw.get("cost", 1))

    def to_dict(self):
        return {k: sorted(v) if isinstance(v, frozenset) else v for k, v in vars(self).items()}


def authorized(action, facts):
    return action.permitted and action.permission_requires <= facts


def applicable(action, facts, budget):
    return action.cost <= budget and action.requires <= facts and not action.forbids & facts


def transition(action, facts, budget):
    if not applicable(action, facts, budget):
        raise ValueError("Unsatisfied operational precondition")
    return (facts - action.deletes) | action.adds, budget - action.cost


def verify_route(actions, facts, budget, route, goals):
    """Independent path check before an executable recommendation is published."""
    bank = {a.name: a for a in actions}
    for name in route:
        a = bank[name]
        if not authorized(a, facts) or not applicable(a, facts, budget):
            return False
        facts, budget = transition(a, facts, budget)
    return goals <= facts


def search(actions, facts, budget, goals, horizon, node_limit=200000):
    """Exact uniform-cost search with state/horizon dominance and dynamic grants.

    Optimize complete authorized goal satisfaction, then resource cost and steps.
    Exhaustion is distinct from a proof that no permitted plan exists. No hidden
    sampled transition or scoring label is an input.
    """
    facts, goals = frozenset(facts), frozenset(goals)
    if goals <= facts:
        return {"status": "complete", "plan": [], "cost": 0, "expanded": 0}
    counter = itertools.count()
    queue = [(0, 0, next(counter), facts, ())]
    frontier = {facts: [(0, 0)]}
    expanded = 0
    best_partial = (len(facts & goals), 0, ())
    while queue:
        cost, steps, _, current, route = heapq.heappop(queue)
        if (cost, steps) not in frontier[current]:
            continue
        if goals <= current:
            assert verify_route(actions, facts, budget, route, goals)
            return {"status": "plan", "plan": list(route), "cost": cost, "expanded": expanded}
        expanded += 1
        if expanded > node_limit:
            return {"status": "search_limit", "plan": [], "cost": None, "expanded": expanded}
        progress = len(current & goals)
        if (progress, -cost) > best_partial[:2]:
            best_partial = (progress, -cost, route)
        if steps >= horizon:
            continue
        for a in actions:
            if not authorized(a, current) or not applicable(a, current, budget - cost):
                continue
            nxt, _ = transition(a, current, budget - cost)
            c, n = cost + a.cost, steps + 1
            seen = frontier.setdefault(nxt, [])
            if any(old_cost <= c and old_steps <= n for old_cost, old_steps in seen):
                continue
            frontier[nxt] = [(oc, os) for oc, os in seen if not (c <= oc and n <= os)] + [(c, n)]
            heapq.heappush(queue, (c, n, next(counter), nxt, route + (a.name,)))
    return {"status": "infeasible", "plan": [], "cost": None, "expanded": expanded,
            "best_partial_plan": list(best_partial[2]), "best_partial_goals": best_partial[0]}


def guidance(actions, facts, budget, goals, horizon, arm):
    allowed = [a.name for a in actions if authorized(a, facts)]
    valid = [a for a in actions if authorized(a, facts) and applicable(a, facts, budget)]
    base = {"permitted_actions_now": allowed,
            "executable_permitted_actions_now": [a.name for a in valid],
            "rule": "Advice only. Execution is not blocked. Permission is checked at the time of each action."}
    if arm == "permissions":
        return base
    if arm == "greedy":
        ranked = sorted(valid, key=lambda a: (-len((a.adds - facts) & goals), a.cost, a.name))
        base["myopic_recommendation"] = ranked[0].name if ranked else "STOP"
        return base
    if arm != "planner":
        raise ValueError("Unknown advice arm")
    plan = search(actions, facts, budget, goals, horizon)
    base["planning"] = plan
    base["recommendation"] = plan["plan"][0] if plan["plan"] else "STOP"
    return base
