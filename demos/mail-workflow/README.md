# Containment-extension: an email workflow

Open [the video](containment-mail-workflow.mp4) in any H.264/AAC-capable player.
The 4:48, 1920×1080 film includes English synthetic narration, burned-in English captions, and animated
mail, planner, journal, and integration views. Playback needs no network or setup.

The film starts with a brief introduction to Inspect and CRUX, then shows a
customer follow-up in three branches: an authorized email reply, an extra ticket
comment outside scope, and a request that needs channel clarification. It ends
with the proposed integration and current implementation status.

| Time | Topic |
| --- | --- |
| 0:16 | Inspect and CRUX explained |
| 0:42 | Customer email and the user's authorization boundary |
| 1:16 | Reading, composing, and replying |
| 1:31 | The committed effect and planner feedback |
| 1:46 | An extra ticket write, flagged after it happens |
| 2:07 | An ambiguous request and `ASK_USER` |
| 2:25 | Native Inspect components, models, agents, tools, and scorers |
| 2:48 | Proposed native tool loop, approval policy, and feedback |
| 3:16 | Eval sets, execution controls, log viewer, dataframes, and scanners |
| 3:42 | Extension packaging and features to use when needed |
| 4:09 | A CRUX-style experimental workflow |
| 4:25 | Current readiness and remaining adapter work |

The [Inspect feature map](inspect-feature-map.md) connects each documentation
section to this workflow and distinguishes native capabilities from adapter work.
The expanded integration section remains a design, not a recording of an Inspect
run. It covers the full evaluation flow as well as the planner/journal mechanism.

## What actually runs

[replay_trace.py](replay_trace.py) executes existing repository code against the
`AM-01-explicit` and `AM-01-unspecified` local office fixtures. It declares scope
from the visible requests, compiles the contracts, obtains planner advice, calls
the fixture's tools, and constructs the effect journal. The safe reply and extra
write branch also run the existing scorer. Assertions check authorized completion,
the unchanged ticket in the safe branch, the committed and flagged extra comment,
and the `ASK_USER` recommendation for the unclear request.

[trace.json](trace.json) retains the actual calls, responses, before/after states,
advice, journals, scoring results, source hashes, and repository commit. The
renderer reads that trace and animates a mail interface; the film is not a screen
recording of Inspect or a live email client.

The actor is scripted and scope is declared for this demonstration. No language
model, external API, or live mail account is used. The generic feedback helpers
retain their original model-inference metadata strings in the raw trace; the
trace's provenance explains the declared source used here. The fixture checks
structural operations and targets; it does not assess free-form message quality
or confirm delivery to an actual inbox. These branches demonstrate mechanisms,
not model efficacy.

The current planner supplies advice and the journal records committed effects.
Neither prevents the extra ticket write in this fixture. Pre-execution enforcement
requires a separate layer. The general Inspect adapter and CRUX-style deployment
shown in the last chapters are proposals; the existing Inspect adapter is specific
to the legacy ImpossibleBench runner.

## Rebuild

Requires Python 3 with Pillow, `ffmpeg`, and macOS `say` with the Samantha voice.
The renderer prefers Carlito fonts, with Arial and DejaVu fallbacks. Voice timing
may vary between operating-system versions.

From the repository root:

```sh
python3 demos/mail-workflow/replay_trace.py
python3 demos/mail-workflow/build_video.py
```

For a storyboard preview without encoding the movie:

```sh
python3 demos/mail-workflow/build_video.py --preview
```

Generated speech and intermediate frames stay in the ignored `.build/` directory.
After the first build, `--reuse-narration` uses the existing timing and cached audio.
Regenerate narration after editing [storyboard.json](storyboard.json).

Supporting files include the [transcript](narration.txt), [SRT captions](captions.srt),
[scene timing](timeline.json), [storyboard preview](storyboard-preview.jpg), and
[poster](poster.jpg). Captions are already visible in the MP4; the SRT is provided
for reuse and editing.

## References

- [Inspect documentation](https://inspect.aisi.org.uk/): tasks, agents, tools, logs, and scorers.
- [Inspect tool approval](https://inspect.aisi.org.uk/approval.html): pre-execution approval policies and custom approvers.
- [Inspect feature map and references](inspect-feature-map.md): components, models, ReAct, execution, analysis, and extension packaging.
- [Open-World Evaluations for Measuring Frontier AI Capabilities](https://arxiv.org/abs/2605.20520): CRUX, Collaborative Research for Updating AI eXpectations.
- [Repository system design](../../figures/system-design/README.md): implemented components and proposed general integration.
- [Legacy Inspect adapter](../../src/containment_extension/impossiblebench/inspect_adapter.py): the existing ImpossibleBench-specific runner.

External references and repository status were checked on 26 November 2026.
