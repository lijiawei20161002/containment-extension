# System-design figures

Line-art figures for the planned step from per-study simulations to one agent
harness and evaluation framework. They follow the layout of Figures 1 and 2 of
the FlashRT paper (arXiv:2607.18171): a before/after teaser, then an example
input, the plain agent, and the harness workflow. Figure 3 adds the evaluation
framework, which has no counterpart in that paper. Figures 4 and 5 show how the
design fits Inspect and a CRUX-style open-world evaluation.

These are design drawings. Nothing here is a measured result, and the harness
drawn in Figures 1, 2c and 3 to 5 does not exist yet as one component.

| File | Shows |
| --- | --- |
| `fig1-before-after` | Hand-written guardrails per application, against one harness that takes plain task requests |
| `fig2a-example-input` | A task with its stated scope and an unmodified agent loop |
| `fig2b-plain-agent` | The two decisions the plain agent leaves open |
| `fig2c-harness-workflow` | Scope contract and Grant Look-ahead, then the journaled action loop, then the permitted outcomes |
| `fig3-evaluation-framework` | Incident library and frozen plan, one control layer over simulated or real backends, replay oracle and reported measures |
| `fig4-inspect-integration` | Each harness component on the Inspect extension point it would use |
| `fig5-crux-open-world` | A CRUX-style open-world run: dry run, live run, and the harness artifact behind each CRUX recommendation |

Each figure comes as `.svg` (editable), `.pdf` (vector, for LaTeX) and `.png`
(300 dpi). `preview.png` shows all of them with draft captions; the captions
are also in `metadata.json`.

## Rebuild

```sh
python3 scripts/draw_system_design_figures.py
```

The script needs Google Chrome (prints the PDFs) and `pdftocairo`. The harness
label "Containment harness" is a working name: change `HARNESS_NAME` at the top
of the script and rebuild.

## What exists and what is planned

| Drawn element | In the repository today | Planned |
| --- | --- | --- |
| Scope contract | Stated scope with `incident_fixture.semantic_label`; inferred and reviewed contracts in `sabench_study.infer_scope`; argument checks in `verified_planner.compile_office_contract` | One contract format for every backend |
| Grant Look-ahead | `grant_model.lookahead`, `native_algorithms.FeedbackLab.advice`, `sabench_study.planning_advice` | Unchanged algorithm behind the gateway |
| Effect Journal | `GrantLab.journal`, `FeedbackLab.journal`, `sabench_study.effect_journal` | Journal fed by real tool effects |
| Trusted approver | Authorization route with a precommitted reply (`native_algorithms.ASK_URL`) | A human or policy approver |
| Tool gateway | Each fixture's own `request` method; `Lab` mode `scoped` is the broker | One gateway in front of every tool |
| Agent adapter | `providers.NativeAgent` | Adapters for external agent frameworks |
| Simulated backends | `GrantLab`, `RecoveryLab`, the SABench office workspace | Kept as regression fixtures |
| Real tool backends | None | Sandboxed shell, HTTP egress, MCP servers |
| Replay and incident oracle | `incident_study.score_outcomes`, `sabench_study.score` and the replay reports | Same oracle over recorded real effects |
| Reported measures | First and repeat incidents, authorized completion, unknown outcomes | Advice-following score (see the roadmap) |
| Incident library to task families | The library motivates hand-written tasks | A recorded link from each task family to its incident records |

Figure 2a is condensed from `prompts.TASK_PROMPT` and the loop in
`experiment.run_live`; the `Task(...)` form is the proposed input format.

## Integration with Inspect (Figure 4)

Checked against the Inspect documentation on 24 November 2026. The repository
already runs one frozen schedule inside Inspect
(`impossiblebench/inspect_adapter.py`); nothing below is built yet.

| Harness component | Inspect extension point | Limit to design around |
| --- | --- | --- |
| Frozen plan | `Task(dataset=...)`, a task parameter for the arm, `--model` | None |
| Scope compiler | A `@solver` that runs before the agent and writes the contract to `store_as(...)` | None |
| Grant Look-ahead and journal text | `react(on_continue=...)`: a returned string is appended as a user message. For Claude Code or Codex CLI, the `filter=` function of `sandbox_agent_bridge` | An approver cannot add text to a tool result, so feedback arrives between turns |
| Grant gateway | An `@approver` in an `ApprovalPolicy`: `approve` in advice mode, `reject` in broker mode, `escalate` for a request | For a bridged agent a rejection discards every call in that model response |
| Trusted approver | `human_approver`, next in the approval chain | It offers approve, reject and terminate, not modify |
| Effect record | A service in the sandbox that the agent cannot write to | Approval sees the proposed call, not what an approved command then does, and a bridged agent's transcript is its own account of its tool use |
| Replay oracle | A `@scorer` that reads the record with `sandbox().read_file` or `exec` | Keep unknown outcomes as their own value, as the existing adapter does |
| Tool backends | `sandbox=` (docker, k8s, proxmox and others) and local MCP servers | Remote MCP servers cannot pass through approval |

## Integration with CRUX (Figure 5)

CRUX (Collaborative Research for Updating AI eXpectations, arXiv:2605.20520) is
a method for open-world evaluations: long real-world tasks, few runs, analysed
qualitatively. It has no software interface, so integration means how a run is
conducted and reported. CRUX #1 ran an agent in a virtual machine with broad
permissions and no per-action authorization; the harness would add that layer.

| CRUX recommendation | Harness artifact | What it supplies |
| --- | --- | --- |
| Specify the construct | Scope contract | The grant written down beside the capability claim |
| Run dry runs first | Simulated backends | The same contract and gateway with no real side effects |
| Add real-time monitoring | Journal flags | Effects outside the grant flagged as they are committed |
| Document interventions | Ask and grant log | Every approver decision with its time and reason |
| Analyze and release logs | Effect record | A service-side record beside the agent's transcript |
| Report cost | Budget ledger (`budget.py`) | Tokens and spend per run |

## LaTeX

```latex
\begin{figure}[t]\centering
  \includegraphics[width=\columnwidth]{figures/system-design/fig1-before-after.pdf}
  \caption{...}
\end{figure}

\begin{figure*}[t]\centering
  \begin{subfigure}[b]{0.58\textwidth}\centering
    \includegraphics[width=\linewidth]{figures/system-design/fig2a-example-input.pdf}\caption{...}
  \end{subfigure}\hfill
  \begin{subfigure}[b]{0.34\textwidth}\centering
    \includegraphics[width=0.9\linewidth]{figures/system-design/fig2b-plain-agent.pdf}\caption{...}
  \end{subfigure}
  \begin{subfigure}[b]{\textwidth}\centering
    \includegraphics[width=\linewidth]{figures/system-design/fig2c-harness-workflow.pdf}\caption{...}
  \end{subfigure}
  \caption{...}
\end{figure*}
```
