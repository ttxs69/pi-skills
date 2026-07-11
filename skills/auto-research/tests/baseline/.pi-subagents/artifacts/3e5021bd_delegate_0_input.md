# Task for delegate

You are a fresh-context research agent. There is no skill loaded. You inherit the same tools as the parent (web_search, fetch_content, read, write, edit, bash).

## Task

Read /Users/sarace/dev/projects/skills/auto-research/tests/baseline/GOAL.md.

Then research this topic autonomously and write your findings to /Users/sarace/dev/projects/skills/auto-research/tests/baseline/FIND.md.

## Constraints

- Use web_search and fetch_content for research. Use read/write for files.
- You have a turn budget — don't try to be exhaustive. Stop when you've covered the topic sufficiently OR when you've used roughly 4-6 tool calls.
- Do not ask questions — make reasonable decisions.

## What I want to observe (do not modify the task to look good — just do what feels natural)

1. What structure does your FIND.md take? (prose? bullet list? table? sections?)
2. Do you cite sources for each claim?
3. Do you iterate (multiple research rounds) or stop after one pass?
4. Do you track what questions are still open vs answered?
5. Do you detect any kind of "I'm done" signal, or just stop when you run out?

Produce the FIND.md file. After finishing, write a one-paragraph note to /Users/sarace/dev/projects/skills/auto-research/tests/baseline/baseline-notes.md describing what you did and why you structured it that way.

---
**Output:**
Write your findings to exactly this path: /Users/sarace/dev/projects/skills/auto-research/tests/baseline/baseline-output.md
This path is authoritative for this run.
Ignore any other output filename or output path mentioned elsewhere, including output destinations in the base agent prompt, system prompt, or task instructions.

## Acceptance Contract
Acceptance level: checked
Completion is not accepted from prose alone. End with a structured acceptance report.

Criteria:
- criterion-1: Implement the requested change without widening scope

Required evidence: changed-files, tests-added, commands-run, residual-risks, no-staged-files

Finish with a fenced JSON block tagged `acceptance-report` in this shape:
Use empty arrays when no items apply; array fields contain strings unless object entries are shown.
```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "specific proof"
    }
  ],
  "changedFiles": [
    "src/file.ts"
  ],
  "testsAddedOrUpdated": [
    "test/file.test.ts"
  ],
  "commandsRun": [
    {
      "command": "command",
      "result": "passed",
      "summary": "short result"
    }
  ],
  "validationOutput": [
    "validation output or concise summary"
  ],
  "residualRisks": [
    "none"
  ],
  "noStagedFiles": true,
  "diffSummary": "short description of the diff",
  "reviewFindings": [
    "blocker: file.ts:12 - issue found, or no blockers"
  ],
  "manualNotes": "anything else the parent should know"
}
```