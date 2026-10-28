"""The agent loop, driven by a fake client so no API call is made."""

import json
from types import SimpleNamespace

import pytest

from triage.agent import TriageError, triage
from triage.tools import Workspace

REPORT = {
    "summary": "One product bug, one infrastructure failure.",
    "causes": [
        {
            "cause_id": "year-validation", "category": "product_bug", "title": "Next year accepted",
            "explanation": "", "evidence": [], "suggested_fix": "", "confidence": "high",
            "tests": ["tests.api.test_books::test_year"],
        },
        {
            "cause_id": "app-start", "category": "infrastructure", "title": "App did not start",
            "explanation": "", "evidence": [], "suggested_fix": "", "confidence": "medium",
            "tests": ["tests.ui.test_login::test_login[chromium]"],
        },
    ],
}
USAGE = SimpleNamespace(input_tokens=1000, output_tokens=200, cache_read_input_tokens=0, cache_creation_input_tokens=0)


def tool_call(id, name, input):
    return SimpleNamespace(type="tool_use", id=id, name=name, input=input)


def text(value):
    return SimpleNamespace(type="text", text=value)


def response(*content, stop_reason="end_turn"):
    return SimpleNamespace(content=list(content), stop_reason=stop_reason, stop_details=None, usage=USAGE)


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self.create))

    def create(self, **request):
        self.requests.append({**request, "messages": list(request["messages"])})
        return self.responses.pop(0)


def test_loop_runs_tools_and_returns_report(run_dir, repo):
    client = FakeClient([
        response(
            tool_call("t1", "get_failure", {"test_id": "tests.api.test_books::test_year"}),
            tool_call("t2", "read_file", {"path": "missing.py"}),
            stop_reason="tool_use",
        ),
        response(text(json.dumps(REPORT))),
    ])

    result = triage(Workspace(run_dir, repo), client=client)

    assert result.report == REPORT
    assert result.turns == 2
    assert [step["tool"] for step in result.trace] == ["get_failure", "read_file"]
    # Both tool results go back in one user message; the bad path is reported as an error.
    tool_results = client.requests[1]["messages"][-1]["content"]
    assert [r["is_error"] for r in tool_results] == [False, True]
    assert "assert 201 == 422" in tool_results[0]["content"]
    assert result.usage["input"] == 2000
    assert result.cost_usd == pytest.approx(0.0004)  # Haiku: 2000 in x $0.10/M + 400 out x $0.50/M


@pytest.mark.parametrize("model, sends_fallback", [("claude-haiku-5-5", False), ("claude-opus-5-5", True)])
def test_fallback_is_only_sent_to_models_that_support_it(run_dir, repo, model, sends_fallback):
    client = FakeClient([response(text(json.dumps(REPORT)))])

    triage(Workspace(run_dir, repo), client=client, model=model)

    assert ("fallbacks" in client.requests[0]) is sends_fallback


def test_first_message_lists_the_failures(run_dir, repo):
    client = FakeClient([response(text(json.dumps(REPORT)))])

    triage(Workspace(run_dir, repo), client=client)

    first = client.requests[0]["messages"][0]["content"]
    assert "tests.ui.test_login::test_login[chromium] [error]" in first
    assert "abc123" in first


def test_report_can_only_name_this_runs_failed_tests(run_dir, repo):
    client = FakeClient([response(text(json.dumps(REPORT)))])

    triage(Workspace(run_dir, repo), client=client)

    schema = client.requests[0]["output_config"]["format"]["schema"]
    allowed = schema["properties"]["causes"]["items"]["properties"]["tests"]["items"]["enum"]
    assert allowed == ["tests.api.test_books::test_year", "tests.ui.test_login::test_login[chromium]"]


def test_run_without_failures_makes_no_api_call(tmp_path, repo):
    run = tmp_path / "clean"
    run.mkdir()
    (run / "junit.xml").write_text('<testsuites><testsuite tests="1"><testcase classname="a" name="b"/></testsuite></testsuites>')

    result = triage(Workspace(run, repo), client=FakeClient([]))

    assert result.report["causes"] == []


def test_refusal_is_an_error(run_dir, repo):
    with pytest.raises(TriageError):
        triage(Workspace(run_dir, repo), client=FakeClient([response(stop_reason="refusal")]))


def test_gives_up_after_max_turns(run_dir, repo):
    looping = [response(tool_call(f"t{i}", "list_failures", {}), stop_reason="tool_use") for i in range(3)]

    with pytest.raises(TriageError):
        triage(Workspace(run_dir, repo), client=FakeClient(looping), max_turns=3)
