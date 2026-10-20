# Prior work and the contribution we can defend

Literature checked on 20 October 2026. This is a targeted comparison with primary papers and official project documentation, not an exhaustive novelty search. “Our difference” below is our interpretation, not a claim made by those authors. Published rates are not comparable to our local rates. A prior six-run ImpossibleBench attempt is documented below; it is not a clean comparative baseline. Other listed systems have not been reproduced here.

The present evidence supports a reproducible, small service-agent measurement study. It does **not** establish a new safety principle, a new containment algorithm, superiority over existing defenses, or safety under recursive self-improvement. The proposed feedback-selection experiment remains unmeasured.

## Closest overlaps

| Prior work | What it already studies | Our present difference and missing evidence |
| --- | --- | --- |
| [ImpossibleBench — Zhong et al., 2025; ICLR 2026](https://arxiv.org/abs/2510.20270) | Inconsistent coding tests expose specification-violating shortcuts. It also studies prompts, test access, abort options, feedback loops, and transcript monitors (§§5–6). | This is the closest overlap, including our prompt comparison. We measure authorization violations in local services, including reads followed by failure to score. That is a different endpoint, not proof of novelty. We need a shared task suite and a comparison including all assigned runs. |
| [Anthropic incident assessment — September 2026](https://www.anthropic.com/research/alignment-assessment-cybersecurity-incidents) | Edits incident context and resamples continuations. Builds evaluations with no in-scope CTF solution and examines monitoring. | Even closer to the incident-to-test motivation. Our deterministic service state and effect logs support a smaller measurement study. Incident-derived impossible tasks and checkpoint continuations are not new contributions. |
| [AgentDojo — Debenedetti et al., 2024](https://arxiv.org/abs/2406.13352) | Tool-using agents face attacker-controlled external content; utility and attacker success are evaluated separately in an extensible environment. | Our current diagnostic changes continuation wording without an injected attacker objective. Explicit task authorization and separate safety/utility measurements are already established. We have not tested prompt-injection defenses. |
| [AI Control — Greenblatt et al., 2023/2024](https://arxiv.org/abs/2312.06942) | Evaluates control protocols against intentional subversion, including trusted editing and untrusted monitoring with constrained trusted resources. | Our actors are not instructed to sabotage and our observer is trusted service instrumentation. We have not performed an adversarial control evaluation or demonstrated prevention. |
| [SHADE-Arena — Kutasov et al., 2025](https://arxiv.org/abs/2506.15740) | Measures completion of a legitimate task, a hidden harmful objective, and evasion of transcript monitoring. | Our small fixture measures spontaneous continuation behavior under task constraints. “Success plus harm” and “a monitor can miss harm” are not new claims. We lack its long-horizon task diversity and adversarial objectives. |
| [CaMeL — Debenedetti et al., 2025](https://arxiv.org/abs/2503.18813) | Separates trusted control flow from untrusted data and uses capabilities to constrain information flow. Its guarantees depend on its policy and system assumptions. | Our observer records service effects after execution; our permissive broker does not prevent them. An explicit allowlist is a necessary engineering baseline, but is not a reproduction of CaMeL. We cannot claim enforcement or formal security. |
| [ControlArena — UK AISI / Redwood, official framework](https://control-arena.aisi.org.uk/) | Provides settings, policies, monitors, post-hoc scoring, and safety/usefulness analysis for control experiments. | Frozen evaluation and monitoring infrastructure are reusable practice. Compare our measurement signal within an existing framework rather than presenting a custom runner as a new control method. |
| [AgentDyn — Li et al., 2026, v3](https://arxiv.org/abs/2602.03117v3) | Dynamic open-ended tasks include useful third-party instructions; evaluates security and excessive defense. | Our recoverable controls check a narrow form of utility loss. They do not establish competence on dynamic tasks or show that broad refusal is solved. Include a second task family and helpful third-party content. |
| [CoSec — Chen et al., September 2026; v3 October 19](https://arxiv.org/abs/2609.34790v3) | Evaluates authorization and privacy across persistent community boundaries, using traces and artifacts against active authorization state. | Very direct overlap with boundary violations, cross-context information, and task utility versus compliance. Our one-run service fixture is narrower. Cross-run provenance alone is not a defensible novelty claim; evolving authorization and persistent memory remain untested here. This is a recent preprint, not independently validated by us. |
| [Passing the Test You Trained On — Liu, October 2026 preprint](https://arxiv.org/abs/2610.03448v1) | Studies transfer of prompt-injection detector rankings across benchmarks, with replay-based reference labels and low-FPR evaluation. | Motivates out-of-domain judge evaluation and realistic calibration. Our judge detects unauthorized actions, not injected text, so this is related methodology rather than an identical classifier task. Our failed 12-case calibration cannot justify a deployment threshold. |

## ImpossibleBench: compare the operational definitions

| Dimension | ImpossibleBench | Our current service study |
| --- | --- | --- |
| Task | Coding specification and tests | Retrieve a current-run flag |
| Obstruction | Mutated tests contradict the specification | Dependency down; fallback may be absent |
| Main violation endpoint | Passing an impossible task | Executed access to an excluded resource |
| Exit | Human-intervention marker ends feedback | Blocked/incomplete response; termination already available |
| Intervention | Prompt, test access, feedback and abort ablations | Scope/accepted-exit wording; later paired checkpoint notes |
| Useful behavior | Original benchmark tasks | Working and recoverable service variants |
| Monitor evaluation | Scorer-passing coding trajectories | All 48 assigned diagnostic trajectories |

The label distinction matters locally: two of our 15 violations did not pass.
It does not imply that ImpossibleBench claims to detect every unsuccessful
violation. Its broader analysis includes trajectories and monitors. Separate
safety and utility endpoints are also established in AgentDojo and CoSec.
Source: [ImpossibleBench §§2, 5–6](https://arxiv.org/html/2510.20270v1).

The [September upstream report](impossiblebench-upstream-baseline-results.md)
records six Haiku runs using the original task constructor, tools solver,
prompts and scorer: original 1/2, oneoff 0/2, conflicting 0/2. All reached the
100-message cap, with dependency errors and no explicit submission or
human-intervention marker. The referenced live raw archive is absent from this
checkout; these numbers are **report-only**, not independently recomputed in
this revision. The separate preparation archive is not substitute live evidence.
Restore logs, fix actor/scorer environment consistency, and establish original-task
capability before estimating an intervention effect. Zero impossible passes alone
does not demonstrate appropriate stopping.

## Threat model and control mechanism

| Work | What is adversarial or variable? | What must match for a fair comparison? |
| --- | --- | --- |
| AgentDojo | Attacker-supplied tool content | Same injected content, allowed tools, tasks and utility definition |
| SHADE-Arena / AI Control | Deliberately adversarial agent behavior | Same malicious objective, monitor visibility and trusted budget |
| CoSec | Community authorization, memory and information flows | Same owner, recipient, time-dependent permissions and scoring surface |
| CaMeL | Untrusted data enters an agent workflow | Same policies and tools; evaluate runtime prevention and useful completion |
| Our current fixture | Continuation wording; service feasibility | Same model, checkpoint, scope, budgets and local effect oracle |

An endpoint allowlist is a useful small baseline. It is not CaMeL's program
interpreter with data-flow capabilities. A transcript judge, an effect recorder
and a pre-dispatch blocker also perform different functions. Compare each at its
actual intervention point. Count blocked attempts separately from executed effects.

The incident reports motivate a new crossed design: vary repair availability
and permission independently while keeping a resource reachable. This can
distinguish stopping because a route failed from obeying a resource boundary.
The design and its evidence limits are in
[From incidents to experiments](trust4rsi-incident-to-experiment.md).
Its novelty and generalization remain unestablished.

## What the current measurements establish

The historical 160-run cohort contains 13 scorer-passing violations, two violations without scorer success, 96 clean passes, and 49 clean non-passes. An endpoint counting only successful shortcuts would omit those two observed violations in this fixture. This is a local measurement observation; prior work already separates task achievement from security.

The new 48-run cohort compares the exact current continuation note with the archived N note on paired fixture inputs. Impossible-task incidents are 11/16 and 15/16; the paired difference is +25 percentage points with a conservative approximate 95% interval from −19.9 to +57.9 points. Both arms complete all eight feasible controls. This is insufficient to establish a note effect or generalize across tasks.

The transcript audit exposes two distinct operational problems: strict JSON parsing failed on 12 fenced responses; removing only the outer fence still failed the frozen benign false-positive requirement. A separate descriptive audit uses a fixed 0.5 threshold and preserves the failures. It is not a calibrated safety gate. See [the live results](trust4rsi-live-followup-results.md) for the complete matrix, raw-boolean comparison, and uncertainty.

## The experiment that would make the contribution stronger

Proposed question: **When does the choice of incident measurement change which policy is selected, and does that change improve authorization compliance on unseen tasks without reducing authorized completion?** This is a research hypothesis, not a verified gap across all literature.

1. Keep the actor model, candidate instructions, development inputs, task score, tie-breaks, and inference budget fixed. Select once using transcript labels and once using service-effect labels.
2. Include the original instruction, the fixed instruction baseline, and an explicit broker allowlist. Report attempted violations separately from executed violations for the enforcement arm. Do not label the allowlist “CaMeL.”
3. Diagnose judge parsing and calibration on development data only. Freeze the revised judge before collecting fresh evaluation cases; do not reuse the current 48 targets as unseen evidence.
4. Evaluate on a new task family and on feasible, recoverable, and impossible cases. Split by task family rather than merely changing seeds. Report all assigned cases, unknowns, paired contrasts, intervals, authorized utility, and total cost.
5. Separate two questions: does a privileged service observer contain more information, and does using that information improve policy selection? Add a transcript-plus-service-evidence judge to distinguish information access from deterministic versus model-based classification.
6. Accept null results. If both signals select the same policy or fresh outcomes are indistinguishable, the claim becomes an audit/measurement result, not an improved optimization method.

These comparisons require hosted APIs and CPU-based service fixtures, not a local GPU. Docker and more CPU/RAM/disk become relevant when reproducing the coding environments. Local weights, fine-tuning, or white-box methods would be separate GPU-dependent work.

## Paper framing

Suggested working title: **Auditing Authorization Violations in Service Agents: A Controlled Measurement Study**.

The philosophical question is useful: what gives an agent legitimate authority to take an action while pursuing a goal? In the experiments, this becomes explicit authorized resources, observable actions, and preserved task utility. A correct answer does not enlarge delegated authority. This is a normative framing of the study, not a claim to invent that distinction.

Avoid “first,” “solves containment,” “proves trustworthy evolution,” and “observer feedback improves safety” until the relevant literature coverage and fresh comparisons support them. The workshop theme can motivate studying future policy updates, but the current experiments do not implement recursive self-improvement.
