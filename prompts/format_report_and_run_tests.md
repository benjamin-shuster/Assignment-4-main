Current implementation:

```py
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

```

tests:

```py
def test_run_tests_on_the_project(ws):
    assert tools.run_tests() == (
        "FAILED: 1 of 4 tests did not pass.\n"
        "ERROR test_lowercase_code_works: ValueError: unknown code: save10"
    )


def test_run_tests_after_a_fix(ws):
    apply(ws, OLD_CASE, NEW_CASE)
    assert tools.run_tests() == "PASSED: 4 of 4 tests passed."


def test_format_report_shows_at_most_ten_problems():
    problems = tuple(Problem("FAIL", f"test_{i:02d}", "AssertionError: 1 != 2") for i in range(12))
    lines = tools.format_report(TestReport(total=20, problems=problems)).splitlines()
    assert lines[0] == "FAILED: 12 of 20 tests did not pass."
    assert lines[1] == "FAIL test_00: AssertionError: 1 != 2"
    assert len(lines) == 12
    assert lines[-1] == "(2 more not shown)"


@pytest.mark.parametrize("fn", tools.TOOLS, ids=lambda f: f.__name__)
def test_every_tool_has_a_real_description(fn):
    doc = inspect.getdoc(fn) or ""
    assert "TODO" not in doc, f"write the description of {fn.__name__}"
    assert len(doc.split()) >= 20, f"the description of {fn.__name__} is too short to guide a model"

```

Relevant Context:

```py
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

```

Goal: Implement the `run_tests` tool in `agent/tools.py` so that it runs the project's tests and returns a summary of the results. The tool should handle both passing and failing tests, and provide clear feedback to the model.