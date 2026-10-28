import pytest

from triage.tools import ToolError, Workspace


def test_failures_are_read_from_junit(run_dir, repo):
    ws = Workspace(run_dir, repo)

    assert list(ws.failures) == ["tests.api.test_books::test_year", "tests.ui.test_login::test_login[chromium]"]
    assert ws.totals == {"tests": 3, "failures": 1, "errors": 1, "skipped": 0}
    assert "[error] failed on setup" in ws.list_failures()


def test_get_failure_returns_traceback(run_dir, repo):
    output = Workspace(run_dir, repo).get_failure("tests.api.test_books::test_year")

    assert "assert 201 == 422" in output


def test_unknown_failure_id_is_a_tool_error(run_dir, repo):
    with pytest.raises(ToolError):
        Workspace(run_dir, repo).call("get_failure", {"test_id": "nope"})


def test_read_file_numbers_lines(run_dir, repo):
    output = Workspace(run_dir, repo).call("read_file", {"path": "app/main.py", "start_line": 2})

    assert output.strip() == "2      return year <= 2026"


@pytest.mark.parametrize("path", ["../outside.txt", "README.md", ".venv/lib.py"])
def test_paths_outside_repo_hidden_or_skipped_are_refused(run_dir, repo, path):
    with pytest.raises(ToolError):
        Workspace(run_dir, repo).read_file(path)


def test_search_skips_hidden_files(run_dir, repo):
    ws = Workspace(run_dir, repo)

    assert ws.search_code("year") == "app/main.py:1: def validate(year):\napp/main.py:2: return year <= 2026"
    assert ws.search_code("answer key") == "No matches."
    assert "README.md" not in ws.list_files()


def test_bad_arguments_are_a_tool_error(run_dir, repo):
    with pytest.raises(ToolError):
        Workspace(run_dir, repo).call("read_file", {"file": "app/main.py"})
