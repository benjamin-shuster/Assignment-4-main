# Provenance Ledger

Write one entry per reviewable change or experiment, when the work is done. Use exactly
the schema in HANDOUT.md. Put the prompts you typed into AI tools in `prompts/` and name
the file in the entry's `prompts` field.

For a run, most of the entry comes straight from its trace: what the agent did and in
what order, the commands that checked it, and the result. You add what only you know:
how you reviewed it, what you rejected, and what is still uncertain.

## Worked example (not graded; leave it here and add your entries under "My entries")

This shows the level of detail expected. The commit SHAs, dates, steps and numbers are
made up, and so is the practice run.

```
## Entry 2
artifact:  agent/loop.py, run_agent, at commit 9c3a71e
tool:      Claude Code, model Claude Sonnet 5.5, 2026-11-01
prompts:   asked for the loop body from the comment above run_agent;
           prompts/loop-01.md
review:    read every line against the comment. It returned as soon as is_stuck was
           true, which skipped the tool results for the other calls in the same turn;
           moved the stuck check after the for loop as the comment says. Rejected its
           suggestion to import a framework's message classes; kept the dicts from
           core.py
checks:    pytest tests/test_loop.py: 9 passed
evidence:  HANDOUT Part 3; the comment above run_agent, steps 4 and 5
risk:      no test of mine has three tool calls in one turn

## Entry 4
artifact:  runs/try1, a practice run, agent code at commit 4b9e2d1
tool:      my agent (python -m agent run try1), anthropic claude-haiku-5-5, 2026-11-02
prompts:   the default task and BASE_SYSTEM in agent/loop.py; prompts/try1-task.md
review:    read every event in trace.jsonl. At attempt 1, steps 4 and 6, the model
           copied old_text with the read_file line numbers, and edit_file refused both
           times. At step 7 it made an edit that changed nothing the tests check, and
           at step 8 the stuck rule stopped it. I approved the step 7 edit without
           reading it closely
checks:    python -m agent check-trace try1: complete
evidence:  HANDOUT Part 1 (tool descriptions) and Part 2 (is_stuck)
risk:      one practice run; a better description may still not stop the copying
dataset:   fixture/ at commit 4b9e2d1, task "Make the tests pass."
result:    stopped stuck after 8 model calls, 14,880 input tokens, about $0.002;
           runs/try1/trace.jsonl
changed:   wrote "copy it without the line numbers" into the read_file and edit_file
           descriptions, and read every diff before approving
```

## My entries

## Entry 1

provider: OpenAI
model: gpt-6-luna
price_input_per_mtok: 0.1
price_output_per_mtok: 0.5
page: https://platform.openai.com/docs/models/gpt-6-luna
notes: I chose this model even though the default model is different, because it is cheaper for my use case. I accept all risks associated with using this model for the assignment.

## Entry 2

artifact: agent/tools.py, safe_path, at commit d724319c027985155a526872fcd3ae8601476913
tool: Chat GPT Web UI 2026-10-31
prompts: prompts/safe_path.md
review: pasted output into VS code and used default linter to check for syntax errors and style issues. Ran tests to ensure they all passed.
checks: pytest tests/test_tools.py: all 3 safe_path tests passed
evidence: HANDOUT Part 1 step 1
risk: unexpected edge cases in path resolution depending on the environment the code is run in

## Entry 3

artifact: agent/tools.py, read_file and edit_file, at commit f5af19487184d8dacdb7e8bf6702194307380ad8
tool: Chat GPT Web UI 2026-10-31
prompts: prompts/read_and_edit_file.md
review: pasted output into VS code and used default linter to check for syntax errors and style issues. Ran tests to ensure they all passed.
checks: pytest tests/test_tools.py: all 8 read_file and edit_file tests passed
evidence: HANDOUT Part 1 step 1
risk: unexpected edge cases in file reading and editing, such as handling line numbers, whitespace, and multiple matches

## Entry 4

artifact: agent/tools.py, run_tests and format_report, at commit baf0830ff6bf090e42427458c98590bceeeb2ca1
tool: Chat GPT Web UI 2026-10-31
prompts: prompts/format_report_and_run_tests.md
review: pasted output into VS code and used default linter to check for syntax errors and style issues. Ran tests to ensure they all passed.
checks: pytest tests/test_tools.py: all 4 run_tests and format_report tests passed
evidence: HANDOUT Part 1 step 1
risk: unexpected edge cases in running tests and formatting reports, such as handling timeouts, partial failures, and large numbers of failing tests

## Entry 5

artifact: agent/policy.py,gate_for, budget_stop, is_stuck, at commit eed6d4247d93294f1fbfea0cd86a1db87ea2bc1a
tool: Chat GPT Web UI 2026-10-31
prompts: prompts/policy.md
review: pasted output into VS code and used default linter to check for syntax errors and style issues. Ran tests to ensure they all passed.
checks: pytest tests/test_policy.py: all gate_for, budget_stop, and is_stuck tests passed
evidence: HANDOUT Part 2
risk: unexpected edge cases in policy enforcement, such as handling unusual tool names, malformed arguments, and extreme budget conditions

## Entry 6

artifact: agent/loop.py, run_agent and build_system_prompt, at commit 56a171914e3d3d2eb7f426a8abf53617e6484782
tool: Chat GPT Web UI 2026-10-31
prompts: prompts/loop.md
review: pasted output into VS code and used default linter to check for syntax errors and style issues. Ran tests to ensure they all passed.
checks: pytest tests/test_loop.py: all tests passed
evidence: HANDOUT Part 3
risk: unexpected edge cases in the agent loop, such as handling tool call failures, policy violations, and extreme budget conditions

## Entry 7

artifact: agent/reflexion.py, judge, write_lesson and reflexion, at commit 719e5634b32e47f7b2e6f34a0ddc4528a33bd09e
tool: Chat GPT Web UI 2026-10-31
prompts: prompts/reflexion.md
review: pasted output into VS code and used default linter to check for syntax errors and style issues. Ran tests to ensure they all passed.
checks: pytest tests/test_reflexion.py: all tests passed
evidence: HANDOUT Part 4
risk: unexpected edge cases in the reflexion process, such as handling tool call failures, policy violations, and extreme budget conditions

## Entry 8

artifact: agent/server.py, at commit 0b1af5fb450cf42924a30ee20b6cb2655eafdc0e
tool: Chat GPT Web UI 2026-10-31
prompts: prompts/server.md
review: pasted output into VS code and used default linter to check for syntax errors and style issues. Ran tests to ensure they all passed. Ran python -m agent check-mcp to verify the server starts correctly.
checks: pytest tests/test_server.py: all tests passed
evidence: HANDOUT Part 5
risk: unexpected edge cases in the server, such as handling tool call failures, policy violations, and extreme budget conditions