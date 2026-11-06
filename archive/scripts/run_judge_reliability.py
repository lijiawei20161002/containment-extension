"""Prepare, run, resume, analyze or inspect the judge reliability study.

`archived` scores the single-draw labels the 2026-10-31 cohorts already saved and
makes no model calls. `prepare` freezes a plan; `run` performs only judge draws
under the frozen allocation; `analyze` recomputes metrics from saved draws.
"""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from containment_extension.judge_reliability import (  # noqa: E402
    analyze, archived_labels, execute, human_report, prepare,
)
from containment_extension.config import load_env  # noqa: E402

ARCHIVED_COHORTS = [
    "runs/decision-algorithms-v2-haiku-4-5-20261031",
    "runs/decision-algorithms-v2-haiku-5-5-20261031",
    "runs/decision-algorithms-v2-sonnet-4-6-20261031",
    "runs/decision-algorithms-v2-sonnet-5-20261031",
    "runs/eval-awareness-v1-haiku-4-5-20261031",
    "runs/eval-awareness-v1-sonnet-5-20261031",
]


def archived_markdown(table):
    lines = ["# Archived single-draw judge labels (2026-10-31 cohorts)", "",
             "No new inference. Calibration failures list every scripted case the saved label got wrong, "
             "with the saved reason text. Development agreement uses the labels each cohort actually produced; "
             "the transcript-only view produced none because it failed its gate.", "",
             "| Cohort | Model | Gate: transcript | Gate: transcript+journal | Transcript failures | Journal-view dev agreement |",
             "| --- | --- | --- | --- | --- | ---: |"]
    for cohort, e in table.items():
        if "model" not in e:
            lines.append(f"| {Path(cohort).name} | – | – | – | {e['status']} | – |")
            continue
        fails = ", ".join(f"{f['id']} ({'granted' if f['granted_in_task'] else 'ungranted'}; {'+'.join(f['operations'])})"
                          for f in e["calibration_failures"]["transcript"]) or "none"
        dev = e["development"].get("transcript_journal")
        dev_text = "–" if not dev else f"{dev['agree']}/{dev['decided']} ({dev['false_alarm']} FA, {dev['miss']} miss)"
        lines.append(f"| {Path(cohort).name} | {e['model']} | {'pass' if e['calibration_passed']['transcript'] else 'fail'} | "
                     f"{'pass' if e['calibration_passed']['transcript_journal'] else 'fail'} | {fails} | {dev_text} |")
    lines += ["", "## Saved reasons on failed transcript cases", ""]
    for cohort, e in table.items():
        for f in e.get("calibration_failures", {}).get("transcript", []):
            lines.append(f"- {Path(cohort).name} / {f['id']} (truth {f['truth']}, label {f['label']}): {f['reason']}")
    lines.append("")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("prepare", "run", "status", "analyze", "archived"))
    p.add_argument("--output", type=Path)
    p.add_argument("--config", type=Path)
    p.add_argument("--env-file", type=Path)
    p.add_argument("--ca-file", type=Path)
    args = p.parse_args()
    if args.command == "archived":
        out = Path(args.output or ROOT / "results/judge-reliability-v1")
        out.mkdir(parents=True, exist_ok=True)
        table = archived_labels(ROOT, ARCHIVED_COHORTS)
        (out / "archived-labels.json").write_text(json.dumps(table, indent=2) + "\n")
        (out / "archived-labels.md").write_text(archived_markdown(table))
        result = {"written": str(out), "cohorts": len(table)}
    elif args.command == "prepare":
        result = prepare(args.output, args.config)
    elif args.command == "status":
        result = {name: json.loads((args.output / name).read_text())
                  for name in ("worker.json", "progress.json", "budget.json") if (args.output / name).exists()}
    elif args.command == "analyze":
        report = analyze(args.output)
        saved = args.output / "report.json"
        previous = json.loads(saved.read_text()) if saved.exists() else {}
        report.update({k: previous.get(k) for k in ("status", "error", "budget")})
        if report["budget"] is None:
            report["budget"] = json.loads((args.output / "budget.json").read_text())
        (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        human_report(args.output, report)
        result = {"analyzed": str(args.output), "judged_items": report["judged_items"]}
    else:
        load_env(args.env_file)
        if args.ca_file:
            os.environ["SSL_CERT_FILE"] = str(args.ca_file.resolve())
        result = execute(args.output)
        result = {k: result[k] for k in ("status", "error", "judged_items", "planned_items", "budget")}
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
