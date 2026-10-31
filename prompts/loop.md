Current Implementation:
```py
"""The agent loop: decide, act, observe, repeat. Part 3 of HANDOUT.md.

YOU WRITE: build_system_prompt, run_agent.
GIVEN (do not change): BASE_SYSTEM, NOTES_HEADER.

run_agent is the ReAct loop, written against a real tool-calling API. It
must be your own code: no agent framework, and no SDK helper that runs the loop for you.
"""

from __future__ import annotations

from typing import Any

from agent.core import (
    AIError,
    Approver,
    Limits,
    RunResult,
    ToolSpec,
    tool_result_message,
    user_message,
)
from agent.policy import budget_stop, gate_for, is_stuck
from agent.trace import TraceWriter

BASE_SYSTEM = """You are a careful coding agent working in a small Python project.
You can see and change the project only through the tools you are given.
Before each tool call, write one short sentence that says what you will do and why.
Change only what the task needs, one edit at a time.
A person reviews every edit. If they reject one, read their reason and follow it.
When you are finished, reply without calling a tool, in one or two sentences that say what you changed."""

NOTES_HEADER = "Notes from earlier runs. Read them before you start:"


# build_system_prompt(notes) returns the system prompt for one attempt.
#   - If notes is empty or only whitespace: return BASE_SYSTEM.
#   - Otherwise: BASE_SYSTEM, a blank line, NOTES_HEADER, a newline, then notes.strip().
#     That is: BASE_SYSTEM + "\n\n" + NOTES_HEADER + "\n" + notes.strip()
#   This is long-term memory: the text of NOTES.md, put in front of the model at every start.
def build_system_prompt(notes: str) -> str:
    raise NotImplementedError("Part 3: write build_system_prompt in agent/loop.py")


# run_agent(...) runs one attempt at the task and returns a RunResult.
#
# Before the loop:
#   - system = build_system_prompt(notes); history = [user_message(task)]
#   - Offer the model only the tools your policy does not deny:
#     every spec in toolbox.specs() for which gate_for(spec.name, {})[0] != "deny".
#   - Keep counters: steps (model calls), input and output tokens, the last run_tests
#     output, and the number of successful edits since the last run_tests.
#
# Each time around the loop:
#   1. reason = budget_stop(steps, input + output tokens, limits). If there is a reason,
#      stop with status "budget" and that reason, without calling the model.
#   2. turn = provider.next_turn(system, history, specs). If it raises AIError, stop with
#      status "error" and str(error) as the reason. Otherwise add 1 to steps, add the
#      turn's tokens, and append turn.message to the history.
#   3. If turn.tool_calls is empty, the model is finished: stop with status "done", reason
#      "the model replied without a tool call", and turn.text as the final text.
#   4. For every call in turn.tool_calls, in order:
#        decision, why = gate_for(call.name, call.args)
#        deny:  do not run it. ok is False; text is f"Refused by policy: {why}"
#        ask:   preview = toolbox.preview(call.name, call.args)
#               If preview is None, the call cannot succeed, so run it without asking
#               (the tool returns its own error). Otherwise approved, reason = approve(call, preview).
#               Rejected: do not run it. ok is False; text is
#                   f"A person rejected this {call.name} call. Reason: {reason}"
#               Approved: ok, text = toolbox.call(call.name, call.args)
#        allow: ok, text = toolbox.call(call.name, call.args)
#      Then append tool_result_message(call, text, ok) to the history, and write one
#      trace.tool(...) event: attempt, step (the current steps count), thought (turn.text),
#      tool, input (call.args), gate (the decision), approved (True or False if a person
#      was asked, otherwise None), reason (the person's reason when rejected, otherwise ""),
#      ok, output (text), and the turn's input_tokens and output_tokens.
#      Bookkeeping: a successful edit_file adds 1 to the edits count. After a successful
#      run_tests, check is_stuck(last_output, text, edits); then remember text as the last
#      output and set the edits count back to 0.
#   5. If is_stuck was True for any run_tests in this turn, stop with status "stuck" and
#      reason "the same tests failed the same way after an edit".
#
# Every way of stopping writes exactly one trace.stop(...) event (attempt, step = steps,
# status, reason, final_text, and the attempt's total input_tokens and output_tokens) and
# returns RunResult(status, reason, steps, input_tokens, output_tokens, final_text, history).
def run_agent(
    task: str,
    *,
    provider: Any,
    toolbox: Any,
    approve: Approver,
    trace: TraceWriter,
    limits: Limits = Limits(),
    notes: str = "",
    attempt: int = 1,
) -> RunResult:
    raise NotImplementedError("Part 3: write run_agent in agent/loop.py")

```

Tests:
```py
"""Part 3: the loop. GIVEN CODE. Do not change it.

These tests use a scripted model (no API key, no cost) and a person played by Approvals.
"""

from agent.core import AIError, Limits
from agent.loop import BASE_SYSTEM, NOTES_HEADER, build_system_prompt, run_agent
from agent.provider import ScriptedProvider, ask_tool, say
from agent.toolbox import LocalToolbox
from agent.trace import TraceWriter
from conftest import NEW_CASE, OLD_CASE, Approvals

TASK = "Make the tests pass."


def run(ws, replies, approvals=None, limits=Limits(), notes=""):
    provider = ScriptedProvider(replies)
    trace = TraceWriter(None, run="test")
    approve = approvals if approvals is not None else Approvals()
    result = run_agent(TASK, provider=provider, toolbox=LocalToolbox(ws), approve=approve, trace=trace,
                       limits=limits, notes=notes)
    return result, provider, trace


def test_build_system_prompt():
    assert build_system_prompt("") == BASE_SYSTEM
    assert build_system_prompt("  \n") == BASE_SYSTEM
    assert build_system_prompt("\n- read spec.md first\n") == BASE_SYSTEM + "\n\n" + NOTES_HEADER + "\n- read spec.md first"


def test_happy_path(ws):
    approvals = Approvals((True, ""))
    result, provider, trace = run(ws, [
        ask_tool("run_tests", {}, "I will run the tests.", input_tokens=100, output_tokens=10),
        ask_tool("read_file", {"path": "discounts.py"}, "I will read the code.", input_tokens=200, output_tokens=10),
        ask_tool("edit_file", {"path": "discounts.py", "old_text": OLD_CASE, "new_text": NEW_CASE}, "Fix case.",
                 input_tokens=300, output_tokens=30),
        ask_tool("run_tests", {}, "Check again.", input_tokens=400, output_tokens=10),
        say("Codes now ignore case.", input_tokens=500, output_tokens=10),
    ], approvals)

    assert (result.status, result.steps) == ("done", 5)
    assert (result.input_tokens, result.output_tokens) == (1500, 70)
    assert result.final_text == "Codes now ignore case."
    assert NEW_CASE in (ws / "discounts.py").read_text()

    # The model was offered the four tools, and saw each result before its next decision.
    assert [t.name for t in provider.requests[0]["tools"]] == ["list_files", "read_file", "edit_file", "run_tests"]
    assert provider.requests[0]["system"] == BASE_SYSTEM
    second = provider.requests[1]["history"]
    assert [m["role"] for m in second] == ["user", "assistant", "tool"]
    assert second[-1]["text"].startswith("FAILED: 1 of 4")

    # The person saw a diff before the edit was made.
    assert len(approvals.seen) == 1
    assert "+    code = code.upper()" in approvals.seen[0][1]

    kinds = [e["kind"] for e in trace.events]
    assert kinds == ["tool", "tool", "tool", "tool", "stop"]
    edit = trace.events[2]
    assert (edit["step"], edit["tool"], edit["gate"], edit["approved"], edit["ok"]) == (3, "edit_file", "ask", True, True)
    assert trace.events[0]["approved"] is None
    stop = trace.events[-1]
    assert (stop["status"], stop["step"], stop["input_tokens"], stop["output_tokens"]) == ("done", 5, 1500, 70)


def test_a_rejection_goes_back_to_the_model(ws):
    before = (ws / "discounts.py").read_text()
    result, provider, trace = run(ws, [
        ask_tool("edit_file", {"path": "discounts.py", "old_text": OLD_CASE, "new_text": NEW_CASE}),
        say("I will stop."),
    ], Approvals((False, "Add a comment that names the spec rule.")))

    assert (ws / "discounts.py").read_text() == before
    reply = provider.requests[1]["history"][-1]
    assert reply["role"] == "tool" and reply["is_error"] is True
    assert reply["text"] == "A person rejected this edit_file call. Reason: Add a comment that names the spec rule."
    event = trace.events[0]
    assert (event["approved"], event["reason"], event["ok"]) == (False, "Add a comment that names the spec rule.", False)


def test_a_denied_call_never_runs_and_nobody_is_asked(ws):
    before = (ws / "tests" / "test_discounts.py").read_text()
    result, provider, trace = run(ws, [
        ask_tool("edit_file", {"path": "tests/test_discounts.py", "old_text": "1800", "new_text": "0"}),
        say("I will stop."),
    ], Approvals())  # no answers: asking would fail the test

    assert (ws / "tests" / "test_discounts.py").read_text() == before
    reply = provider.requests[1]["history"][-1]
    assert reply["text"].startswith("Refused by policy: ")
    assert trace.events[0]["gate"] == "deny"


def test_an_edit_that_cannot_apply_is_not_sent_for_approval(ws):
    result, provider, trace = run(ws, [
        ask_tool("edit_file", {"path": "discounts.py", "old_text": "not in the file", "new_text": "x"}),
        say("I will stop."),
    ], Approvals())

    reply = provider.requests[1]["history"][-1]
    assert reply["is_error"] is True and "appears 0 times" in reply["text"]
    assert trace.events[0]["approved"] is None


def test_the_step_budget_stops_before_another_model_call(ws):
    result, provider, trace = run(ws, [ask_tool("list_files") for _ in range(5)], limits=Limits(max_steps=2))
    assert (result.status, result.steps) == ("budget", 2)
    assert len(provider.requests) == 2
    assert result.reason == "step budget reached: 2 of 2 model calls"
    assert trace.events[-1]["kind"] == "stop"


def test_the_same_failure_after_an_edit_is_stuck(ws):
    comment = ("    if code == \"\":\n", "    # first try\n    if code == \"\":\n")
    again = ("    # first try\n", "    # second try\n")
    result, provider, trace = run(ws, [
        ask_tool("run_tests"),
        ask_tool("edit_file", {"path": "discounts.py", "old_text": comment[0], "new_text": comment[1]}),
        ask_tool("run_tests"),
        ask_tool("edit_file", {"path": "discounts.py", "old_text": again[0], "new_text": again[1]}),
        ask_tool("run_tests"),
        say("never reached"),
    ], Approvals((True, ""), (True, "")))
    assert result.status == "stuck"
    assert result.steps == 3
    assert result.reason == "the same tests failed the same way after an edit"


def test_a_provider_error_stops_the_run(ws):
    result, provider, trace = run(ws, [AIError("Anthropic rejected your API key.")])
    assert (result.status, result.reason, result.steps) == ("error", "Anthropic rejected your API key.", 0)
    assert [e["kind"] for e in trace.events] == ["stop"]


def test_notes_go_into_the_system_prompt(ws):
    result, provider, trace = run(ws, [say("ok")], notes="- read spec.md before editing")
    assert provider.requests[0]["system"].endswith(NOTES_HEADER + "\n- read spec.md before editing")

```

Relevant Context:

```py
"""The types and helpers everything in the agent uses.

GIVEN CODE. Read it first; do not change it.

The conversation ("history") is a list of plain dicts in one of three shapes. You never
build the assistant shape yourself: append `turn.message`. Use the two helpers below for
the other two.

    {"role": "user", "text": "Make the tests pass."}
    {"role": "assistant", "text": "...", "tool_calls": [{"id", "name", "args"}], ...}
    {"role": "tool", "id": "<call id>", "name": "run_tests", "text": "...", "is_error": False}

The provider (agent/provider.py) turns this list into whatever format the Anthropic or
OpenAI API expects, so the same loop works with either.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


class SetupError(RuntimeError):
    """Something in .env or the setup needs fixing."""


class AIError(RuntimeError):
    """The model provider refused or failed a request."""


@dataclass(frozen=True)
class ToolSpec:
    """What the model is told about one tool. These three fields are all it ever sees."""

    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass(frozen=True)
class ToolCall:
    """One tool request from the model: a tool name and its inputs."""

    id: str
    name: str
    args: dict[str, Any]


@dataclass(frozen=True)
class ModelTurn:
    """One reply from the model.

    text        what the model wrote (its "thought" before a tool call, or its final answer)
    tool_calls  the tools it asked for, in order; empty means it is finished
    raw         the provider's own copy of the reply, sent back unchanged on the next call
    """

    text: str
    tool_calls: tuple[ToolCall, ...]
    input_tokens: int
    output_tokens: int
    stop_reason: str = ""
    raw: Any = None
    provider: str = ""

    @property
    def message(self) -> dict[str, Any]:
        """This reply as a history entry. Append it to the history before running any tool."""
        return {
            "role": "assistant",
            "text": self.text,
            "tool_calls": [{"id": c.id, "name": c.name, "args": dict(c.args)} for c in self.tool_calls],
            "raw": self.raw,
            "provider": self.provider,
        }


def user_message(text: str) -> dict[str, Any]:
    """A history entry for something a person says, such as the task."""
    return {"role": "user", "text": text}


def tool_result_message(call: ToolCall, text: str, ok: bool) -> dict[str, Any]:
    """A history entry that reports one tool call's result back to the model."""
    return {"role": "tool", "id": call.id, "name": call.name, "text": text, "is_error": not ok}


@dataclass(frozen=True)
class Limits:
    """The stop rules' numbers. A step is one model call."""

    max_steps: int = 15
    max_tokens: int = 150_000


@dataclass
class RunResult:
    """How one run of the loop ended.

    status is one of: "done" (the model replied without a tool call), "budget" (a limit
    was reached), "stuck" (the same failure after an edit), "error" (the provider failed).
    """

    status: str
    reason: str
    steps: int
    input_tokens: int
    output_tokens: int
    final_text: str
    history: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ReflexionResult:
    """How a Reflexion run ended: did the judge pass, after how many attempts."""

    passed: bool
    attempts: int
    runs: list[RunResult]
    lessons: list[str]
    report: str


# An approver is shown one tool call and a preview of what it would change, and answers
# (approved, reason). The reason is sent to the model when the call is rejected.
Approver = Callable[[ToolCall, str], "tuple[bool, str]"]


def summarize_actions(history: list[dict[str, Any]], limit: int = 40) -> str:
    """A short numbered list of the tool calls in a history, with the first line of each result.

    Used to tell a model what an earlier attempt did, without sending the whole history.
    """
    results = {m["id"]: m for m in history if m.get("role") == "tool"}
    lines: list[str] = []
    for m in history:
        if m.get("role") != "assistant":
            continue
        for c in m.get("tool_calls", []):
            res = results.get(c["id"])
            if res is None:
                outcome = "no result"
            else:
                first = (res["text"].strip().splitlines() or [""])[0][:160]
                outcome = ("error: " if res["is_error"] else "") + first
            args = ", ".join(f"{k}={_short(v)}" for k, v in c["args"].items())
            lines.append(f"{len(lines) + 1}. {c['name']}({args}) -> {outcome}")
    if not lines:
        return "(it called no tools)"
    if len(lines) > limit:
        lines = lines[:limit] + [f"({len(lines) - limit} more calls not shown)"]
    return "\n".join(lines)


def _short(value: Any, n: int = 60) -> str:
    text = repr(value)
    return text if len(text) <= n else text[: n - 3] + "..."

```

Goal: Write `build_system_prompt` and `run_agent`, following the comments above them. 
The comment above `run_agent` lists every step in order. No framework, and no SDK helper that runs the loop.
Ask for clarification if any part of the instructions is unclear. Do not guess or assume.

