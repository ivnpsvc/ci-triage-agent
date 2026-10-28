import json

from triage.score import score_repeats

LABELS = {
    "run-01": {"scenario": "year", "failures": {
        "t1": {"category": "product_bug", "cause": "year"},
        "t2": {"category": "product_bug", "cause": "year"},
    }},
}


def save_pass(folder, category):
    folder.mkdir(parents=True)
    report = {"summary": "", "causes": [{"cause_id": "c", "category": category, "tests": ["t1", "t2"]}]}
    (folder / "run-01.json").write_text(json.dumps({"report": report, "cost_usd": 0.01, "turns": 3}))


def test_agreement_and_per_run_counts(tmp_path):
    (tmp_path / "labels.json").write_text(json.dumps(LABELS))
    save_pass(tmp_path / "r1", "product_bug")
    save_pass(tmp_path / "r2", "product_bug")
    save_pass(tmp_path / "r3", "flaky")

    result = score_repeats(tmp_path, [tmp_path / "r1", tmp_path / "r2", tmp_path / "r3"])

    assert result["per_run"] == {"run-01": 2}
    assert (result["agreed"], result["compared"]) == (0, 2)


def test_full_agreement(tmp_path):
    (tmp_path / "labels.json").write_text(json.dumps(LABELS))
    save_pass(tmp_path / "r1", "product_bug")
    save_pass(tmp_path / "r2", "product_bug")

    result = score_repeats(tmp_path, [tmp_path / "r1", tmp_path / "r2"])

    assert (result["agreed"], result["compared"]) == (2, 2)
