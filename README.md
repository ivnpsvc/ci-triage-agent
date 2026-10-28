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

### Dataset v2: harder runs, three passes

Dataset v2 adds the first `test_bug` runs (the generator edits a copy of the tests:
a wrong expected value, a mistyped locator, a test that sends next year while
claiming to test the current year), two more flaky runs and a run mixing a product
bug with a broken test: 12 runs, 53 failed tests. The agent sees each run's
edited files through `overlay.json`, like a CI job checking out that commit.

Changes for v3 of the agent: the policy "an outcome that changes between runs on
the same code is `flaky`, wherever the randomness lives" is now in the category
definitions, and `--repeat 3` triages the dataset three times to measure consistency.

| Triage on dataset v2 | Runs fully correct | Category accuracy | Grouping correct | Cost |
|---|---|---|---|---|
| Baseline (rules) | 2/12 | 70% | 6/12 | $0 |
| Agent v3, Haiku 5.5, pass 1 | 12/12 | 100% | 12/12 | $0.044 |
| Agent v3, pass 2 | 12/12 | 100% | 12/12 | $0.040 |
| Agent v3, pass 3 | 12/12 | 100% | 12/12 | $0.041 |

Every failed test got the same category in all three passes (53/53).

**Why the perfect score needs a caveat:** the traces show the agent searching
qa-lab for the fault switches (`BUGS`, `year_off_by_one`) and quoting the app's
docstring that lists the seeded bugs. The test-bug runs have no such shortcut and
were still solved from evidence (for the locator typo it compared
`get_by_test_id('add-books')` in the page object with `data-testid="add-book"` in
the template). But the product-bug and flaky results are inflated. Next: dataset v3
builds product bugs into the code the same way as test bugs, so the app source
has no switches or bug list left to find.

### Dataset v3: no shortcuts left

qa-lab's app no longer has fault switches or a bug list. Every fault is now a code
edit made by the generator to a temporary copy (for example, the book query losing
its `owner_id` filter, or the title check missing `.strip()`), and the agent sees
the edited files like any checked-out commit. A scan of the run files finds no
fault names. The same tests fail as in v2, so the datasets are comparable.

| Triage on dataset v3 | Pass 1 | Pass 2 | Pass 3 | Same category every pass | Cost (3 passes) |
|---|---|---|---|---|---|
| Baseline (rules) | 2/12 | | | | $0 |
| Agent v3 | 10/12 | 12/12 | 12/12 | 91% | $0.103 |
| Agent v4, report completeness check | **12/12** | **12/12** | **12/12** | **100%** | $0.101 |

Runs fully correct per pass. With nothing to search for, the agent's searches
follow the evidence (`sleep|random`, `owner_id`, `add-books|data-testid`), and it
still solves every fault, so the v2 result wasn't only the shortcut.

**What v3 showed:** both misses were reports with an empty list of causes, while
the summary had the right diagnosis (`not book.title` without `.strip()`; the
random sleep in `list_books`). The schema allows an empty list, and the model
sometimes took it. **Fix in v4:** after the final answer, the agent checks that
every failed test is in exactly one cause; if not, it sends the report back with
what's missing (at most twice). Over 36 runs the check fired once and the retry
fixed it.

## How it works

`triage/agent.py` is a hand-written tool-use loop on the Anthropic Messages API:

1. The first message lists the run's failures.
2. The model calls tools to investigate, all read-only (`triage/tools.py`):
   `list_failures`, `get_failure`, `list_files`, `read_file`, `search_code`.
   Tool errors (bad path, unknown test id) go back to the model so it can correct itself.
3. It finishes with a JSON report that must match a schema (structured output), so
   the result is always machine-readable and scoreable.

4. The report is checked: every failed test must be in exactly one cause. If not,
   it goes back to the model with what's missing (at most twice).

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

- Twelve runs and eight faults is still a small dataset, and every fault is a
  one-line edit. Harder cases to add: bugs spread over several files, failures with
  misleading error messages, and real-world flaky patterns (test order, shared state).
- Results are for one model at one effort level. Next: the same dataset on
  `claude-opus-5-5` to see what the extra cost buys, if anything.
