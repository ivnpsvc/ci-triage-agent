"""Score triage reports against the answer key from qa-lab's seeded runs.

Per run we check:
- coverage: every failed test is in the report, and nothing else is
- category: product_bug / test_bug / flaky / infrastructure matches the key
- grouping: tests are split into the same groups as the true causes. Cause ids
  are the agent's own names, so only the partition is compared, not the labels.
"""

import json
from pathlib import Path


def flatten(report: dict) -> dict[str, dict]:
    """test id -> {"category", "cause"} from a report's list of causes."""
    flat = {}
    for cause in report.get("causes", []):
        for test in cause["tests"]:
            flat[test] = {"category": cause["category"], "cause": cause["cause_id"]}
    return flat


def partition(assignments: dict[str, str | None]) -> set[frozenset]:
    groups: dict[str, set] = {}
    for test, cause in assignments.items():
        groups.setdefault(cause, set()).add(test)
    return {frozenset(g) for g in groups.values()}


def score_run(report: dict, truth: dict[str, dict]) -> dict:
    predicted = flatten(report)
    missing = sorted(set(truth) - set(predicted))
    extra = sorted(set(predicted) - set(truth))

    gradable = [t for t, label in truth.items() if label["category"] is not None]
    correct = [t for t in gradable if predicted.get(t, {}).get("category") == truth[t]["category"]]
    wrong = {
        t: {"expected": truth[t]["category"], "got": predicted.get(t, {}).get("category")}
        for t in gradable
        if t not in correct
    }

    attributable = [t for t, label in truth.items() if label["cause"] is not None]
    true_groups = partition({t: truth[t]["cause"] for t in attributable})
    pred_groups = partition({t: predicted[t]["cause"] for t in attributable if t in predicted})

    return {
        "failed": len(truth),
        "missing": missing,
        "extra": extra,
        "category_correct": len(correct),
        "category_total": len(gradable),
        "wrong_category": wrong,
        # Leaving a failure out of the report never counts as grouping it right.
        "grouping_correct": not missing and true_groups == pred_groups,
    } | {"fully_correct": not missing and not extra and not wrong and true_groups == pred_groups}


def score_dataset(dataset_dir: Path, predictions_dir: Path) -> dict:
    labels = json.loads((dataset_dir / "labels.json").read_text())
    runs, totals = {}, {"runs": 0, "fully_correct": 0, "category_correct": 0, "category_total": 0,
                        "grouping_correct": 0, "missing": 0, "extra": 0, "cost_usd": 0.0, "turns": 0}
    for run_id, label in labels.items():
        prediction_file = predictions_dir / f"{run_id}.json"
        if not prediction_file.exists():
            continue
        prediction = json.loads(prediction_file.read_text())
        row = score_run(prediction["report"], label["failures"])
        row.update(scenario=label["scenario"], cost_usd=prediction.get("cost_usd"), turns=prediction.get("turns"))
        runs[run_id] = row

        totals["runs"] += 1
        totals["fully_correct"] += row["fully_correct"]
        totals["category_correct"] += row["category_correct"]
        totals["category_total"] += row["category_total"]
        totals["grouping_correct"] += row["grouping_correct"]
        totals["missing"] += len(row["missing"])
        totals["extra"] += len(row["extra"])
        totals["cost_usd"] += row["cost_usd"] or 0
        totals["turns"] += row["turns"] or 0
    totals["cost_usd"] = round(totals["cost_usd"], 4)
    return {"runs": runs, "totals": totals}


def pct(part: int, whole: int) -> str:
    return f"{100 * part / whole:.0f}%" if whole else "n/a"


def render_markdown(score: dict) -> str:
    t = score["totals"]
    lines = [
        "| Run | Scenario | Failed | Category | Grouping | Missing | Extra | Turns | Cost |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for run_id, r in score["runs"].items():
        lines.append(
            f"| {run_id} | {r['scenario']} | {r['failed']} | {r['category_correct']}/{r['category_total']} | "
            f"{'yes' if r['grouping_correct'] else 'no'} | {len(r['missing'])} | {len(r['extra'])} | "
            f"{r['turns']} | ${r['cost_usd'] or 0:.2f} |"
        )
    lines += [
        "",
        f"- Runs fully correct (every category, grouping, nothing missing or extra): "
        f"**{t['fully_correct']}/{t['runs']}**",
        f"- Category accuracy: **{pct(t['category_correct'], t['category_total'])}** "
        f"({t['category_correct']}/{t['category_total']} failed tests)",
        f"- Grouping correct: **{t['grouping_correct']}/{t['runs']} runs**",
        f"- Missing / extra tests in reports: {t['missing']} / {t['extra']}",
        f"- Total cost: ${t['cost_usd']:.2f} over {t['turns']} model turns",
    ]
    wrong = [(run_id, test, w) for run_id, r in score["runs"].items() for test, w in r["wrong_category"].items()]
    if wrong:
        lines += ["", "Wrong categories:"]
        lines += [f"- {run_id} `{test}`: expected {w['expected']}, got {w['got']}" for run_id, test, w in wrong]
    return "\n".join(lines) + "\n"
