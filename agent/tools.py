"""The agent's tools. Part 1 of HANDOUT.md (and the descriptions are used again in Part 5).

YOU WRITE: safe_path, read_file, edit_file, run_tests, format_report, and the docstring of
each of the three tools you write.
GIVEN (do not change): ToolFailure, use_workspace, workspace, list_files, TOOLS.

A tool's docstring is its description. It is the only thing the model learns about the
tool, both in your own agent and through your MCP server, so write it for the model:
what the tool does, what each input means, what comes back, and its limits. list_files
below is an example of the style.

When a tool cannot do what was asked, raise ToolFailure with a message that teaches: say
what went wrong and what to do next. The model reads that message and decides again.
The exact messages the tests expect are given in the comments above each function.
"""

from __future__ import annotations

from pathlib import Path

from mcp.server.mcpserver.exceptions import ToolError

from agent import ROOT
from agent.testrunner import TestReport, run_unittests

TEST_TIMEOUT_SECONDS = 20
READ_LIMIT_MAX = 200
MAX_PROBLEM_LINES = 10


class ToolFailure(ToolError):
    """A failure you saw coming. Its message is shown to the model, so write it to teach.

    It is MCP's own ToolError, so your MCP server passes the message on to the host too.
    """


_workspace: Path | None = None


def use_workspace(path: str | Path) -> Path:
    """Point every tool at one project folder. A relative path counts from the repository root."""
    global _workspace
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    p = p.resolve()
    if not p.is_dir():
        raise FileNotFoundError(f"workspace folder not found: {p}")
    _workspace = p
    return p


def workspace() -> Path:
    """The project folder the tools work in."""
    if _workspace is None:
        raise RuntimeError("No workspace is set. Call tools.use_workspace(path) first.")
    return _workspace


# safe_path(path) returns the absolute Path of `path` inside the workspace.
#   - `path` is relative to the workspace, for example "discounts.py" or "tests/test_discounts.py".
#   - Refuse an absolute path, and any path that ends up outside the workspace once it is
#     resolved (for example "../judge/acceptance_test.py"), by raising
#         ToolFailure(f"{path} is outside the project folder. Use a path inside it, such as discounts.py.")
#   - The workspace folder itself counts as inside.

def safe_path(path: str) -> Path:
    """Resolve a relative path safely within the workspace."""
    root = workspace()
    requested = Path(path)

    if requested.is_absolute():
        raise ToolFailure(
            f"{path} is outside the project folder. "
            "Use a path inside it, such as discounts.py."
        )

    resolved = (root / requested).resolve()

    if not resolved.is_relative_to(root):
        raise ToolFailure(
            f"{path} is outside the project folder. "
            "Use a path inside it, such as discounts.py."
        )

    return resolved



def list_files() -> str:
    """List every file in the project, one path per line, relative to the project folder.

    Takes no inputs. Use it first to see what the project contains; the paths it returns
    are the paths read_file and edit_file expect.
    """
    root = workspace()
    rows = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    return "\n".join(rows) if rows else "(the project folder is empty)"



def read_file(path: str, start: int = 1, limit: int = 80) -> str:
    """Read numbered lines from a project file, with pagination.

    Use this tool to inspect file contents before making edits.
    Paths must be relative to the project folder. Line numbers start at 1.
    """
    file_path = safe_path(path)

    if not file_path.is_file():
        raise ToolFailure(
            f"{path} is not a file in the project. Call list_files to see the files."
        )

    if start < 1 or limit < 1:
        raise ToolFailure("start and limit must be 1 or more.")

    lines = file_path.read_text(encoding="utf-8").splitlines()
    n = len(lines)

    if n == 0:
        return f"{path} is empty."

    if start > n:
        raise ToolFailure(
            f"{path} has only {n} lines. Use a start between 1 and {n}."
        )

    limit = min(limit, READ_LIMIT_MAX)
    end = min(start + limit - 1, n)

    output = [f"{path}, lines {start} to {end} of {n}"]

    for number in range(start, end + 1):
        output.append(f"{number:>4}: {lines[number - 1]}")

    if end < n:
        output.append(
            f"(more below: call read_file with start={end + 1})"
        )

    return "\n".join(output)


def edit_file(path: str, old_text: str, new_text: str) -> str:
    """Replace one exact, unique text match in a project file.

    Use read_file first to copy the exact text, including whitespace,
    without line numbers. The file is changed only if exactly one
    match exists. Paths must be relative to the project folder.
    """
    file_path = safe_path(path)

    if not file_path.is_file():
        raise ToolFailure(
            f"{path} is not a file in the project. Call list_files to see the files."
        )

    if old_text == "":
        raise ToolFailure(
            "old_text is empty. Copy the exact lines you want to replace "
            "from read_file, without the line numbers."
        )

    content = file_path.read_text(encoding="utf-8")
    count = content.count(old_text)

    if count == 0:
        raise ToolFailure(
            f"old_text appears 0 times in {path}. Read the file again with "
            "read_file and copy the exact text, including its spaces, "
            "without the line numbers."
        )

    if count >= 2:
        raise ToolFailure(
            f"old_text appears {count} times in {path}. Include more of the "
            "surrounding lines so that it appears exactly once."
        )

    updated = content.replace(old_text, new_text, 1)

    with file_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(updated)

    return f"Edited {path}: replaced 1 match."


# format_report(report) turns a TestReport (agent/testrunner.py) into short text.
#   - No problems:  f"PASSED: {report.total} of {report.total} tests passed."
#   - Otherwise the first line is
#         f"FAILED: {len(report.problems)} of {report.total} tests did not pass."
#     then one line per problem, in the report's order, at most MAX_PROBLEM_LINES of them:
#         f"{problem.kind} {problem.name}: {problem.message}"
#     and, only if some were left out, a last line f"({k} more not shown)".
#   - Never include anything else: no timings, no tracebacks, no passing tests.
#     (The stop rule in Part 2 compares two outputs, so the same result must give the same text.)
def format_report(report: TestReport) -> str:
    raise NotImplementedError("Part 1: write format_report in agent/tools.py")


# run_tests() runs the unit tests in the workspace's tests/ folder.
#   - Call run_unittests(workspace(), timeout=TEST_TIMEOUT_SECONDS).
#   - If the report timed out, raise ToolFailure(
#         f"The tests did not finish within {TEST_TIMEOUT_SECONDS} seconds. The last edit may "
#         "have caused an endless loop; read the code you changed.")
#   - Otherwise return format_report(report). Failing tests are not a tool failure: the
#     tool worked, and its output says which tests failed.
def run_tests() -> str:
    """TODO(Part 1): write this tool's description for the model. See HANDOUT.md, Part 1."""
    raise NotImplementedError("Part 1: write run_tests in agent/tools.py")


# The tools the agent offers, in this order. Do not rename them.
TOOLS = [list_files, read_file, edit_file, run_tests]
