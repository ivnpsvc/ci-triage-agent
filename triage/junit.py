import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Failure:
    test_id: str
    kind: str  # "failure" (assertion) or "error" (setup/teardown/crash)
    message: str
    details: str


def test_id(case: ET.Element) -> str:
    return f"{case.get('classname')}::{case.get('name')}"


def read_failures(junit_path: Path) -> list[Failure]:
    failures = []
    for case in ET.parse(junit_path).getroot().iter("testcase"):
        for kind in ("failure", "error"):
            node = case.find(kind)
            if node is not None:
                failures.append(Failure(test_id(case), kind, node.get("message") or "", node.text or ""))
                break
    return failures


def suite_totals(junit_path: Path) -> dict:
    totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    for suite in ET.parse(junit_path).getroot().iter("testsuite"):
        for key in totals:
            totals[key] += int(suite.get(key, 0))
    return totals
