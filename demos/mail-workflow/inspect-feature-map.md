# Inspect capabilities in the mail workflow

The current movie executes containment-extension's local office fixture. It does
not run an Inspect evaluation. The Inspect scenes describe the proposed adapter.
The repository's existing ImpossibleBench adapter uses Inspect tasks, samples,
model generation, a custom solver, scoring, and eval logs, but delegates the tool
loop to its own `run_one` implementation. Its direct backend dispatch does not
automatically acquire Inspect's native tool approvals.

This distinction matters: the integration should reuse Inspect's experiment and
agent infrastructure while adding the scope contract, Grant Look-ahead, Effect
Journal, and domain-specific effect scoring.

| Inspect capability | Role in this email example | Work needed in containment-extension |
| --- | --- | --- |
| Components: tasks and datasets | One request and initial workspace per `Sample`; a task parameter selects plain, planner, journal, or combined feedback | Build a general mail task with isolated state and a setup solver; keep scoring-only labels out of model-visible context |
| Components: solvers and scorers | Initialize scope before the agent; score the recorded outcome after the run | Adapt contract compilation and existing outcome checks to Inspect components; preserve unknown outcomes |
| Models | Select providers, models, generation settings, and concurrency through Inspect | Replace direct provider plumbing where appropriate; record settings and keep experimental conditions comparable |
| Agents | Use the built-in ReAct loop, or an explicit adapter for an external agent | Deliver initial advice before generation, then journal and updated advice between turns; verify callback timing and termination |
| Tools | Expose `email_fetch`, `email_reply`, and ticket operations as custom tools or locally executed MCP tools | Bind those tools to the fixture first, then to a real service with reliable receipts |
| Tool approval | In a distinct enforcement condition, approve, reject, or escalate a proposed write before dispatch | Supply a policy that checks the scope contract; record blocked attempts separately from committed effects |
| Running | Organize model × feedback-condition comparisons, concurrency, errors, and limits | Configure retry and stopping behavior explicitly; isolate workspaces; retain interrupted and failed trials |
| Analysis | Inspect View for individual traces; dataframes for comparisons; scanners for transcript review | Include feedback delivery, scope revisions, effects, and outcomes so they can be joined and inspected |
| Extensions | Package tasks, solvers, tools, scorers, approvers, and monitoring hooks for reuse | Add a tested registry and Inspect entry point; document which tasks and tools the package supports |

Tasks combine the dataset, solver/agent, scoring, setup, approval, and execution
options in one evaluation definition. See [Tasks](https://inspect.aisi.org.uk/tasks.html).
Model selection and generation options are documented in
[Using Models](https://inspect.aisi.org.uk/models.html).

## What the extension adds

- A ReAct agent can plan through model reasoning and tool use. Grant Look-ahead
  adds recommendations computed over an explicit, modeled authorization scope.
  Inspect's agent loop can host that advice without replacing its own execution
  machinery. The current finite planner still needs a modeled action space.
- Inspect approval supplies the pre-execution decision mechanism. Our scope policy
  would supply the domain-specific authorization decision. This is an optional
  enforcement condition, separate from measuring whether advice changes behavior.
- Inspect logs retain the evaluation trajectory. Effect Journal adds a structured
  account of committed effects and their scope status, delivered back to the agent
  when the experimental condition calls for it. The backend observation and scope
  classification remain part of this project's work.

## One action in the proposed native loop

```text
Dataset Sample: user request + visible email/ticket workspace
  → Task setup: create per-sample state, compile scope, deliver initial advice
  → Inspect ReAct agent: choose email_reply(message-01)
  → Optional approval policy: approve / reject / escalate
  → Inspect custom tool or local-execution MCP binding
  → Mail backend: commit reply and retain receipt
  → Effect Journal: classify the committed effect against scope
  → Continuation feedback: journal + updated planner recommendation
  → Next agent decision, or completion
  → Scorer: authorized completion, incidents, repeat effects, unknowns
  → Inspect log viewer, dataframes, and transcript review
```

For current Inspect documentation, a callable `react(on_continue=...)` can return
a string to append between iterations even when the preceding response called a
tool. A plain string continuation has different timing: it is only appended when
the model made no tool calls. Initial advice must also be supplied before the
first generation. Submission and any final effects need end-of-run handling even
when there is no next iteration. These are adapter behaviors to test against a
pinned Inspect version, not features demonstrated by the local replay.
[ReAct continuation](https://inspect.aisi.org.uk/react-agent.html#continuation)

The advisory conditions must leave the actor able to ignore the feedback if the
study is measuring whether agents follow it. An enforcement condition adds a
separate approver and answers a different question. An approver observes a proposed
call; an effect record describes what execution committed. A rejected call is a
blocked attempt, not a committed incident. Provider-executed remote MCP calls
cannot go through Inspect approval; use local execution when approval is required.
[Tool approval](https://inspect.aisi.org.uk/approval.html)

## Running and analysis are part of the design

An evaluation set could compare the same cases across models and feedback arms.
Retries, caching, and early stopping must follow the study protocol, rather than
silently inheriting defaults. A retry is not a new independent successful trial,
and a missing outcome is not evidence of safe completion. Side-effecting services
also need reset or reconciliation before any rerun.
[Eval sets](https://inspect.aisi.org.uk/eval-sets.html)

The resulting Inspect logs should show which feedback was visible before each
decision and link calls to the backend's receipts. `samples_df()` provides
sample-level rows, while message and event dataframes support closer inspection.
Scanners, authored with Inspect Scout and integrated into the evaluation workflow,
can assist with transcript review; structural effect verification still needs the
backend evidence and appropriate scorers.
[Log dataframes](https://inspect.aisi.org.uk/dataframe.html),
[Transcript scanners](https://inspect.aisi.org.uk/scanners.html)

Monitoring hooks can export lifecycle events and results. They should not be used
as a hidden mechanism for mutating the agent's context or as a substitute for the
service's effect record. Hook instances are process-wide, so concurrent sample
state must be keyed and isolated correctly.
[Hooks](https://inspect.aisi.org.uk/extensions-hooks.html)

## Features to add when the task needs them

Multimodal input is useful when the customer sends screenshots or other supported
attachments. Multiple agents are useful when the experiment intentionally separates
mail triage from another role. A sandbox is appropriate when an agent can execute
untrusted code or use a browser; the pure in-memory mail fixture does not itself
need a container. Caching and batch mode are execution options whose suitability
depends on the provider and study. New model APIs, sandbox implementations, or
filesystems are unnecessary if existing Inspect integrations already meet the
requirements.

Tutorial, Evals, the community gallery, and the API reference are learning and
reuse resources. They are not additional runtime stages that every evaluation
needs to invoke. Ready-made benchmarks still need compatible tools, scope, and
observable effects before this extension can evaluate their authorization behavior.

## What “one-click” could mean

Inspect discovers packaged components through Python entry points. A future
containment package could expose a configured mail task and an adapter factory,
making a supported evaluation straightforward to launch. Installing it would not
automatically instrument every existing agent, tool backend, or CRUX experiment.
Tool bindings, credentials, scope semantics, and observation coverage still have
to be configured. The current `pyproject.toml` has an optional Inspect dependency
but no Inspect entry-point registration.
[Packaged components](https://inspect.aisi.org.uk/extensions-components.html)

CRUX remains the open-world research project and methodology. An Inspect-based
implementation could support a CRUX-style study; that would not make CRUX a
separate plugin runtime.

Checked against the repository and official Inspect documentation on 26 November 2026.
