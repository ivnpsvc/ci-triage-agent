import json
from pathlib import Path

import pytest

JUNIT = """<?xml version="1.0" encoding="utf-8"?>
<testsuites><testsuite name="pytest" tests="3" failures="1" errors="1" skipped="0">
  <testcase classname="tests.api.test_books" name="test_ok"/>
  <testcase classname="tests.api.test_books" name="test_year">
    <failure message="assert 201 == 422">def test_year():
&gt;       assert response.status_code == 422
E       assert 201 == 422</failure>
  </testcase>
  <testcase classname="tests.ui.test_login" name="test_login[chromium]">
    <error message="failed on setup">RuntimeError: App exited early with code 1</error>
  </testcase>
</testsuite></testsuites>
"""


@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    run = tmp_path / "run-01"
    run.mkdir()
    (run / "junit.xml").write_text(JUNIT)
    (run / "meta.json").write_text(json.dumps({"commit": "abc123"}))
    return run


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "app").mkdir(parents=True)
    (root / "app" / "main.py").write_text("def validate(year):\n    return year <= 2026\n")
    (root / "README.md").write_text("answer key lives here\n")
    (root / ".venv").mkdir()
    (root / ".venv" / "lib.py").write_text("year = 1\n")
    return root
