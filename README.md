# ci-triage-agent

An agent that reads a failed CI test run, investigates the test and application
code, and reports **why** each test failed:

| Category | Meaning |
|---|---|
| `product_bug` | the app is wrong; the test is right to fail |
| `test_bug` | the test itself is wrong |
| `flaky` | timing or chance; could pass on a rerun |
| `infrastructure` | the environment broke (app didn't start, DB, network) |

Failures with the same root cause are grouped, so each group is one thing to fix,
with evidence (error text, `file:line`) and a suggested fix.

The point of the project is that **the agent's accuracy is measured, not assumed**.

## How it's measured

The test data comes from [qa-lab](https://github.com/ivnpsvc/qa-lab), whose app has
switchable seeded faults. `qa-lab/scripts/seeded_runs.py` runs the suite once per
fault and records which fault caused each failure. That gives runs where the true
answer is known:

```
datasets/v1/
  runs/run-01/junit.xml, meta.json   what the agent sees (neutral run ids)
  labels.json                        the answer key, never shown to the agent
```

Scoring (`triage/score.py`) checks each run's report for:

- **Category**: is each failed test in the right category?
- **Grouping**: are tests split into the same groups as the true causes? The agent
  names causes itself, so only the grouping is compared, not the names.
- **Coverage**: no failed test left out, no passing test included.
- **Fully correct**: all of the above for the whole run.

Results are compared against a **rule-based baseline** with no AI (crashes are
infrastructure, assertion failures are product bugs, same error message = same cause).
If the agent can't beat that, it isn't worth its cost.

### Dataset v1

| Run | What broke | Failed tests |
|---|---|---|
| run-01 | product bug: next year accepted as publication year | 2 |
| run-02 | product bug: blank title accepted | 1 |
| run-03 | product bug: users can see each other's books | 2 |
| run-04 | flaky: random slow responses vs 5 s UI timeouts | 5 |
| run-05 | infrastructure: app can't open its database | 26 |
| run-06 | two product bugs at once (run-01 + run-03) | 4 |

### Results

| Triage | Runs fully correct | Category accuracy | Grouping correct | Cost |
|---|---|---|---|---|
| Baseline (rules) | 2/6 | 88% | 2/6 | $0 |
| Agent v1, Claude Haiku 5.5, medium effort | 4/6 | 85% | 4/6 | $0.025 |
| Agent v2, test ids fixed by schema | 5/6 | 88% | 6/6 | $0.024 |

Per-run details: `results/<name>/score.md`.

**What v1 showed:** the agent's diagnoses were right in all 6 runs, including the
flaky one (it traced the timeouts to the random delay in `list_books` and the 5 s
UI timeout). But in 2 runs it rewrote the test ids as file paths
(`tests/ui/test_books_ui.py::...` instead of `tests.ui.test_books_ui::...`), so
those tests counted as missing. Anything downstream that uses the ids (rerunning
tests, filing tickets) would break the same way. Fix in v2: the output schema now
allows only the run's exact test ids.

**What v2 showed:** no missing tests and every run grouped correctly. The one miss
is the flaky run, now labeled `product_bug` (v1 said `flaky`). Its reasoning holds
up: the app sometimes takes 8 s, the tests' 5 s limit is a fair expectation, so the
slowness is an app defect. It also noted that nothing in the repo's CI sets the
fault flag and lowered its confidence to medium. So the miss is a gap in the
category definitions, not in the investigation: "flaky" vs "product bug" is
undefined for an app that is randomly slow, and the model flips between the two.

Next steps:
- Decide the policy (for example: "an outcome that changes between runs on the
  same code is `flaky`, wherever the slowness lives") and write it into the
  category definitions. Then add more flaky runs so the rule isn't tuned to one example.
- Run each version 3 times. v1 and v2 disagreeing on the same evidence shows one
  run per version isn't enough to call a difference.

## How it works

`triage/agent.py` is a hand-written tool-use loop on the Anthropic Messages API:

1. The first message lists the run's failures.
2. The model calls tools to investigate, all read-only (`triage/tools.py`):
   `list_failures`, `get_failure`, `list_files`, `read_file`, `search_code`.
   Tool errors (bad path, unknown test id) go back to the model so it can correct itself.
3. It finishes with a JSON report that must match a schema (structured output), so
   the result is always machine-readable and scoreable.

Guard rails: paths can't leave the repo, files that describe the seeded faults
(qa-lab's README and seeding script) are hidden, a turn limit stops runaway loops,
and every tool call is recorded in a trace saved with the report.

## Run it

Requires Python 3.12+ and an Anthropic API key (`ANTHROPIC_API_KEY`).

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest                                   # offline tests, no API calls
```

```bash
python -m triage run --dataset datasets/v1 --repo ../qa-lab --out results/haiku-medium
python -m triage score --dataset datasets/v1 --predictions results/haiku-medium
python -m triage one --run-dir datasets/v1/runs/run-03 --repo ../qa-lab   # readable report
```

The default model is Claude Haiku 5.5 (the cheapest; the whole dataset costs cents).
Use `--model claude-opus-5-5 --effort high` to compare with the strongest model.
`--budget` (default $0.50) stops a dataset run before it starts a new run past that spend.

## Known limitations

- qa-lab's app switches faults on with flags, and the flag names are visible in its
  source. The agent still has to work out which behavior broke from the failures,
  but a real bug wouldn't be labeled. Next: give the agent a copy of the source with
  each fault built in.
- No `test_bug` runs yet. Next: seed broken tests too (wrong locator, wrong
  expected value).
- Six runs is a small dataset; the nightly qa-lab job will add more.
