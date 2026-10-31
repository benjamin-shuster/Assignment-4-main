"""Where a person must approve, and when the agent must stop. Part 2 of HANDOUT.md.

YOU WRITE: gate_for, budget_stop, is_stuck.
GIVEN (do not change): GATES, TESTS_RULE.

These are plain functions with no model calls, so they are easy to test, and your loop
(Part 3) calls them at the right moments.
"""

from __future__ import annotations

import posixpath
from typing import Any

from agent.core import Limits

# Gate each action by how hard it is to undo:
#   allow  nothing to undo: let it run
#   ask    a person sees what would change and approves or rejects it first
#   deny   never run it
GATES = {
    "list_files": "allow",
    "read_file": "allow",
    "run_tests": "allow",
    "edit_file": "ask",
}

TESTS_RULE = "The tests check the spec, so this agent may not edit files in tests/. Change the code instead."



def gate_for(tool_name: str, args: dict[str, Any]) -> tuple[str, str]:
    if tool_name not in GATES:
        return ("deny", f"{tool_name} is not one of this agent's tools.")

    if tool_name == "edit_file":
        path = args.get("path")

        if isinstance(path, str):
            normalized_path = posixpath.normpath(path.replace("\\", "/"))

            if normalized_path == "tests" or normalized_path.startswith("tests/"):
                return ("deny", TESTS_RULE)

    return (GATES[tool_name], "")


def budget_stop(steps: int, tokens: int, limits: Limits) -> str | None:
    if steps >= limits.max_steps:
        return f"step budget reached: {steps} of {limits.max_steps} model calls"

    if tokens >= limits.max_tokens:
        return f"token budget reached: {tokens} of {limits.max_tokens} tokens"

    return None


def is_stuck(last_output: str | None, output: str, edits_since_last_run: int) -> bool:
    return (
        output.startswith("FAILED")
        and output == last_output
        and edits_since_last_run >= 1
    )