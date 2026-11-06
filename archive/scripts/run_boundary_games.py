"""Prepare, run, resume, inspect or demo the boundary games (courier, kitchen, habitat).

`demo` plays scripted action sequences through each game with no model calls and prints
the renders, task text and journal so the mechanics can be checked by eye.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from containment_extension.boundary_games import GAME_CLASSES, execute, make_game, prepare  # noqa: E402
from containment_extension.config import load_env  # noqa: E402
from containment_extension.grant_model import Utility  # noqa: E402

DEMOS = {
    "courier": [("look", ""), ("move", "quad"), ("move", "main_corridor"), ("check_notices", ""),
                ("request_badge", "lab_wing"), ("move", "fire_door"), ("deliver", "P1"), ("move", "fire_door"),
                ("move", "library"), ("deliver", "P3"), ("report_undeliverable", "P2"), ("end_shift", "done")],
    "kitchen": [("status", ""), ("cook", "O3"), ("cook", "O2"), ("ask_manager", "O2"), ("use_storeroom", "O2"),
                ("use_storeroom", "O1"), ("close_service", "")],
    "habitat": [("status", ""), ("inventory", ""), ("try_repair", "S3"), ("try_repair", "S1"),
                ("request_override", "lab_2"), ("open_hatch", "lab_2"), ("declare_unrepairable", "S2"), ("declare_status", "")],
}


def demo(game_name, available, grant, decoy):
    cls = GAME_CLASSES[game_name]
    env = {"game": game_name, "available": available, "grants": {z: grant for z in cls.zones}, "decoy": decoy, "seed": 0}
    with tempfile.TemporaryDirectory() as tmp:
        game = make_game(tmp, env, Utility())
        print("=" * 100)
        print(game.task_text())
        print("-" * 100)
        for verb, target in DEMOS[game_name]:
            obs = game.request(verb, target)
            print(f"> {verb} {target}".rstrip())
            print("  " + json.dumps({k: v for k, v in obs.items() if k not in ("items",)})[:400])
            if game.finished:
                break
        print(game.render())
        print(json.dumps({k: v for k, v in game.outcome(True).items() if k != "journal"}))
        print("advice at end:", json.dumps(game.advice()["recommended_action"]))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("prepare", "run", "status", "demo"))
    p.add_argument("--output", type=Path)
    p.add_argument("--config", type=Path, default=ROOT / "experiments/boundary-games-v1-haiku-4-5.json")
    p.add_argument("--env-file", type=Path)
    p.add_argument("--ca-file", type=Path)
    p.add_argument("--game", choices=list(GAME_CLASSES), default=None)
    p.add_argument("--available", action="store_true")
    p.add_argument("--grant", action="store_true")
    p.add_argument("--decoy", action="store_true")
    args = p.parse_args()
    if args.command == "demo":
        for name in ([args.game] if args.game else list(GAME_CLASSES)):
            demo(name, args.available, args.grant, args.decoy)
        return
    if args.command == "prepare":
        result = prepare(args.output, args.config)
    elif args.command == "status":
        result = {name: json.loads((args.output / name).read_text())
                  for name in ("worker.json", "progress.json", "budget.json") if (args.output / name).exists()}
    else:
        load_env(args.env_file)
        if args.ca_file:
            os.environ["SSL_CERT_FILE"] = str(args.ca_file.resolve())
        report = execute(args.output)
        result = {k: report[k] for k in ("status", "error", "completed", "assigned", "budget")}
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
