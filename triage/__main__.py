"""Command line.

    python -m triage check
    python -m triage one   --run-dir path/to/run --repo ../qa-lab
    python -m triage run   --dataset datasets/v1 --repo ../qa-lab --out results/haiku-medium
    python -m triage score --dataset datasets/v1 --predictions results/haiku-medium
    python -m triage baseline --dataset datasets/v1 --out results/baseline
"""

import argparse
import json
import os
from pathlib import Path

import anthropic

from triage.agent import MODEL, TriageError, triage
from triage.score import render_markdown, render_repeats, score_dataset, score_repeats
from triage.tools import Workspace


def print_report(report: dict) -> None:
    print(report["summary"], "\n")
    for cause in report["causes"]:
        print(f"[{cause['category']}] {cause['title']} ({cause['confidence']} confidence)")
        print(f"  {cause['explanation']}")
        for line in cause["evidence"]:
            print(f"  - {line}")
        print(f"  Fix: {cause['suggested_fix']}")
        for test in cause["tests"]:
            print(f"    {test}")
        print()


def cmd_one(args) -> None:
    result = triage(Workspace(args.run_dir, args.repo), model=args.model, effort=args.effort)
    print_report(result.report)
    print(f"{result.turns} turns, ${result.cost_usd}")


def cmd_run(args) -> None:
    run_dirs = sorted(p for p in (args.dataset / "runs").iterdir() if p.is_dir())
    if args.runs:
        run_dirs = [p for p in run_dirs if p.name in args.runs]
    # With --repeat N, each pass goes to <out>/r1 ... rN so they can be compared.
    outs = [args.out] if args.repeat == 1 else [args.out / f"r{i}" for i in range(1, args.repeat + 1)]
    spent = 0.0
    for out in outs:
        out.mkdir(parents=True, exist_ok=True)
        for run_dir in run_dirs:
            if spent >= args.budget:
                print(f"Stopping: spent ${spent:.4f}, budget is ${args.budget:.2f}")
                print(f"Total: ${spent:.4f}")
                return
            spent += triage_run(run_dir, out, args)
    print(f"Total: ${spent:.4f}")


def triage_run(run_dir: Path, out: Path, args) -> float:
    """Triage one run, save its report and return what it cost."""
    try:
        result = triage(Workspace(run_dir, args.repo), model=args.model, effort=args.effort)
    except TriageError as e:
        print(f"{out.name}/{run_dir.name}: FAILED - {e}")
        return 0.0
    (out / f"{run_dir.name}.json").write_text(json.dumps({
        "run_id": run_dir.name,
        "model": args.model,
        "effort": args.effort,
        "turns": result.turns,
        "cost_usd": result.cost_usd,
        "usage": dict(result.usage),
        "report": result.report,
        "trace": result.trace,
    }, indent=2) + "\n")
    print(f"{out.name}/{run_dir.name}: {len(result.report['causes'])} causes, {result.turns} turns, ${result.cost_usd}")
    return result.cost_usd or 0


def baseline_report(ws: Workspace) -> dict:
    """No-AI rules to beat: errors are infrastructure, assertion failures are product
    bugs, and failures with the same first message line share a cause."""
    causes: dict[str, dict] = {}
    for failure in ws.failures.values():
        key = failure.message.strip().splitlines()[0] if failure.message.strip() else failure.kind
        cause = causes.setdefault(key, {
            "cause_id": f"cause-{len(causes) + 1}",
            "category": "infrastructure" if failure.kind == "error" else "product_bug",
            "title": key, "explanation": "", "evidence": [], "suggested_fix": "", "confidence": "low", "tests": [],
        })
        cause["tests"].append(failure.test_id)
    return {"summary": "Rule-based baseline.", "causes": list(causes.values())}


def cmd_baseline(args) -> None:
    args.out.mkdir(parents=True, exist_ok=True)
    # Baseline reads only the JUnit reports, so the dataset folder stands in for the repo.
    for run_dir in sorted(p for p in (args.dataset / "runs").iterdir() if p.is_dir()):
        report = baseline_report(Workspace(run_dir, args.dataset))
        (args.out / f"{run_dir.name}.json").write_text(json.dumps(
            {"run_id": run_dir.name, "model": "baseline", "turns": 0, "cost_usd": 0, "report": report}, indent=2
        ) + "\n")
    print(f"Baseline reports written to {args.out}")


def cmd_check(args) -> None:
    """Confirm an API key is configured and accepted, without printing it."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        print("ANTHROPIC_API_KEY is not set in this terminal.")
        return
    print(f"Key found: starts with {key[:10]}..., {len(key)} characters")
    try:
        model = anthropic.Anthropic().models.retrieve(args.model)
        print(f"Key works. {model.display_name} is available.")
    except anthropic.AuthenticationError:
        print("The API rejected this key. Check it was copied from the API Keys page.")
    except anthropic.APIError as e:
        print(f"API error: {e}")


def cmd_score(args) -> None:
    if not args.predictions.is_dir():
        raise SystemExit(f"No reports in {args.predictions}. Run `python -m triage run --out {args.predictions}` first.")
    passes = sorted(p for p in args.predictions.iterdir() if p.is_dir() and p.name.startswith("r"))
    if passes:  # made with --repeat: score each pass, then how much they agree
        for p in passes:
            (p / "score.md").write_text(render_markdown(score_dataset(args.dataset, p)))
        markdown = render_repeats(score_repeats(args.dataset, passes))
    else:
        markdown = render_markdown(score_dataset(args.dataset, args.predictions))
    (args.predictions / "score.md").write_text(markdown)
    print(markdown)


def main() -> None:
    parser = argparse.ArgumentParser(prog="triage")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_model_options(p):
        p.add_argument("--repo", type=Path, required=True, help="Checkout of the repo the tests belong to")
        p.add_argument("--model", default=MODEL)
        p.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])

    one = sub.add_parser("one", help="Triage a single run and print the report")
    one.add_argument("--run-dir", type=Path, required=True)
    add_model_options(one)
    one.set_defaults(func=cmd_one)

    run = sub.add_parser("run", help="Triage every run in a dataset and save the reports")
    run.add_argument("--dataset", type=Path, required=True)
    run.add_argument("--out", type=Path, required=True)
    run.add_argument("--runs", nargs="*", help="Only these run ids")
    run.add_argument("--budget", type=float, default=0.50, help="Stop starting new runs once this many USD are spent")
    run.add_argument("--repeat", type=int, default=1, help="Triage the dataset N times to measure consistency")
    add_model_options(run)
    run.set_defaults(func=cmd_run)

    check = sub.add_parser("check", help="Check the API key works (free; doesn't print the key)")
    check.add_argument("--model", default=MODEL)
    check.set_defaults(func=cmd_check)

    baseline = sub.add_parser("baseline", help="Write rule-based (no AI) reports for a dataset")
    baseline.add_argument("--dataset", type=Path, required=True)
    baseline.add_argument("--out", type=Path, required=True)
    baseline.set_defaults(func=cmd_baseline)

    score = sub.add_parser("score", help="Score saved reports against the dataset's answer key")
    score.add_argument("--dataset", type=Path, required=True)
    score.add_argument("--predictions", type=Path, required=True)
    score.set_defaults(func=cmd_score)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
