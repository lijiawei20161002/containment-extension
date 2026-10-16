# Figure library

Figures are grouped by research topic, then by study, component, or incident.
Each image stays with its editable SVG (when available), generation/edit prompts,
and metadata. Filenames and version suffixes are retained so existing figures
remain easy to find by name.

| Directory | Contents |
| --- | --- |
| [experiments/](experiments/) | Pilot results, scope-level studies, impossible-task and upstream-link experiments |
| [impossiblebench/](impossiblebench/) | Coding tasks, intervention messages, and preflight results |
| [evaluation/](evaluation/) | Evaluation implementation, infrastructure, optimization, and stopping policy |
| [optimization/](optimization/) | Policy optimization architecture, overviews, intuition, and instruction generation |
| [replay/](replay/) | Counterfactual replay concepts, tools, incident reconstructions, and sandbox proposals |
| [incidents/](incidents/) | Public incident case-study illustrations used in presentations |

```text
figures/
├── experiments/
│   ├── pilot/
│   ├── scope-levels/
│   │   ├── technical/
│   │   ├── workflow/
│   │   ├── resources/
│   │   ├── scorer/
│   │   └── instructions/
│   ├── impossible-tasks/
│   └── upstream-link/
├── impossiblebench/
│   ├── task-v1/
│   ├── messages-v1/
│   └── preflight-v1/
├── evaluation/
│   ├── implementation-v1/
│   ├── counterfactual-infrastructure-v1/
│   ├── optimization/
│   └── stop-switch/
├── optimization/
│   ├── architecture-v1/
│   ├── overview-v1/
│   ├── overview-v2/
│   ├── intuition-v1/
│   ├── system-components-v1/
│   └── meta-generator/
├── replay/
│   ├── concept-v1/
│   ├── diagnostic-tool-v1/
│   ├── incident-replays-v1/
│   ├── ca5-v1/
│   └── sandbox-proposals-v1/
└── incidents/
    ├── medicare/
    └── dsewiki/
```

## Browse the figures

The folder links include supporting prompts and metadata where available.

| Topic | Figure | Supporting files |
| --- | --- | --- |
| Experiments | [Pilot setup](experiments/pilot/experiment-setup.png), [results](experiments/pilot/observed-results.png) | [Pilot folder](experiments/pilot/) |
| Experiments | [Scope instructions](experiments/scope-levels/technical/scope-levels-instructions.png), [results](experiments/scope-levels/technical/scope-levels-results.png) | [Technical PNG/SVG files](experiments/scope-levels/technical/) |
| Experiments | [Scope workflow](experiments/scope-levels/workflow/scope-workflow-cartoon.png) | [Workflow folder](experiments/scope-levels/workflow/) |
| Experiments | [Resource inventory](experiments/scope-levels/resources/scope-resources-cartoon.png) | [Resources folder](experiments/scope-levels/resources/) |
| Experiments | [Scorer explained](experiments/scope-levels/scorer/scorer-explained-cartoon.png) | [Scorer folder](experiments/scope-levels/scorer/) |
| Experiments | [Instruction levels cartoon](experiments/scope-levels/instructions/scope-levels-instructions-cartoon.png) | [Instructions folder](experiments/scope-levels/instructions/) |
| Experiments | [Impossible tasks](experiments/impossible-tasks/impossible-tasks-cartoon.png) | [Impossible-tasks folder](experiments/impossible-tasks/) |
| Experiments | [Upstream link](experiments/upstream-link/upstream-link-cartoon.png) | [Upstream-link folder](experiments/upstream-link/) |
| ImpossibleBench | [Task design](impossiblebench/task-v1/impossiblebench-task-cartoon-v1.png) | [Task folder](impossiblebench/task-v1/) |
| ImpossibleBench | [Intervention messages](impossiblebench/messages-v1/impossiblebench-messages-cartoon-v1.png) | [Messages folder](impossiblebench/messages-v1/) |
| ImpossibleBench | [Preflight results](impossiblebench/preflight-v1/impossiblebench-preflight-cartoon-v1.png) | [Preflight folder](impossiblebench/preflight-v1/) |
| Evaluation | [Implemented evaluation](evaluation/implementation-v1/evaluation-implementation.png) | [Implementation folder](evaluation/implementation-v1/) |
| Evaluation | [Counterfactual infrastructure](evaluation/counterfactual-infrastructure-v1/counterfactual-eval-infrastructure.png) | [Infrastructure folder](evaluation/counterfactual-infrastructure-v1/) |
| Evaluation | [Optimization opportunities](evaluation/optimization/evaluation-optimization-cartoon.png) | [Evaluation optimization folder](evaluation/optimization/) |
| Evaluation | [Stopping policy](evaluation/stop-switch/evaluation-stop-switch-cartoon.png) | [Stop-switch folder](evaluation/stop-switch/) |
| Optimization | [Architecture](optimization/architecture-v1/incident-aware-optimization-architecture.png) | [Architecture folder](optimization/architecture-v1/) |
| Optimization | [Overview v1](optimization/overview-v1/incident-optimization-overview.png) | [Overview v1 folder](optimization/overview-v1/) |
| Optimization | [Overview v2](optimization/overview-v2/incident-optimization-overview-v2.png) | [Overview v2 folder](optimization/overview-v2/) |
| Optimization | [Policy-selection intuition](optimization/intuition-v1/incident-optimization-intuition.png) | [Intuition folder](optimization/intuition-v1/) |
| Optimization | [System components](optimization/system-components-v1/incident-system-components.png) | [Components folder](optimization/system-components-v1/) |
| Optimization | [Instruction generator](optimization/meta-generator/meta-generator-workflow-cartoon.png) | [Meta-generator folder](optimization/meta-generator/) |
| Replay | [Replay concept](replay/concept-v1/rewind-detective.png) | [Concept folder](replay/concept-v1/) |
| Replay | [Diagnostic toolbox](replay/diagnostic-tool-v1/counterfactual-diagnostic-tool.png) | [Diagnostic-tool folder](replay/diagnostic-tool-v1/) |
| Replay | [Upstream-link replay](replay/incident-replays-v1/01-upstream-link-replay.png), [answer-archive replay](replay/incident-replays-v1/02-answer-archive-replay.png) | [Incident replay folder](replay/incident-replays-v1/) |
| Replay | [CA5 counterfactual](replay/ca5-v1/ca5-counterfactual-replay.png) | [CA5 folder](replay/ca5-v1/) |
| Replay | [Sandbox proposals](replay/sandbox-proposals-v1/sandbox-proposals.png) | [Sandbox folder](replay/sandbox-proposals-v1/) |
| Incidents | [Medicare statistics portal](incidents/medicare/slide-3-medicare-statistics-portal-incident.png) | [Medicare folder](incidents/medicare/) |
| Incidents | [DSEwiki message board](incidents/dsewiki/slide-6-dsewiki-unauthorized-message-board-icons-refined.png) | [DSEwiki folder](incidents/dsewiki/) |

## Regenerating figures

Run these scripts from the repository root. Their output paths follow this layout.

| Script | Output directory under `figures/` |
| --- | --- |
| [make_figures.py](../scripts/make_figures.py) | `experiments/pilot/` |
| [plot_scope_levels.py](../scripts/plot_scope_levels.py) | `experiments/scope-levels/technical/` |
| [draw_coordination_figures.py](../scripts/draw_coordination_figures.py) | `experiments/coordination-harness/` (created when generated; gallery is not currently checked in) |
| [draw_evaluation_implementation.py](../scripts/draw_evaluation_implementation.py) | `evaluation/implementation-v1/` |
| [draw_incident_optimization_architecture.py](../scripts/draw_incident_optimization_architecture.py) | `optimization/architecture-v1/` |
| [draw_incident_optimization_overview.py](../scripts/draw_incident_optimization_overview.py) | `optimization/overview-v1/` |
| [draw_incident_optimization_overview_v2.py](../scripts/draw_incident_optimization_overview_v2.py) | `optimization/overview-v2/` |
| [draw_incident_optimization_intuition.py](../scripts/draw_incident_optimization_intuition.py) | `optimization/intuition-v1/` |
| [draw_incident_system_components.py](../scripts/draw_incident_system_components.py) | `optimization/system-components-v1/` |

## Adding and maintaining assets

- Add new assets to the matching topic and create a study/component/case folder
  when needed. Keep individual assets out of the `figures/` root.
- Keep each figure's image, SVG, prompts, and metadata together. Retain explicit
  version suffixes where multiple versions are meaningful.
- Update this index, consuming documents, and generator or slide-builder paths
  when moving or adding assets.
- Source and generator hashes in metadata describe the original generation inputs;
  a directory reorganization does not regenerate the images or replace those hashes.
- Frozen evidence under `results/` retains its recorded paths. To locate an asset
  mentioned by an old path, search this index or run
  `rg --files figures | rg '<original-filename>'` from the repository root.
