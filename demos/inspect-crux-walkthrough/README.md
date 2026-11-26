# Inspect × CRUX coding walkthrough

Open [index.html](index.html) directly in a browser, or watch the
[English coding video](inspect-crux-coding-walkthrough.mp4) (7 minutes 10 seconds,
1080p, English narration and visible English captions). Both are new teaching
artifacts; the earlier [mail workflow replay](../mail-workflow/README.md) remains
available separately.

Inspect is the evaluation framework used in the proposed integration. CRUX
(Collaborative Research for Updating AI eXpectations) is an open-world evaluation
project and research approach. The tutorial shows how Inspect could execute a
CRUX-style study; its protocol and intervention schemas are our suggested
design, not an official CRUX SDK or schema.

## Use the interactive tutorial

- Choose a chapter, then click **Write next step** or **Play walkthrough** to
  reveal the code. **Alt + Left/Right** also moves between steps.
- Click a code line to read its explanation. **Show full code** reveals the
  complete sketch; **Restart chapter** returns to its first explanation.
- Drag the divider between code and explanation on a wide screen, or focus it
  and use the arrow keys. Narrow screens stack the panels.
- Compare advisory feedback, enforcement and human clarification in the small
  browser illustration. Its outcomes are simulated, not evaluation results.
- Use **Copy sketch** or **Download notes + sketches** to take the code,
  explanations, implementation checklist and official references with you.

The HTML is a self-contained file with inline styles, code and curriculum. It
works offline without a server, installation or account. Documentation links
need internet access when opened. Checklist state lasts for the current page
session. The MP4 is a separate portable file and does not require the HTML.

## What the code means

The 14 chapters contain 42 explained steps. Purple names mark Inspect API
patterns; `ce.*` marks helpers the reader must implement. Other locally defined
functions are introduced in the relevant chapters. All snippets are teaching
sketches, including the proposed package registry. They are not executed by
either artifact and are not a ready-to-run adapter.

The walkthrough covers tasks and datasets, setup solvers, sample state, custom
tools and receipts, ReAct continuation, approval, scoring, model configuration,
evaluation sets, log analysis, extension registration and optional capabilities.
Three CRUX chapters cover a research brief, trusted human interventions and
scope versions, and case execution with evidence export. The final chapter gives
an implementation order.

No model was called, email sent, evaluation environment installed, or real
evaluation run to create this tutorial. Browser checks validate the presentation,
not containment efficacy. Before implementing the sketches, pin Inspect and
check its official APIs against that version. The source links were reviewed on
26 November 2026.

## Video chapters

| Time | Chapter |
| --- | --- |
| 00:00 | Start with a task and a sample |
| 00:27 | Prepare scope before the first decision |
| 00:58 | Bind a tool to an observable effect |
| 01:27 | Let ReAct run the agent loop |
| 01:56 | Choose advice or enforcement explicitly |
| 02:27 | Score the record, including unknowns |
| 02:57 | Configure models and a comparison run |
| 03:28 | Make the trajectory inspectable |
| 03:58 | Package the adapter for reuse |
| 04:26 | Add features when the task needs them |
| 04:59 | Write the CRUX-style research brief |
| 05:30 | Record interventions and scope changes |
| 06:02 | Execute the case and export evidence |
| 06:37 | Turn the sketches into a working adapter |

The video animates instructional code and narrates its design. It is not an IDE
recording or evidence of a completed integration. The HTML provides longer
explanations and per-chapter implementation steps.

## Files and rebuilding

| File | Purpose |
| --- | --- |
| [index.html](index.html) | Portable interactive tutorial |
| [inspect-crux-coding-walkthrough.mp4](inspect-crux-coding-walkthrough.mp4) | Narrated code animation |
| [coding-notes.txt](coding-notes.txt) | Full code, explanations and implementation steps |
| [content.py](content.py) | Shared curriculum used by both builders |
| [index.template.html](index.template.html) | HTML, styles and browser controls |
| [build_html.py](build_html.py) | Builds the self-contained HTML and text notes |
| [build_video.py](build_video.py) | Renders code frames and synthesizes narration |
| [captions.srt](captions.srt) | English subtitle track |
| [narration.txt](narration.txt) | English narration transcript |
| [video-timeline.json](video-timeline.json) | Chapter and step timing |
| [storyboard-preview.jpg](storyboard-preview.jpg) | Contact sheet of the video chapters |

From the repository root, rebuild the HTML with standard Python:

```sh
python3 demos/inspect-crux-walkthrough/build_html.py
```

Rendering the video requires Pillow, FFmpeg/ffprobe and macOS `say` with the
Samantha voice. It does not require Inspect or a model provider:

```sh
python3 demos/inspect-crux-walkthrough/build_video.py --preview
python3 demos/inspect-crux-walkthrough/build_video.py --reuse-narration
```

The first command synthesizes narration and checks all 42 frame layouts. The
second reuses that narration and renders the MP4. After changing `content.py`,
run without `--reuse-narration` to refresh the timeline; unchanged speech is
cached by content hash in ignored `.build/` files.

## Primary references

- [Inspect documentation](https://inspect.aisi.org.uk/)
- [ReAct continuation](https://inspect.aisi.org.uk/react-agent.html#continuation)
- [Custom approval](https://inspect.aisi.org.uk/extensions-approvers.html)
- [Packaged components](https://inspect.aisi.org.uk/extensions-components.html)
- [CRUX and open-world evaluations](https://arxiv.org/abs/2605.20520)

Each HTML chapter and the downloadable notes also link to the relevant source.
