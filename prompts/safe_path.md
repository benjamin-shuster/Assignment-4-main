Current implementation:

```py
# safe_path(path) returns the absolute Path of `path` inside the workspace.
#   - `path` is relative to the workspace, for example "discounts.py" or "tests/test_discounts.py".
#   - Refuse an absolute path, and any path that ends up outside the workspace once it is
#     resolved (for example "../judge/acceptance_test.py"), by raising
#         ToolFailure(f"{path} is outside the project folder. Use a path inside it, such as discounts.py.")
#   - The workspace folder itself counts as inside.
def safe_path(path: str) -> Path:
    raise NotImplementedError("Part 1: write safe_path in agent/tools.py")

```

tests:

```py
def test_safe_path_inside(ws):
    assert tools.safe_path("discounts.py") == ws / "discounts.py"
    assert tools.safe_path("tests/test_discounts.py") == ws / "tests" / "test_discounts.py"


def test_safe_path_refuses_parent(ws):
    with pytest.raises(ToolFailure) as err:
        tools.safe_path("../judge/acceptance_test.py")
    assert str(err.value) == "../judge/acceptance_test.py is outside the project folder. Use a path inside it, such as discounts.py."


def test_safe_path_refuses_absolute(ws):
    target = str((ws / "discounts.py").resolve())
    with pytest.raises(ToolFailure):
        tools.safe_path(target)
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
```

Goal: Implement `safe_path` in `agent/tools.py` to ensure that all file paths are safely resolved within the workspace, refusing absolute paths and paths that lead outside the workspace.


