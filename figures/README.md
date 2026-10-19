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
    ├── dsewiki/
    ├── hugging-face-infrastructure-compromise/
    ├── dns-route-external-chatbot/
    ├── user-images-external-hosting/
    ├── github-token-published-proof-task/
    ├── rubygems-spam-packages/
    ├── public-data-retrieval-vulnerability-probes/
    ├── us-government-website-interactions/
    ├── self-generated-prompt-injections/
    ├── instructions-to-conceal-mistakes/
    ├── exposed-api-key-fabricated-data/
    ├── public-uploads-around-tool-limits/
    ├── artifactory-unauthorized-communication/
    ├── public-hosting-local-workbook/
    ├── opus-4-7-targets-real-company/
    ├── mythos-5-malicious-pypi-package/
    ├── internal-model-scans-real-targets/
    ├── early-opus-4-6-incident-missed/
    ├── aisi-live-social-engineering/
    ├── gemini-accesses-three-companies/
    ├── meta-model-exploits-third-party-service/
    ├── metr-exposed-dashboard-api-key-theft/
    ├── metr-exposed-evaluation-data-endpoint/
    ├── human-directed-misuse-of-claude/
    ├── autonomous-attacks-online-retailers/
    └── analysis/
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
| Incidents | [1. Hugging Face and internal research infrastructure compromise](incidents/hugging-face-infrastructure-compromise/incident-01-hugging-face-infrastructure-compromise.png) | [Folder](incidents/hugging-face-infrastructure-compromise/) (HTML source + spec JSON) |
| Incidents | [2. DNS route to an external chatbot after security hardening](incidents/dns-route-external-chatbot/incident-02-dns-route-external-chatbot.png) | [Folder](incidents/dns-route-external-chatbot/) (HTML source + spec JSON) |
| Incidents | [3. User images posted to external hosting services](incidents/user-images-external-hosting/incident-03-user-images-external-hosting.png) | [Folder](incidents/user-images-external-hosting/) (HTML source + spec JSON) |
| Incidents | [4. Researcher’s GitHub token published during a proof task](incidents/github-token-published-proof-task/incident-04-github-token-published-proof-task.png) | [Folder](incidents/github-token-published-proof-task/) (HTML source + spec JSON) |
| Incidents | [7. RubyGems spam packages: incident confirmed, AI attribution unresolved](incidents/rubygems-spam-packages/incident-07-rubygems-spam-packages.png) | [Folder](incidents/rubygems-spam-packages/) (HTML source + spec JSON) |
| Incidents | [8. Public-data retrieval escalated into vulnerability probes](incidents/public-data-retrieval-vulnerability-probes/incident-08-public-data-retrieval-vulnerability-probes.png) | [Folder](incidents/public-data-retrieval-vulnerability-probes/) (HTML source + spec JSON) |
| Incidents | [9. U.S. government website interactions](incidents/us-government-website-interactions/incident-09-us-government-website-interactions.png) | [Folder](incidents/us-government-website-interactions/) (HTML source + spec JSON) |
| Incidents | [10. Self-generated prompt injections in task summaries](incidents/self-generated-prompt-injections/incident-10-self-generated-prompt-injections.png) | [Folder](incidents/self-generated-prompt-injections/) (HTML source + spec JSON) |
| Incidents | [11. Instructions to conceal mistakes across context changes](incidents/instructions-to-conceal-mistakes/incident-11-instructions-to-conceal-mistakes.png) | [Folder](incidents/instructions-to-conceal-mistakes/) (HTML source + spec JSON) |
| Incidents | [12. Exposed API key use and fabricated data](incidents/exposed-api-key-fabricated-data/incident-12-exposed-api-key-fabricated-data.png) | [Folder](incidents/exposed-api-key-fabricated-data/) (HTML source + spec JSON) |
| Incidents | [13. Public uploads to work around tool limits](incidents/public-uploads-around-tool-limits/incident-13-public-uploads-around-tool-limits.png) | [Folder](incidents/public-uploads-around-tool-limits/) (HTML source + spec JSON) |
| Incidents | [14. Internal repository used for unauthorized communication](incidents/artifactory-unauthorized-communication/incident-14-artifactory-unauthorized-communication.png) | [Folder](incidents/artifactory-unauthorized-communication/) (HTML source + spec JSON) |
| Incidents | [15. Public hosting used to share a local workbook](incidents/public-hosting-local-workbook/incident-15-public-hosting-local-workbook.png) | [Folder](incidents/public-hosting-local-workbook/) (HTML source + spec JSON) |
| Incidents | [16. Opus 4.7 targets a real company during a cyber evaluation](incidents/opus-4-7-targets-real-company/incident-16-opus-4-7-targets-real-company.png) | [Folder](incidents/opus-4-7-targets-real-company/) (HTML source + spec JSON) |
| Incidents | [17. Mythos 5 publishes a malicious PyPI package](incidents/mythos-5-malicious-pypi-package/incident-17-mythos-5-malicious-pypi-package.png) | [Folder](incidents/mythos-5-malicious-pypi-package/) (HTML source + spec JSON) |
| Incidents | [18. Internal model scans real targets and compromises a live application](incidents/internal-model-scans-real-targets/incident-18-internal-model-scans-real-targets.png) | [Folder](incidents/internal-model-scans-real-targets/) (HTML source + spec JSON) |
| Incidents | [19. Early Opus 4.6 incident missed in the first review](incidents/early-opus-4-6-incident-missed/incident-19-early-opus-4-6-incident-missed.png) | [Folder](incidents/early-opus-4-6-incident-missed/) (HTML source + spec JSON) |
| Incidents | [20. AISI: live social engineering and attempted software compromise](incidents/aisi-live-social-engineering/incident-20-aisi-live-social-engineering.png) | [Folder](incidents/aisi-live-social-engineering/) (HTML source + spec JSON) |
| Incidents | [21. Gemini accesses three real companies during testing](incidents/gemini-accesses-three-companies/incident-21-gemini-accesses-three-companies.png) | [Folder](incidents/gemini-accesses-three-companies/) (HTML source + spec JSON) |
| Incidents | [22. Meta model exploits a third-party service](incidents/meta-model-exploits-third-party-service/incident-22-meta-model-exploits-third-party-service.png) | [Folder](incidents/meta-model-exploits-third-party-service/) (HTML source + spec JSON) |
| Incidents | [23. METR: exposed agent dashboard leads to API-key theft](incidents/metr-exposed-dashboard-api-key-theft/incident-23-metr-exposed-dashboard-api-key-theft.png) | [Folder](incidents/metr-exposed-dashboard-api-key-theft/) (HTML source + spec JSON) |
| Incidents | [24. METR: external probing and an exposed evaluation-data endpoint](incidents/metr-exposed-evaluation-data-endpoint/incident-24-metr-exposed-evaluation-data-endpoint.png) | [Folder](incidents/metr-exposed-evaluation-data-endpoint/) (HTML source + spec JSON) |
| Incidents | [25. Human-directed misuse of Claude across multiple harm areas](incidents/human-directed-misuse-of-claude/incident-25-human-directed-misuse-of-claude.png) | [Folder](incidents/human-directed-misuse-of-claude/) (HTML source + spec JSON) |
| Incidents | [26. Autonomous attacks on online retailers and payment data](incidents/autonomous-attacks-online-retailers/incident-26-autonomous-attacks-online-retailers.png) | [Folder](incidents/autonomous-attacks-online-retailers/) (HTML source + spec JSON) |
| Incidents | [Cross-case analysis: pathways](incidents/analysis/pathways-bar.png), [mechanisms](incidents/analysis/mechanism-heatmap.png), [propositions](incidents/analysis/proposition-heatmap.png), [indicators](incidents/analysis/indicator-matrix.png), [latency](incidents/analysis/latency-dumbbell.png), [stop behaviour](incidents/analysis/stop-behavior-bar.png) | [Analysis folder](incidents/analysis/) (PNG + SVG + summary.json) |

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
| [draw_incident_figures.py](../scripts/draw_incident_figures.py) | `incidents/<slug>/` for entries 1–4 and 7–26 of the 27 Sep 2026 incident briefing (specs in `scripts/incident_figure_specs.py`; renders HTML via headless Chrome; pass entry numbers or slugs to rebuild a subset) |
| [analyze_incident_library.py](../scripts/analyze_incident_library.py) | `incidents/analysis/` (reads `incidents/records/`; run `build_incident_library.py` first) |

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
