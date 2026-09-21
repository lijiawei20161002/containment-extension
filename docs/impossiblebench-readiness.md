# ImpossibleBench execution readiness

Updated September 21, 2026. Linux validation and qualification of two real
development issues are complete. The approved live preflight has also executed;
see its [incomplete outcomes and accounting correction](impossiblebench-live-preflight-results.md).
For local controls, see the
[development review](impossiblebench-development-review.md) and
[archived evidence](../results/impossiblebench-dev-qualification-v1/README.md).

The current Linux x86-64 Docker host has 30 CPUs, about 222 GiB RAM, and over
1.4 TB free disk. It passes the resource preflight. Both digest-pinned task images
pass the image checks and all scripted qualification controls. The repository
suite passes 121 tests with zero failures/errors/skips after the accounting fix.
The September 18 Mac
assessment below is historical context.

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

Development now includes `pytest-dev__pytest-10051` and `sympy__sympy-24562`;
no held-out assignment has been made. The inventory is reproducible
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
no local GPU. The user subsequently configured `/home/ubuntu/.env` on this Linux
host, and the approved Haiku model was exercised in the live preflight. No key
values are stored in the repository or evidence archive.
Keep credentials in the execution host's environment or an explicit local env
file, outside version control.

## Next execution gate

1. Address actor environment activation and establish original-task completion
   within a suitable call allowance. The completed live preflight had no scored
   submissions or intervention deliveries.
2. Verify the actor reaches the scored submission interface, then requalify any
   changed setup and freeze a new matrix.
3. Obtain approval for a new live allocation. The completed $5/three-million-input
   allocation stopped at its input reservation limit; it does not authorize an
   automatic expansion or retries of its incomplete assignments.

The [execution method](impossiblebench-method.md) contains the commands. Successful
fixture tests and dataset inventory do not establish live model results.
