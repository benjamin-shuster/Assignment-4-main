Current Implementation:
```py
"""A judge the agent cannot edit, and Reflexion around the loop. Part 4 of HANDOUT.md.

YOU WRITE: judge, write_lesson, reflexion.
GIVEN (do not change): JUDGE_PATTERN, LESSON_SYSTEM, LESSON_PROMPT.

The judge is the acceptance tests in judge/, outside every workspace, so the agent can
neither read them nor change them. Reflexion runs the agent, asks the judge, and after a
failure asks the model for a two-sentence lesson that the next attempt reads first.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent import JUDGE_DIR
from agent.core import AIError, Approver, Limits, ReflexionResult, summarize_actions
from agent.loop import run_agent
from agent.testrunner import run_unittests
from agent.tools import TEST_TIMEOUT_SECONDS, format_report
from agent.trace import TraceWriter

JUDGE_PATTERN = "*_test.py"

LESSON_SYSTEM = "You review a coding agent's failed attempt and write one short lesson for its next attempt."

LESSON_PROMPT = """The task was: {task}

What the agent did:
{actions}

A check the agent could not see then failed:
{report}

In two plain sentences: why did the attempt fail, and what should the next attempt do differently?"""


# judge(workspace) runs the acceptance tests against one workspace.
#   - report = run_unittests(workspace, tests_dir=JUDGE_DIR, timeout=TEST_TIMEOUT_SECONDS,
#                            pattern=JUDGE_PATTERN)
#   - If it timed out: return (False, f"FAILED: the acceptance tests did not finish within "
#                                     f"{TEST_TIMEOUT_SECONDS} seconds.")
#   - Otherwise return (report.ok, format_report(report)).
def judge(workspace: Path) -> tuple[bool, str]:
    raise NotImplementedError("Part 4: write judge in agent/reflexion.py")


# write_lesson(provider, task, history, report) asks the model why the attempt failed.
#   - prompt = LESSON_PROMPT.format(task=task, actions=summarize_actions(history), report=report)
#   - turn = provider.complete(LESSON_SYSTEM, prompt)
#   - The lesson is turn.text on one line: " ".join(turn.text.split()), cut to its first
#     600 characters.
#   - Return (lesson, turn.input_tokens, turn.output_tokens). Let AIError propagate.
def write_lesson(provider: Any, task: str, history: list[dict[str, Any]], report: str) -> tuple[str, int, int]:
    raise NotImplementedError("Part 4: write write_lesson in agent/reflexion.py")


# reflexion(...) runs up to max_attempts attempts and returns a ReflexionResult.
#   For attempt = 1, 2, ... max_attempts:
#     1. notes = the text of notes_path (or "" if the file does not exist), read fresh
#        at the start of every attempt.
#     2. result = run_agent(task, provider=..., toolbox=..., approve=..., trace=...,
#                           limits=limits, notes=notes, attempt=attempt)
#        If result.status is "error", stop now: return passed False, with result.reason
#        as the report. (A broken provider is not a reason to try again.)
#     3. passed, report = judge(toolbox.workspace), then trace.judge(attempt=..., passed=..., report=...).
#        If passed, return ReflexionResult(True, attempt, runs, lessons, report).
#     4. Otherwise write a lesson with write_lesson(provider, task, result.history, report).
#        If that raises AIError, stop and return passed False.
#        Append one line to notes_path:  f"- Lesson from {trace.run}, attempt {attempt}: {lesson}\n"
#        (start a new line first if the file does not end with one), add the lesson to
#        the list, and write trace.lesson(attempt=..., text=lesson, input_tokens=..., output_tokens=...).
#   After the last attempt fails, return ReflexionResult(False, max_attempts, runs, lessons, report).
#   `runs` is the list of every RunResult, in order.
def reflexion(
    task: str,
    *,
    provider: Any,
    toolbox: Any,
    approve: Approver,
    trace: TraceWriter,
    notes_path: Path,
    limits: Limits = Limits(),
    max_attempts: int = 2,
) -> ReflexionResult:
    raise NotImplementedError("Part 4: write reflexion in agent/reflexion.py")

```

Tests:
```py
"""Part 4: the judge and Reflexion. GIVEN CODE. Do not change it."""

from agent.provider import ScriptedProvider, ask_tool, say
from agent.reflexion import LESSON_SYSTEM, judge, reflexion, write_lesson
from agent.toolbox import LocalToolbox
from agent.trace import TraceWriter
from conftest import NEW_CASE, NEW_DATE, OLD_CASE, OLD_DATE, Approvals, apply

TASK = "Make the tests pass."


def test_judge_fails_the_project_as_given(ws):
    passed, report = judge(ws)
    assert passed is False
    assert report.splitlines() == [
        "FAILED: 2 of 6 tests did not pass.",
        "ERROR test_rule_2_codes_ignore_case: ValueError: unknown code: save10",
        "FAIL test_rule_4_code_is_rejected_after_its_last_day: AssertionError: ValueError not raised",
    ]


def test_judge_passes_when_every_rule_holds(ws):
    apply(ws, OLD_CASE, NEW_CASE)
    apply(ws, OLD_DATE, NEW_DATE)
    assert judge(ws) == (True, "PASSED: 6 of 6 tests passed.")


def test_write_lesson():
    provider = ScriptedProvider([say("It never read spec.md.\n  Next time,   read it first.", input_tokens=70, output_tokens=12)])
    history = [{"role": "user", "text": TASK}]
    lesson, tin, tout = write_lesson(provider, TASK, history, "FAILED: 1 of 6 tests did not pass.")
    assert (lesson, tin, tout) == ("It never read spec.md. Next time, read it first.", 70, 12)
    request = provider.requests[0]
    assert request["kind"] == "complete" and request["system"] == LESSON_SYSTEM
    assert TASK in request["prompt"] and "FAILED: 1 of 6 tests did not pass." in request["prompt"]


def test_reflexion_retries_with_the_lesson(ws, tmp_path):
    notes = tmp_path / "NOTES.md"
    notes.write_text("# Notes for the agent\n", encoding="utf-8")
    provider = ScriptedProvider([
        ask_tool("edit_file", {"path": "discounts.py", "old_text": OLD_CASE, "new_text": NEW_CASE}),
        say("Codes ignore case now."),
        say("I never read spec.md. Next time I will read it before editing."),
        ask_tool("edit_file", {"path": "discounts.py", "old_text": OLD_DATE, "new_text": NEW_DATE}),
        say("Expired codes are rejected now."),
    ])
    trace = TraceWriter(None, run="runX")
    result = reflexion(TASK, provider=provider, toolbox=LocalToolbox(ws), approve=Approvals((True, ""), (True, "")),
                       trace=trace, notes_path=notes, max_attempts=2)

    assert (result.passed, result.attempts) == (True, 2)
    assert [r.status for r in result.runs] == ["done", "done"]
    assert result.lessons == ["I never read spec.md. Next time I will read it before editing."]
    assert notes.read_text().splitlines()[-1] == (
        "- Lesson from runX, attempt 1: I never read spec.md. Next time I will read it before editing."
    )
    # The second attempt started with the lesson in its system prompt.
    second_attempt = [r for r in provider.requests if r["kind"] == "turn"][2]
    assert "I never read spec.md. Next time I will read it before editing." in second_attempt["system"]
    assert second_attempt["history"] == [{"role": "user", "text": TASK}]
    kinds = [(e["kind"], e["attempt"]) for e in trace.events]
    assert kinds == [("tool", 1), ("stop", 1), ("judge", 1), ("lesson", 1), ("tool", 2), ("stop", 2), ("judge", 2)]


def test_reflexion_gives_up_after_the_last_attempt(ws, tmp_path):
    notes = tmp_path / "NOTES.md"
    provider = ScriptedProvider([say("done"), say("Lesson one."), say("done again"), say("Lesson two.")])
    trace = TraceWriter(None, run="runY")
    result = reflexion(TASK, provider=provider, toolbox=LocalToolbox(ws), approve=Approvals(),
                       trace=trace, notes_path=notes, max_attempts=2)
    assert (result.passed, result.attempts, result.lessons) == (False, 2, ["Lesson one.", "Lesson two."])
    assert result.report.startswith("FAILED: 2 of 6")
    assert notes.read_text().splitlines() == [
        "- Lesson from runY, attempt 1: Lesson one.",
        "- Lesson from runY, attempt 2: Lesson two.",
    ]

```

Goal:write `judge`, `write_lesson` and `reflexion`, following the comments above them. If any context is missing, ask for clarification. Do not make assumptions.