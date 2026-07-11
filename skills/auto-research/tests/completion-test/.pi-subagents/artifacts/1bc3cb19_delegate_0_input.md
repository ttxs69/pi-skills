# Task for delegate

You are running a FOCUSED completion-behavior test for the auto-research skill.

You are the parent agent (loop controller). First: read /Users/sarace/dev/projects/skills/auto-research/SKILL.md in full.

## Test workspace
- GOAL.md: /Users/sarace/dev/projects/skills/auto-research/tests/completion-test/GOAL.md (already exists)
- FIND.md: /Users/sarace/dev/projects/skills/auto-research/tests/completion-test/FIND.md (DOES NOT exist — copy template-FIND.md to it)
- template-FIND.md: /Users/sarace/dev/projects/skills/auto-research/tests/completion-test/template-FIND.md

## Test parameters
- **`Iterations: 1`** — run exactly ONE iteration then stop with status CAPPED.
- Use your own tools (read, grep, find, ls, bash) — no nested subagents, no need for web.
- One iteration = one research question = 1-2 findings.

## What I need to verify (only these)

1. Banner prints at bootstrap: `[auto-research] goal: ... | iter: 0/1 | saturation: 0/3`
2. FIND.md is created from template-FIND.md (file is created, not just edited)
3. After iter 1, FIND.md has Findings section populated (claim + sources + confidence + date)
4. After iter 1, FIND.md has Iteration Log with one entry
5. After iter 1, the HEADER LINE updates to `Iterations: 1 | Status: capped`
6. `## Summary` is rewritten with a 2-3 sentence synthesis
7. Final banner prints: `[auto-research] DONE — status: capped | iterations: 1 | findings: M | open questions: K`

## Output requirements

- Print both banners (bootstrap and DONE) — these should appear in your tool output / response.
- Write FIND.md exactly as specified.
- After everything, write a one-paragraph note to /Users/sarace/dev/projects/skills/auto-research/tests/completion-test/COMPLETION_NOTES.md confirming which of the 7 verification points passed and any that didn't.

## Time budget
Be efficient. This is a 1-iteration test. Aim for under 15 tool calls total.

Read the SKILL.md first — it has the full protocol including the banner format and the on-stop procedure.

---
**Output:**
Write your findings to exactly this path: /Users/sarace/dev/projects/skills/auto-research/tests/completion-test/COMPLETION_OUTPUT.md
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