Current implementation:

```py
# read_file(path, start=1, limit=80) returns part of one text file, with line numbers.
#   - Use safe_path. If the path is not a file, raise
#         ToolFailure(f"{path} is not a file in the project. Call list_files to see the files.")
#   - If start or limit is less than 1, raise ToolFailure("start and limit must be 1 or more.")
#   - Never return more than READ_LIMIT_MAX lines, even if limit is larger.
#   - An empty file returns f"{path} is empty."
#   - If start is past the last line, raise
#         ToolFailure(f"{path} has only {n} lines. Use a start between 1 and {n}.")
#   - Otherwise return, joined with newlines:
#         a header line           f"{path}, lines {start} to {end} of {n}"
#         one line per file line  f"{number:>4}: {text}"   (numbers start at 1)
#         and, only if lines remain after `end`, a last line
#                                 f"(more below: call read_file with start={end + 1})"
def read_file(path: str, start: int = 1, limit: int = 80) -> str:
    """TODO(Part 1): write this tool's description for the model. See HANDOUT.md, Part 1."""
    raise NotImplementedError("Part 1: write read_file in agent/tools.py")


# edit_file(path, old_text, new_text) replaces old_text with new_text, once, in one file.
#   - Use safe_path. If the path is not a file, raise the same ToolFailure as read_file.
#   - If old_text is "", raise ToolFailure(
#         "old_text is empty. Copy the exact lines you want to replace from read_file, without the line numbers.")
#   - Count how many times old_text appears in the file.
#       0 times: raise ToolFailure(f"old_text appears 0 times in {path}. Read the file again with "
#                                  "read_file and copy the exact text, including its spaces, without the line numbers.")
#       2 or more: raise ToolFailure(f"old_text appears {count} times in {path}. Include more of the "
#                                    "surrounding lines so that it appears exactly once.")
#   - Exactly once: replace it, write the file back as UTF-8 with "\n" line endings, and
#     return f"Edited {path}: replaced 1 match."
#   - Change nothing in the file when you raise.
def edit_file(path: str, old_text: str, new_text: str) -> str:
    """TODO(Part 1): write this tool's description for the model. See HANDOUT.md, Part 1."""
    raise NotImplementedError("Part 1: write edit_file in agent/tools.py")
```

tests:

```py
def test_read_file_header_numbers_and_more_line(ws):
    lines = (ws / "discounts.py").read_text().splitlines()
    out = tools.read_file("discounts.py", start=1, limit=3)
    assert out.splitlines() == [
        f"discounts.py, lines 1 to 3 of {len(lines)}",
        f"   1: {lines[0]}",
        f"   2: {lines[1]}",
        f"   3: {lines[2]}",
        "(more below: call read_file with start=4)",
    ]


def test_read_file_to_the_end_has_no_more_line(ws):
    n = len((ws / "spec.md").read_text().splitlines())
    out = tools.read_file("spec.md").splitlines()
    assert out[0] == f"spec.md, lines 1 to {n} of {n}"
    assert len(out) == n + 1
    assert out[-1].startswith(f"{n:>4}: ")


def test_read_file_missing(ws):
    with pytest.raises(ToolFailure) as err:
        tools.read_file("nope.py")
    assert str(err.value) == "nope.py is not a file in the project. Call list_files to see the files."


def test_edit_file_once(ws):
    out = tools.edit_file("discounts.py", OLD_CASE, NEW_CASE)
    assert out == "Edited discounts.py: replaced 1 match."
    assert NEW_CASE in (ws / "discounts.py").read_text()


def test_edit_file_zero_times_teaches(ws):
    before = (ws / "discounts.py").read_text()
    with pytest.raises(ToolFailure) as err:
        tools.edit_file("discounts.py", "if code not in codes:", "x")
    assert str(err.value) == (
        "old_text appears 0 times in discounts.py. Read the file again with read_file and copy the exact "
        "text, including its spaces, without the line numbers."
    )
    assert (ws / "discounts.py").read_text() == before


def test_edit_file_two_times_teaches(ws):
    before = (ws / "discounts.py").read_text()
    with pytest.raises(ToolFailure) as err:
        tools.edit_file("discounts.py", "return total_cents", "return 0")
    assert str(err.value) == (
        "old_text appears 2 times in discounts.py. Include more of the surrounding lines so that it appears exactly once."
    )
    assert (ws / "discounts.py").read_text() == before

```

Relevant Context:

```py
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
```

Goal: Implement `read_file` and `edit_file` in `agent/tools.py` to ensure that file reading and editing are safe and correctly handle edge cases, such as missing files, multiple matches, and zero matches.
