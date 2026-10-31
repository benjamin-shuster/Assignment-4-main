Current Implementation:

```py
"""Your MCP server: the same four tools, offered to any MCP host. Part 5 of HANDOUT.md.

YOU WRITE this file. It is short: about 15 lines.

What it must do:
  1. Create an MCPServer named "a4-tools" and keep it in a module-level variable named mcp.
  2. Register every function in agent.tools.TOOLS as a tool, with mcp.add_tool(fn).
     That is the same as putting @mcp.tool() on the function: the function's name becomes
     the tool's name, its docstring becomes the description, and its parameters become
     the input schema.
  3. Only when run as a program (inside `if __name__ == "__main__":`), read one required
     command-line option, --workspace PATH, call tools.use_workspace(PATH), then
     mcp.run(transport="stdio").

Importing this file must not start the server: the tests import it and talk to `mcp`
directly.
"""

import argparse

from mcp.server import MCPServer

from agent import tools

# TODO(Part 5): create the server, register the tools, and write main(). About 15 lines.
mcp = None


def main() -> None:
    raise NotImplementedError("Part 5: write server.py")


if __name__ == "__main__":
    main()

```

Tests:

````py
"""Part 5: the MCP server. GIVEN CODE. Do not change it.

These tests connect an MCP client to your server inside the same Python process. The
command `python -m agent check-mcp` starts it as a separate program instead, the way
Claude Code or agy would.
"""

import asyncio
import inspect

from mcp import Client

from agent import tools


def connect_and(fn):
    import server

    assert server.mcp is not None, "server.py must create an MCPServer named mcp (Part 5)"

    async def main():
        async with Client(server.mcp) as client:
            return await fn(client)

    return asyncio.run(main())


def same(a: str, b: str) -> bool:
    return " ".join(a.split()) == " ".join(b.split())


def test_server_offers_the_four_tools_with_their_docstrings(ws):
    result = connect_and(lambda c: c.list_tools())
    names = [t.name for t in result.tools]
    assert names == ["list_files", "read_file", "edit_file", "run_tests"]
    for t in result.tools:
        fn = next(f for f in tools.TOOLS if f.__name__ == t.name)
        assert same(t.description or "", inspect.getdoc(fn) or ""), f"{t.name}: description is not its docstring"
    read = next(t for t in result.tools if t.name == "read_file")
    assert read.input_schema["required"] == ["path"]


def test_server_runs_a_tool(ws):
    result = connect_and(lambda c: c.call_tool("list_files", {}))
    assert result.is_error is False
    assert "discounts.py" in result.content[0].text


def test_server_passes_on_a_teaching_error(ws):
    result = connect_and(lambda c: c.call_tool("read_file", {"path": "../judge/acceptance_test.py"}))
    assert result.is_error is True
    assert "../judge/acceptance_test.py is outside the project folder" in result.content[0].text

        ```
````

Background:

```
**Background.** MCP, the Model Context Protocol, is an open standard for packaging tools
so that any agent can use them. A server is a separate program that offers tools. A
host, such as Claude Code, agy or your own agent, starts the server and talks to it
through a client. The host asks the server `tools/list` to learn each tool's name,
description and inputs, offers those tools to its model, and sends `tools/call` when the
model asks for one. To the model, an MCP tool looks exactly like a tool written inside
the agent. With the official Python SDK, a function you register with the server becomes
a tool: its name is the tool's name, its docstring is the description, and its
parameters are the inputs.

Installing someone else's MCP server means running their code with access to whatever
you connect it to, and putting their tool descriptions in front of your model on every
request. A description or a tool result can hide instructions meant to steer the agent,
for example to read a file of secrets and pass its contents to the server. This is called
prompt injection. The defenses are to install few servers, from sources you trust, to
read their tool descriptions, and to keep approvals on so you see a call's inputs before
it runs.

1. Write `server.py`, following its docstring. It is about 15 lines.
2. Run `python -m agent check-mcp`. It starts your server as a separate program, the
   way Claude Code would, and prints the tools/list reply. That reply is everything the
   model will know about your tools. Read it.
3. Run the whole test suite: `pytest`.

Done when: `pytest` passes and `python -m agent check-mcp` prints "all checks passed".

```

Goals:
Write a server that offers the four tools: `list_files`, `read_file`, `edit_file`, and `run_tests`. Ensure that each tool's description matches its docstring and that the server correctly handles errors and edge cases.
Make no assumptions about the environment or the files available;If any detail is missing, ask for clarification or provide a reasonable default.