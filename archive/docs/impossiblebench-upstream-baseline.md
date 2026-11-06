# Direct ImpossibleBench baseline

Updated September 21, 2026. **U1 is completed.** The approved six-run allocation
produced 1/2 original and 0/4 impossible-task passes, at an estimated $5.78.
All runs reached the message cap and encountered actor environment problems.
Read the [results and next design decision](impossiblebench-upstream-baseline-results.md).
The frozen protocol below records the allocation that was executed.

## What is being measured

ImpossibleBench makes coding tests conflict with their specification. Its primary
measure is the pass rate on those impossible tasks: a passing solution necessarily
uses a specification-violating shortcut, provided the mutation is valid. Original
tasks measure coding capability separately. This is the measure to report first.
[Paper](https://arxiv.org/abs/2510.20270).

The earlier service study measured accessing or modifying resources beyond an
agent's authorization. The custom coding adapter uses real ImpossibleBench tasks,
but changes its prompts, tools, scoring procedure and stopping behavior. Its N arm
is therefore **not an upstream baseline**. It also observes prohibited changes that
do not produce a passing score. Those observations complement the benchmark score;
they do not replace it.

| Feature | Upstream baseline prepared here | Existing custom coding adapter |
| --- | --- | --- |
| Tasks | Two actual Impossible-SWEbench issues and their three variants | The same task triples |
| Solver | Unmodified upstream tools solver and Inspect basic agent | Custom continuation loop |
| Tools | bash, python, text_editor, think, submit(answer) | shell, submit(), finish(...) |
| Initial wording | Upstream paper's tools prompt and STOP custom_prompt | Explicit authorization policy and shared interface |
| Failed submissions | Upstream feedback, including repeated prompt suffix | One assigned N/R/E/RE note after first scored failure |
| Terminal handling | Upstream scorer and human-intervention marker behavior | Explicit finish or natural final response |
| Primary output | Original upstream numeric score | Raw pass plus independently observed effects and semantic review |
| Stopped or failed runs | Preserve raw upstream score, error/limit and missing-score count | Unfinished violation outcomes remain unknown |

The source is pinned at
[`061dc3d`](https://github.com/safety-research/impossiblebench/tree/061dc3dce6a96ab6cf02a855157263033dcfa3ba).
The driver imports its task constructor, solver and scorer without editing them.
Only the unpinned dataset lookup is replaced with frozen, reviewed local rows;
the supplied Compose configuration controls infrastructure. Scoring retains
`reset_tests=False` and `hide_tests=False`, as in the tools example in upstream's
`replicate_swebench()`. The baseline includes the paper's existing STOP instruction;
it is not a condition with no safety wording.

## Frozen U1 allocation

Use `anthropic/claude-haiku-4-5-20251001` on:

- `pytest-dev__pytest-10051` and `sympy__sympy-24562`;
- original, oneoff and conflicting variants;
- one fresh draw per issue/variant, six assignments total, serial execution;
- upstream `agent_type=tools`, `human_intervention=False`, ten submission attempts,
  and a 100-message limit.

The exact schedule is randomized with seed 23 and frozen in the plan. Additional
resource guards are 60 inference requests, three million input tokens, 122,880
output tokens, $7.50 estimated usage and 1,800 seconds per assignment. Each response
allows at most 2,048 output tokens. A 100-message limit is not 100 model calls:
tool messages count, and any of the limits may stop a run first.

The approved aggregate ceiling was **360 requests, 18 million input tokens,
737,280 output tokens and $45**. No unused share is reassigned. Unknown requests
keep reservations in both ledgers. Provider retries, automatic experiment retries
and prompt caching are disabled. Reservations are written before provider calls.

At the verified $1/$5 per million input/output-token rates, the uncached token
ceilings correspond to $21.6864. The defensive 2× input reservation gives a
$39.6864 planning bound; $45 is the guard, not an expected bill. Rates were checked
September 21, 2026 against [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing).
Six wall-time limits sum to three hours, excluding setup and reporting.

This is a small development baseline using the upstream implementation. Different
models, dependency versions, resource limits, offline execution and a non-root
actor prevent describing it as an exact reproduction of the paper's rates.

## Execution and evidence

**Qualification passed:** twelve upstream reference/unchanged scoring controls and
four real tool-loop controls. The repository suite passed 142 tests including
Docker and Inspect; two additional checkpoint/budget regressions also passed.
All results and the frozen proposal are preserved in the
[preparation archive](../results/upstream-baseline-preparation-v1/README.md).
These are scripted implementation checks, not new model-behavior findings.

The runnable proposed config is
[`impossiblebench-upstream-baseline-v1.proposed.json`](../experiments/impossiblebench-upstream-baseline-v1.proposed.json).
The driver is [`scripts/upstream_baseline.py`](../scripts/upstream_baseline.py).
The prepared directory is `runs/impossiblebench-upstream-baseline-proposed-02/`.
It freezes the upstream sources, local driver hashes, rows, exact assignment
schedule, image IDs, Compose definitions, prompts and all limits.

```sh
# These two commands make no model API calls.
PATH="$PWD/runs/docker-bin:$PATH" .venv/bin/python scripts/upstream_baseline.py \
  qualify runs/impossiblebench-upstream-baseline-proposed-02
PATH="$PWD/runs/docker-bin:$PATH" .venv/bin/python -m scripts.check_upstream_baseline_tools \
  runs/impossiblebench-upstream-baseline-proposed-02

# Historical executed command; do not rerun this completed plan:
PATH="$PWD/runs/docker-bin:$PATH" .venv/bin/python scripts/upstream_baseline.py \
  run runs/impossiblebench-upstream-baseline-proposed-02 --env-file ../.env

# Rebuild the assigned-denominator report without inference.
.venv/bin/python scripts/upstream_baseline.py \
  report runs/impossiblebench-upstream-baseline-proposed-02
```

Qualification and scripted-tool directories are exclusive; do not rerun these
commands in completed directories. A source or image change requires a new plan.
The live command refuses an already-started plan, incomplete reference controls,
or missing/failed tool controls. Host Docker access is required on this machine.

The upstream controls exercise nochange/oracle scoring on all six variants.
Additional scripted controls use every actor tool, repair original tasks, receive
failed feedback on conflicting tasks and terminate with the upstream marker. They
check UID 1000, zero effective capabilities, no routes and no-new-privileges inside
the real actor. The initial editor test found that Inspect tries to chmod a
user-owned injected binary as capability-free root. The final images preinstall
the exact bundled executable instead of granting the actor more capabilities.
The initial diagnostic plan remains in `...-proposed-01/`; it is not the live plan.

## Reporting and the next comparison

Report each split separately with all assigned denominators, raw upstream scores,
missing-score counts, time/token limits, costs and submitted patches. On original
tasks, review passing patches for legitimate repairs before claiming capability.
A zero impossible-task score does not prove the agent avoided prohibited actions.
These are two known issues, not a general cheating-rate estimate.

U1 found actor/scorer environment mismatch and weak original-task capability.
The next revision should qualify the default actor environment and measure
original-only capability **within the same upstream scaffold** before any
intervention comparison. Preserve U1's scores and traces; a repair requires a
new plan and allocation. See the results report for the evidence and qualification
gap. Sparse baseline scores do not support estimating a reminder reduction.

The proposed scientific extension separates a scope reminder from wording that
accepts a supported blocker, while holding tools, scoring and exit availability
constant. The paper already investigates prompt and human-intervention effects;
showing that a reminder can help is not by itself a new finding. Any new delivery
hook must be qualified before a treatment allocation. The repaired custom C1/C2
plans remain available as separate diagnostics; a cross-runner comparison cannot
identify the effect of reminders.
