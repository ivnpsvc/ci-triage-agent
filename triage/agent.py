"""The triage agent: a tool-use loop that investigates a CI run and returns a JSON report."""

import json
from collections import Counter
from dataclasses import dataclass, field

import anthropic

from triage.tools import TOOL_DEFINITIONS, ToolError, Workspace

MODEL = "claude-haiku-5-5"  # cheapest; pass --model claude-opus-5-5 for the strongest
CATEGORIES = ["product_bug", "test_bug", "flaky", "infrastructure"]

# USD per million tokens, for the cost line in reports. Haiku's cache prices are
# estimated from the usual ratios (read 0.1x, write 1.25x of input).
PRICES = {
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50, "cache_read": 0.01, "cache_write": 0.125},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_read": 0.20, "cache_write": 2.50},
    "claude-opus-5-5": {"input": 4.00, "output": 20.00, "cache_read": 0.20, "cache_write": 5.00},
}

# Models that support retrying a declined request on a fallback model.
FALLBACK_MODELS = {"claude-opus-5-5", "claude-sonnet-5-5"}

SYSTEM_PROMPT = """You triage failed CI test runs for a web application's test suite.

For every failed test, decide what caused it:
- product_bug: the application behaves wrongly and the test is right to fail.
- test_bug: the test itself is wrong (bad assertion, locator, data or setup).
- flaky: the outcome depends on timing or chance; the same code could pass on a rerun.
- infrastructure: the environment broke (the app could not start, database, network, CI machine), so the failure says nothing about the behavior under test.

Group failures that share one root cause under one cause, so each cause is one thing to fix. Give each cause a short kebab-case cause_id. List tests by their ids exactly as list_failures shows them.

Work from evidence: read the failure details and the relevant test and application code before deciding. In `evidence`, quote the error text or code lines (with file:line) that support the conclusion. When the evidence is thin, say so and lower the confidence. Every failed test must appear in exactly one cause; don't include tests that passed."""

def report_schema(test_ids: list[str]) -> dict:
    """JSON schema for the final report. Test ids are limited to this run's failed
    tests, so the model can't reformat them (it once wrote file paths instead)."""
    return {
        "type": "object",
        "properties": {
            "summary": {"type": "string", "description": "Two or three sentences for the team: what broke and what to do first."},
            "causes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "cause_id": {"type": "string"},
                        "category": {"type": "string", "enum": CATEGORIES},
                        "title": {"type": "string"},
                        "explanation": {"type": "string"},
                        "evidence": {"type": "array", "items": {"type": "string"}},
                        "suggested_fix": {"type": "string"},
                        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                        "tests": {"type": "array", "items": {"type": "string", "enum": test_ids}},
                    },
                    "required": ["cause_id", "category", "title", "explanation", "evidence", "suggested_fix", "confidence", "tests"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["summary", "causes"],
        "additionalProperties": False,
    }


class TriageError(Exception):
    pass


@dataclass
class TriageResult:
    report: dict
    model: str
    turns: int = 0
    usage: Counter = field(default_factory=Counter)
    trace: list[dict] = field(default_factory=list)

    @property
    def cost_usd(self) -> float | None:
        price = PRICES.get(self.model)
        if price is None:
            return None
        return round(
            sum(self.usage[k] * price[k] for k in ("input", "output", "cache_read", "cache_write")) / 1_000_000, 4
        )


def first_message(ws: Workspace) -> str:
    totals = ", ".join(f"{k}={v}" for k, v in ws.totals.items())
    return (
        f"CI run of the test suite (repo commit {ws.meta.get('commit', 'unknown')}). Totals: {totals}.\n\n"
        f"Failed tests:\n{ws.list_failures()}\n\n"
        "Investigate with the tools, then reply with the triage report."
    )


def add_usage(total: Counter, usage) -> None:
    total["input"] += usage.input_tokens or 0
    total["output"] += usage.output_tokens or 0
    total["cache_read"] += getattr(usage, "cache_read_input_tokens", 0) or 0
    total["cache_write"] += getattr(usage, "cache_creation_input_tokens", 0) or 0


def triage(ws: Workspace, client=None, model: str = MODEL, effort: str = "medium", max_turns: int = 40) -> TriageResult:
    result = TriageResult(report={"summary": "No failed tests.", "causes": []}, model=model)
    if not ws.failures:
        return result

    client = client or anthropic.Anthropic()
    # If a request is declined by a safety classifier, retry it on a fallback model.
    fallback = (
        {"betas": ["server-side-fallback-2026-07-01"], "fallbacks": "default"} if model in FALLBACK_MODELS else {}
    )
    schema = report_schema(list(ws.failures))
    messages = [{"role": "user", "content": first_message(ws)}]
    while result.turns < max_turns:
        result.turns += 1
        response = client.beta.messages.create(
            model=model,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
            output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
            cache_control={"type": "ephemeral"},
            **fallback,
        )
        add_usage(result.usage, response.usage)
        # Keep the full content (including thinking blocks) so the next turn continues it.
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "refusal":
            raise TriageError(f"Model declined the request: {response.stop_details}")
        if response.stop_reason == "max_tokens":
            raise TriageError("Response was cut off at max_tokens")

        tool_uses = [b for b in response.content if b.type == "tool_use"]
        if not tool_uses:
            text = "".join(b.text for b in response.content if b.type == "text")
            try:
                result.report = json.loads(text)
            except json.JSONDecodeError as e:
                raise TriageError(f"Final answer was not valid JSON: {e}")
            return result

        tool_results = []
        for block in tool_uses:
            try:
                output, is_error = ws.call(block.name, block.input), False
            except ToolError as e:
                output, is_error = f"Error: {e}", True
            result.trace.append({"turn": result.turns, "tool": block.name, "input": block.input, "is_error": is_error})
            tool_results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": output, "is_error": is_error}
            )
        messages.append({"role": "user", "content": tool_results})

    raise TriageError(f"No report after {max_turns} turns")
