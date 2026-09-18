# ImpossibleBench execution readiness

Assessment on September 18, 2026. No paid inference or real-task container
qualification was performed during this assessment.

For the next machine and Codex agent, start with the [handoff plan](../HANDOFF.md).

## Dataset inventory

The public `fjzzq2002/impossible_swebench` dataset was downloaded at commit
`9c2d34f364b7229e8c0ff807c646100bdc18bbb5`. Each of the original, oneoff, and
conflicting splits contains 349 rows. All 349 base issues have matching repository,
version, base commit, problem statement, reference patch, and original test patch.
The catalog recorded no structural exclusions. This does not certify the mutations
or execution environments.

| Repository | Matched base issues |
| --- | ---: |
| astropy/astropy | 14 |
| django/django | 174 |
| matplotlib/matplotlib | 14 |
| mwaskom/seaborn | 1 |
| pydata/xarray | 17 |
| pylint-dev/pylint | 6 |
| pytest-dev/pytest | 15 |
| scikit-learn/scikit-learn | 24 |
| sphinx-doc/sphinx | 28 |
| sympy/sympy | 56 |

No development or held-out assignment was made. The inventory is reproducible
using `impossible-catalog`; its output includes hashes of each source row and
test/reference paths. Large cached dataset files remain under ignored `runs/`.

## Execution resources

The inspected Mac has eight CPU cores and 8 GiB physical RAM. Docker Desktop has
eight CPUs and about 3.8 GiB RAM, uses ARM64, and the workspace volume has about
11 GiB free disk. It passes the fixture preflight. It fails the real-study planning
checks for memory, storage, and recommended architecture.

Use an existing Linux x86-64 host with Docker, at least eight CPU cores, 16 GiB RAM,
and 120 GB free disk for the initial real-task work. More RAM and storage provide
headroom for additional images; begin with serial execution. These thresholds
follow [SWE-bench's published guidance](https://github.com/SWE-bench/SWE-bench#-usage).
They are planning targets, not a claim that every individual issue needs that
much capacity. The adapter currently limits each task container to two CPUs and
2 GiB RAM; tasks exceeding that limit will need a separately tested configuration.

The host needs network access to acquire the pinned dataset/images and call model
APIs. Actor containers retain their no-network configuration. API inference needs
no local GPU. OpenAI and Anthropic API keys are present in the local configuration;
their account credit and model access have not been checked by this assessment.
Keep credentials in the execution host's environment or an explicit local env
file, outside version control.

## Next execution gate

1. Identify the execution host and run its resource preflight.
2. Review a small number of mutation triples, acquire images, and freeze image
   digests. Do not automatically select issues based on model outcomes.
3. Run original/reference, original/empty, and impossible/reference/empty controls,
   plus observer and termination checks.
4. Freeze a small live matrix and a user-selected API budget. A $25 initial cap is
   a possible spending limit, not an estimate for the 192-rollout development study.
   Measure token usage and runtime before pricing or sizing the expansion.

The [execution method](impossiblebench-method.md) contains the commands. Successful
fixture tests and dataset inventory do not establish live model results.
