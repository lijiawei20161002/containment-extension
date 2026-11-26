#!/usr/bin/env python3
"""Build a single offline HTML. Does not execute any teaching snippets."""
import json
from pathlib import Path
from content import LESSONS

HERE = Path(__file__).resolve().parent


def main():
    for lesson in LESSONS:
        lines = lesson["code"].splitlines()
        for step in lesson["steps"]:
            assert 1 <= step["lines"][0] <= step["lines"][1] <= len(lines), lesson["id"]
        assert len(lesson["steps"]) == 3
    data = json.dumps(LESSONS, ensure_ascii=False).replace("</", "<\\/")
    template = (HERE / "index.template.html").read_text()
    assert template.count("__CURRICULUM__") == 1
    (HERE / "index.html").write_text(template.replace("__CURRICULUM__", data))
    notes = ["INSPECT × CRUX — CODING WALKTHROUGH", "Teaching pseudocode. ce.* helpers are adapter work to implement. No evaluations were run."]
    for index, lesson in enumerate(LESSONS, 1):
        notes += ["\n" + "=" * 72, f"{index:02}. {lesson['title']}", lesson["summary"], "\n" + lesson["file"], lesson["code"]]
        for step in lesson["steps"]:
            notes += [f"\n{step['title']} (lines {step['lines'][0]}–{step['lines'][1]})", step["explanation"]]
        notes += ["\nIMPLEMENT NEXT"] + ["[ ] " + x for x in lesson["todo"]]
        notes += ["\nREFERENCES"] + [s["label"] + ": " + s["url"] for s in lesson["sources"]]
    (HERE / "coding-notes.txt").write_text("\n\n".join(notes) + "\n")
    print(f"Built {len(LESSONS)} chapters, {sum(len(l['steps']) for l in LESSONS)} steps, {(HERE/'index.html').stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
