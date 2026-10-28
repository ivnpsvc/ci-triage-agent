"""The agent's tools: read one CI run's failures and browse the repo, read-only."""

import fnmatch
import json
import re
from pathlib import Path

from triage.junit import read_failures, suite_totals

MAX_OUTPUT_CHARS = 12_000
MAX_READ_LINES = 400
MAX_SEARCH_HITS = 60
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules", "test-results", "reports"}
TEXT_SUFFIXES = {".py", ".html", ".js", ".ts", ".css", ".toml", ".txt", ".md", ".yml", ".yaml", ".json", ".ini", ".cfg"}

# Files in qa-lab that describe the seeded faults. Hidden by default so the agent
# has to work from evidence instead of reading the answer key.
DEFAULT_HIDDEN = ["README.md", "scripts/seeded_runs.py", ".github/workflows/seeded-bugs.yml"]


class ToolError(Exception):
    """Shown to the model as a failed tool call, so it can correct itself."""


def truncate(text: str, limit: int = MAX_OUTPUT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... [truncated, {len(text) - limit} more characters]"


class Workspace:
    """What the agent can see: one CI run's results and a read-only view of the repo
    as it was checked out for that run (the repo plus the run's overlay.json, which
    holds files that differed in that checkout)."""

    def __init__(self, run_dir: Path, repo_dir: Path, hidden: list[str] | None = None):
        self.run_dir = run_dir
        self.repo = repo_dir.resolve()
        self.hidden = {(self.repo / h).resolve() for h in (DEFAULT_HIDDEN if hidden is None else hidden)}
        junit = run_dir / "junit.xml"
        self.failures = {f.test_id: f for f in read_failures(junit)}
        self.totals = suite_totals(junit)
        meta = run_dir / "meta.json"
        self.meta = json.loads(meta.read_text()) if meta.exists() else {}
        overlay = run_dir / "overlay.json"
        self.overlay = json.loads(overlay.read_text()) if overlay.exists() else {}

    # --- tools -------------------------------------------------------------

    def list_failures(self) -> str:
        if not self.failures:
            return "No failed tests."
        lines = []
        for f in self.failures.values():
            first_line = f.message.strip().splitlines()[0] if f.message.strip() else ""
            lines.append(f"{f.test_id} [{f.kind}] {first_line[:200]}")
        return "\n".join(lines)

    def get_failure(self, test_id: str) -> str:
        failure = self.failures.get(test_id)
        if failure is None:
            raise ToolError(f"No failed test with id {test_id!r}. Use the ids from list_failures.")
        return truncate(f"kind: {failure.kind}\nmessage: {failure.message}\n\n{failure.details}")

    def list_files(self, path: str = ".") -> str:
        root = self._resolve(path)
        if not root.is_dir():
            raise ToolError(f"{path} is not a directory")
        files = sorted(
            str(p.relative_to(self.repo)).replace("\\", "/")
            for p in root.rglob("*")
            if p.is_file() and self._visible(p)
        )
        return truncate("\n".join(files) or "(empty)")

    def read_file(self, path: str, start_line: int = 1, end_line: int | None = None) -> str:
        file = self._resolve(path)
        if not file.is_file():
            raise ToolError(f"{path} is not a file")
        lines = self._text(file).splitlines()
        start = max(start_line, 1)
        end = min(end_line or len(lines), len(lines), start + MAX_READ_LINES - 1)
        numbered = [f"{n:>5}  {lines[n - 1]}" for n in range(start, end + 1)]
        footer = f"\n... file has {len(lines)} lines" if end < len(lines) else ""
        return truncate("\n".join(numbered) + footer)

    def search_code(self, pattern: str, path_glob: str | None = None) -> str:
        try:
            regex = re.compile(pattern)
        except re.error as e:
            raise ToolError(f"Invalid regex: {e}")
        hits = []
        for file in sorted(self.repo.rglob("*")):
            if not (file.is_file() and file.suffix in TEXT_SUFFIXES and self._visible(file)):
                continue
            rel = str(file.relative_to(self.repo)).replace("\\", "/")
            if path_glob and not fnmatch.fnmatch(rel, path_glob):
                continue
            for n, line in enumerate(self._text(file).splitlines(), start=1):
                if regex.search(line):
                    hits.append(f"{rel}:{n}: {line.strip()[:200]}")
                    if len(hits) >= MAX_SEARCH_HITS:
                        return "\n".join(hits) + f"\n... stopped at {MAX_SEARCH_HITS} hits, narrow the search"
        return "\n".join(hits) or "No matches."

    # --- dispatch ----------------------------------------------------------

    def call(self, name: str, args: dict) -> str:
        handlers = {
            "list_failures": self.list_failures,
            "get_failure": self.get_failure,
            "list_files": self.list_files,
            "read_file": self.read_file,
            "search_code": self.search_code,
        }
        if name not in handlers:
            raise ToolError(f"Unknown tool {name!r}")
        try:
            return handlers[name](**args)
        except TypeError as e:
            raise ToolError(f"Bad arguments for {name}: {e}")

    # --- helpers -----------------------------------------------------------

    def _resolve(self, path: str) -> Path:
        resolved = (self.repo / path).resolve()
        if not resolved.is_relative_to(self.repo):
            raise ToolError("Path is outside the repository")
        if not self._visible(resolved):
            raise ToolError(f"{path} is not available")
        return resolved

    def _text(self, file: Path) -> str:
        rel = str(file.relative_to(self.repo)).replace("\\", "/")
        if rel in self.overlay:
            return self.overlay[rel]
        return file.read_text(encoding="utf-8", errors="replace")

    def _visible(self, path: Path) -> bool:
        rel_parts = path.relative_to(self.repo).parts
        return not SKIP_DIRS.intersection(rel_parts) and path not in self.hidden


TOOL_DEFINITIONS = [
    {
        "name": "list_failures",
        "description": "List every failed test in this CI run: test id, kind (failure = assertion, "
        "error = setup/teardown/crash) and the first line of the error message.",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "get_failure",
        "description": "Full error message and traceback for one failed test.",
        "input_schema": {
            "type": "object",
            "properties": {"test_id": {"type": "string", "description": "Id exactly as list_failures shows it."}},
            "required": ["test_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_files",
        "description": "List files in the repository (application and tests), optionally under a subdirectory.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Directory relative to the repo root. Default: whole repo."}},
            "additionalProperties": False,
        },
    },
    {
        "name": "read_file",
        "description": f"Read a repository file with line numbers, up to {MAX_READ_LINES} lines per call.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to the repo root."},
                "start_line": {"type": "integer", "description": "First line to read (1-based)."},
                "end_line": {"type": "integer", "description": "Last line to read (inclusive)."},
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "search_code",
        "description": "Regex search across repository text files. Returns path:line: text for each match.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Python regular expression."},
                "path_glob": {"type": "string", "description": "Only search paths matching this glob, e.g. 'tests/*'."},
            },
            "required": ["pattern"],
            "additionalProperties": False,
        },
    },
]
