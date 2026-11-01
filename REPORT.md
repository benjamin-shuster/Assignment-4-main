# Assignment 4 Report

Name: Benjamin Shuster
Commit graded:

Answer from your own traces. Give step numbers as `attempt 1, step 4`. Keep to the word
limits; a short answer with the right evidence earns full points.

## Note from Ben
I updated the below line so I can use gpt-6-luna ... because I am cheap xD
See commit bcbafb335624e765378ffb2407fecadfb32c0ba6 for the change.
```py
        if self.model.startswith("gpt-"):
            return {"reasoning_effort": "none"}
```

## 1. The runs

Run `python -m agent summary` and paste its table here exactly as printed.

| Run | Tools | Judge | Stopped (per attempt) | Model calls | Tool calls | Input tokens | Output tokens | Cost | Judge verdict |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| runA | local | after | 1: done | 7 | 8 | 10493 | 691 | $0.0014 | 1: PASS |
| runB | mcp | reflexion | 1: done | 6 | 7 | 8759 | 631 | $0.0012 | 1: PASS |

## 2. A rejection is feedback (Run A, at most 100 words)

**Which step proposed the edit you rejected, and what was your reason?** 
When the agent asked to make the edit to the file, I rejected it because it did not have any comments.
**What did the agent do next, and at which step?** 
The agent revised the edit to include comments, and then re-proposed it at the next step.   
**Did it follow your reason?**
Yes, it followed my reason by adding comments to the edit before re-proposing it.

## 3. The visible tests and the judge (Run A, at most 120 words)

**What did the last `run_tests` in runA report, and what did the judge say after the run?**
The last `run_tests` in runA reported that all tests passed, and the judge confirmed this with a "PASS" verdict.
**If the judge failed, which rule in `spec.md` did the code break, at which step did the agent stop, and why did it stop there?**
The judge did not fail.

## 4. The lessons (Run B, at most 150 words)

**Quote every lesson runB wrote to `NOTES.md`. For each one, say whether it names the real cause, points at evidence, and says what to do next. Did attempt 2 follow it?**
**Give the step that shows it. If attempt 1 passed, say which step shows why no lesson was needed.**
Attempt 1 passed, so no lesson was needed.
Step 6 - Updated `apply_discount` to accept codes case-insensitively and reject codes used after their expiry date. All 4 tests pass.
There was no need for a lesson at this step because all tests passed and the code met the requirements.

## 5. Memory grows (Run A, at most 60 words)

Give `input_tokens` from the first and the last tool event in `runs/runA/trace.jsonl`, with their step numbers. Why does the number grow from step to step?

first_input_tokens: 510
last_input_tokens: 10493

The number grows from step to step because each tool event adds more input tokens to the context, reflecting the cumulative usage of the agent as it progresses through the task.


## 6. MCP (at most 120 words)

**Quote one of your tool descriptions exactly as `python -m agent check-mcp` showed it in the tools/list reply. Then name one risk of installing someone else's MCP server, and say which part of your agent would stop it, or that nothing in your agent would.**
list files tool description:
> List every file in the project, one path per line, relative to the project folder.\n\n    Takes no inputs. Use it first to see what the project contains; the paths it returns\n    are the paths read_file and edit_file expect.\n    

The risk of installing someone else's MCP server is that it could introduce and potentially execute malicious code on my system. My agent would not stop this, as it trusts the MCP server to be safe.
## 7. The reviewer and the judge (at most 100 words)

**What did your reviewer find in runB's final `discounts.py`? Did it find anything the judge did not, or miss anything the judge caught? In the tool you used, was the
reviewer's read-only rule a lock or a request, and how do you know?**

The reviewer found that the final `discounts.py` correctly implemented case-insensitive code handling and expiry date checks, which the judge also verified. The reviewer's read-only rule was a request, not a lock, as evidenced by the fact that the reviewer could still access and analyze the file without making changes.

## 8. Your agent and a vendor's agent (at most 120 words)

**What did the fixer change, and what did `python -m agent judge vendor` report for the visible tests and for the judge? Did it change anything in `tests/`?**
The fixer changed the implementation of the discount logic in `discounts.py` to handle uppercase discount codes correctly. `python -m agent judge vendor` reported that all visible tests passed, and the judge confirmed the correctness of the changes. No changes were made in `tests/`.
**Compare this with runA, where your own agent had the same task on the same project. Then name one thing you could control in your own agent that the fixer file could not set, and one thing that was easier with the vendor's agent.**
In my own agent, I could control the choice of tools and the sequence of actions taken, which the fixer file could not set. With the vendor's agent, it was easier to apply the fixer's changes and verify them through the judge, as the vendor's agent provided a streamlined workflow for this process.