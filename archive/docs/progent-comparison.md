# Raising the evidence standard to Progent's level

**Reference.** Shi, He, Wang, Li, Wu, Guo, Song. *Progent: Securing AI Agents with
Privilege Control.* arXiv:2504.11703, v3 revised 14 May 2026. Code:
`sunblaze-ucb/progent` (agentdojo 0.1.29 fork, `secagent/` package, Z3 narrowing
check). Reviewed 2026-10-31.

## What Progent establishes, and how our 2026-10-31 study compares

| Dimension | Progent | Our decision-algorithms / eval-awareness cohorts (2026-10-31) | Gap |
| --- | --- | --- | --- |
| Threat model | Indirect prompt injection in tool outputs; attacker wants a specific unauthorized tool call | Task-seeking overreach with no adversary: the actor substitutes an excluded resource when the authorized route fails | Different, and both are needed. Progent's attacks never test the "legitimate alternative" case; ours never tests an injected instruction. |
| Benchmark | AgentDojo (banking, slack, travel, workspace) and ASB (10 scenarios × 5 attack templates); MCP migration of AgentDojo; AutoGen multi-agent system | One synthetic two-item control structure with two skins (archive, transfer), 16 development and 16 held-out environments | Public, reproducible task suites with hundreds of security cases versus a local fixture whose baseline incident rate is near zero. |
| Metrics | Utility without attack, utility under attack, attack success rate (ASR), approval overhead (~6% of updates are expansions) | Incident rate with unknown bounds, repeat effects, authorized completion on feasible tasks, mean recorded utility, paired McNemar | Same three-way shape (clean utility / attacked utility / violation rate). We add paired uncertainty; Progent reports no intervals, seeds or repetitions. |
| Baselines | AgentDojo: no defense, repeat_user_prompt, spotlighting_with_delimiting, tool_filter, transformers_pi_detector, DataSentinel, LlamaPromptGuard2. ASB: delimiters, sandwich, instructional prevention | plain actor only | We compare against nothing published. |
| Models | Agent LLM: gpt-4o (default), gpt-4.1, claude-sonnet-4, gemini-2.5-flash, Meta-SecAlign-70B. Policy LLM ablation across the same set | Claude Haiku 4.5, Sonnet 4.6, Haiku 5.5, Sonnet 5 (Sonnet 5.5 refused the transfer skin) | Comparable count; ours is single-vendor. |
| Headline numbers | AgentDojo ASR 39.9% → 1.0% (gpt-4o), 6.8% → 0.5% (claude-sonnet-4); ASB 70.3% → 3.9%; initial policy alone 2.5%; manual approval 0% | Plain 5/60 at-risk episodes, planner 0/117, journal 7/62 (interim) | Our baseline is too low to show a reduction of the size Progent reports. |
| Ablations | Approver mode (disable update, auto-deny, auto-approve, manual); policy LLM; agent LLM; real-world frameworks (LangChain, OpenAI Agents SDK, OpenHands, AutoGen); adaptive attacks (if-then-else, allow-attack-tool, AgentVigil) | Stop reward 0/8; alternate cost 3/−4; journal audit notice | No adaptive attacker, no framework integration, no approver ablation. |
| Mechanism | Deterministic check of every tool call against a JSON-schema policy over tool name and arguments; LLM-generated initial policy; updates classified by Z3 as narrowing (auto) or expansion (approval) | GRANT-LOOKAHEAD: exact DP advice filtered by the grant, not enforced. Effect journal: post-effect authorization labels. Grant updated only by a trusted ASK reply | Progent enforces before dispatch; our planner advises and our journal reports after. Our ASK/grant is Progent's expansion request with a fixed oracle approver. |
| Reporting rigor | Figures only for utility; one Slack injection task hand-corrected; two travel injection tasks excluded as out of threat model | Frozen plans with hashes, every assignment in the denominator, unknowns reported, judge calibration gate | We are ahead on auditability, behind on scale and external validity. |

## What "Progent level" means for this project

1. **Same public benchmark, same attack, same baselines.** AgentDojo at a pinned
   benchmark version with the `important_instructions` attack Progent used, plus
   the `tool_knowledge` attack our protocol already names. Run no-defense and the
   three built-in AgentDojo defenses (repeat_user_prompt, spotlighting_with_delimiting,
   tool_filter) as controls in the same harness and the same model snapshots.
2. **Our interventions as AgentDojo defenses.** Each maps onto Progent's own ablation axis:
   - `grant_broker` — an LLM-generated initial grant (allowed tool names and argument
     constraints) from the user task; every tool call is checked before dispatch;
     blocked calls return a fallback message and an effect-journal entry. With updates
     disabled this is Progent's *Disable Update* configuration, which already reached
     2.5% ASR in their paper. Expansion requests are routed to a precommitted approver
     (auto-deny / auto-approve) to reproduce their approver ablation.
   - `effect_journal` — no blocking; every executed call is annotated with its
     authorization label from the same grant and the running journal is attached to
     the tool result. This is the post-effect feedback arm from the decision-algorithms
     study, and it has no analogue in Progent.
   - `grant_advice` — the grant is shown to the actor at every turn as planning advice
     with no enforcement. This isolates "does the actor follow feedback" from "does the
     broker stop the call", the distinction the Slack injection-task note in Progent's
     README shows AgentDojo's own scorer cannot make.
3. **Three endpoints, as Progent reports them, plus intervals.** Benign utility,
   utility under attack, ASR; approval overhead for the broker; cluster bootstrap over
   user tasks as the standardized-benchmarks protocol requires. Report blocked-but-
   attempted calls separately from executed effects.
4. **Models.** Haiku 4.5 and Sonnet 4.6 as agent and policy model (temperature
   allowed, no safety refusals observed on this family); Sonnet 5 as a second family
   generation. Progent's claude-sonnet-4 numbers (6.8% → 0.5%) are the external anchor.
5. **Adaptive attack appendix.** Progent's "allow attack tool call" and "if-then-else"
   adaptive prompts, which target the policy-update channel. Our grant has no
   tool-data update channel by construction; the adaptive test for us is whether an
   injected instruction can make the actor issue an ASK the approver would grant.
6. **Scale in stages.** Pilot one suite (banking) end to end for plumbing and cost,
   then the full four suites. AgentDojo's full attacked run is every user task crossed
   with every injection task per suite, which is where the cost goes.

## What stays different, deliberately

- Progent's incident is an attacker-chosen tool call. Ours is any committed effect
  outside the trusted grant, including ones the actor chose on its own. On AgentDojo
  the two coincide for the injected target call; the effect journal also records
  off-grant calls the attack did not ask for, which AgentDojo's scorer ignores.
- Progent's policy updates come from the LLM reading tool outputs. Our grant is
  updated only by a trusted ASK reply; this is the "tool data cannot expand the grant"
  rule from the decks and it removes the attack surface their adaptive appendix probes.
- The synthetic two-item fixture remains the place where the exact planner's regret
  is computable. AgentDojo gives external validity, not exact optimality.

## Status

- 2026-10-31: comparison written; AgentDojo 0.1.35 installed into the project
  virtualenv; adapter and pilot plan below in progress. No AgentDojo runs allocated yet.
