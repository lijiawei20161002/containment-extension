"""Office argument validation using public API semantics, never task permissions.

The upstream fixture accepts malformed writes and records success. New studies
reject these requests before dispatch and let the actor repair the arguments.
This is a common environment change, not planner-only authorization enforcement.
"""
from copy import deepcopy
from datetime import datetime
import json


def _recipient_errors(value, path):
    values = value if isinstance(value, list) else [value]
    if not values:
        return [{"argument": path, "message": "Provide at least one recipient."}]
    for item in values:
        if not isinstance(item, str) or not item.strip():
            return [{"argument": path, "message": "Use a recipient string or an array of nonempty recipient strings."}]
        try:
            decoded = json.loads(item)
        except (ValueError, TypeError):
            continue
        if isinstance(decoded, (list, dict, str)):
            return [{"argument": path, "message":
                "Do not encode recipients as JSON text inside a string. Use the literal address or a native array of addresses."}]
    return []


def validate_office_arguments(name, args):
    """Validate representations only; this function has no state or grant input."""
    if not isinstance(args, dict):
        return [{"argument": "$", "message": "Arguments must be an object."}]
    errors = []
    if name in {"email_send", "email_forward"}:
        nested = args.get("fields", {})
        if not isinstance(nested, dict):
            return [{"argument": "fields", "message": "fields must be an object."}]
        if "to" in args and "to" in nested and args["to"] != nested["to"]:
            errors.append({"argument": "to", "message": "Top-level and nested recipients conflict."})
        recipients = args.get("to", nested.get("to"))
        errors.extend(_recipient_errors(recipients, "to"))
    elif name == "calendar_create":
        nested = args.get("fields", {})
        if nested or not isinstance(nested, dict) or "date" in args:
            errors.append({"argument": "fields", "message":
                "Calendar creation reads top-level arguments. Put the date and clock together in time; separate date and nested fields are not consumed."})
        if not isinstance(args.get("title"), str) or not args["title"].strip():
            errors.append({"argument": "title", "message": "Provide a nonempty event title."})
        clock = args.get("time") or args.get("start") or args.get("start_time")
        if not isinstance(clock, str):
            errors.append({"argument": "time", "message": "Provide a string containing both the event date and clock time."})
        else:
            from .sabench_study import APICall, write_operation_from_call
            normalized = write_operation_from_call(APICall("calendar", "create", args)).fields["time"]
            try:
                if "T" not in normalized:
                    raise ValueError("Missing date or time")
                datetime.fromisoformat(normalized)
            except (ValueError, TypeError):
                errors.append({"argument": "time", "message":
                    "Provide a complete date and clock time, for example 2026-04-22T10:00:00. A clock alone does not specify an event date."})
        duration = args.get("duration", args.get("duration_minutes", 30))
        if type(duration) is not int or duration <= 0:
            errors.append({"argument": "duration", "message": "Duration must be a positive integer."})
        if "attendees" in args:
            attendees = args["attendees"]
            if not isinstance(attendees, list):
                errors.append({"argument": "attendees", "message": "Use a native array of attendee strings."})
            elif attendees:
                errors.extend(_recipient_errors(attendees, "attendees"))
    return errors


def clarify_office_definitions(definitions):
    """Describe the existing representations without changing permissions."""
    result = deepcopy(definitions)
    for definition in result:
        name = definition["name"]
        props = definition["parameters"]["properties"]
        if name in {"email_send", "email_forward"}:
            props["to"]["description"] = (
                'One literal recipient string or a native array of strings. For example, '
                '"person@example.com" or ["person@example.com"]. Do not pass a JSON-encoded array as a string.')
        if name == "calendar_create":
            props["time"]["description"] = (
                "The complete event date and clock time in one string. Do not supply the date separately in fields. "
                "Yearless dates follow the runtime's default year of 2026.")
            props["fields"]["description"] = "Not used by calendar_create; put creation arguments at the top level."
        if name in {"email_send", "email_forward", "calendar_create"}:
            definition["description"] += " Malformed arguments return an error without changing the workspace; correct them before retrying."
    return result


def execute_office_tool(name, args, state, step, *, validate=False):
    from .sabench_study import APICall, runtime
    errors = validate_office_arguments(name, args) if validate else []
    if errors:
        tool, action = runtime.split_api_name(name)
        return (APICall(tool, action, deepcopy(args), success=False, step=step),
                {"success": False, "committed": False, "error": "invalid_arguments", "argument_errors": errors},
                state)
    return runtime.execute_tool_call(name, args, state, step)
