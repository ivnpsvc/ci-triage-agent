from triage.score import score_run

TRUTH = {
    "t1": {"category": "product_bug", "cause": "year_off_by_one"},
    "t2": {"category": "product_bug", "cause": "year_off_by_one"},
    "t3": {"category": "product_bug", "cause": "leak_books"},
}


def report(*causes):
    return {"summary": "", "causes": [{"cause_id": c, "category": cat, "tests": tests} for c, cat, tests in causes]}


def test_perfect_report():
    score = score_run(report(("year", "product_bug", ["t1", "t2"]), ("leak", "product_bug", ["t3"])), TRUTH)

    assert score["category_correct"] == 3
    assert score["grouping_correct"] is True
    assert score["missing"] == score["extra"] == []
    assert score["fully_correct"] is True


def test_cause_names_dont_matter_only_the_grouping():
    score = score_run(report(("anything", "product_bug", ["t3"]), ("else", "product_bug", ["t1", "t2"])), TRUTH)

    assert score["grouping_correct"] is True


def test_merged_causes_fail_grouping_but_keep_category():
    score = score_run(report(("all", "product_bug", ["t1", "t2", "t3"])), TRUTH)

    assert score["grouping_correct"] is False
    assert score["category_correct"] == 3
    assert score["fully_correct"] is False


def test_missing_and_extra_tests_are_reported():
    score = score_run(report(("year", "flaky", ["t1", "t2", "t9"])), TRUTH)

    assert score["missing"] == ["t3"]
    assert score["extra"] == ["t9"]
    assert score["category_correct"] == 0
    assert score["wrong_category"]["t1"] == {"expected": "product_bug", "got": "flaky"}
    assert score["grouping_correct"] is False


def test_unattributable_failures_are_left_out_of_grading():
    truth = {**TRUTH, "t4": {"category": None, "cause": None}}

    score = score_run(report(("y", "product_bug", ["t1", "t2"]), ("l", "product_bug", ["t3", "t4"])), truth)

    assert score["category_total"] == 3
    assert score["grouping_correct"] is True
