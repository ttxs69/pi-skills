# Task for delegate

You are running a GREEN-phase verification test for the auto-research skill.

You are acting as the **parent agent** (loop controller). The skill content is at /Users/sarace/dev/projects/skills/auto-research/SKILL.md — read it first, in full.

## Test workspace

- `/Users/sarace/dev/projects/skills/auto-research/tests/with-skill/GOAL.md` — the research goal (read it first)
- `/Users/sarace/dev/projects/skills/auto-research/tests/with-skill/template-FIND.md` — starter template (copy to FIND.md if missing)
- `/Users/sarace/dev/projects/skills/auto-research/tests/with-skill/FIND.md` — where findings go (create from template if missing)

## Constraints for this test

- **`Iterations: 3`** — hard cap of 3 iterations. Then stop with status CAPPED.
- You may use web_search / fetch_content if available. If not, use training-time knowledge but disclose this in each finding's `Sources:` field (e.g., `Sources: training-time, no web access in this test run`).
- You may NOT spawn nested subagents in this test — do the research yourself with whatever tools you have. (The skill normally uses subagents per iteration; for this verification we run inline to keep the test cheap.)
- Treat each iteration as ONE focused research question.

## What I'm verifying (do not optimize for these — just follow the skill)

1. **Does FIND.md get written?** (vs inline output like the baseline)
2. **Is FIND.md in the structured findings format** (claim + sources + confidence + date)?
3. **Does the loop actually iterate** (multiple iterations, not one pass)?
4. **Is the iteration log populated**?
5. **Does the banner print at bootstrap and each iteration?**
6. **Does it stop at the cap** (iter 3 = CAPPED)?

## Output expectations

- FIND.md should contain a populated `## Findings` section with at least 2-3 findings.
- FIND.md should have a populated `## Iteration Log` with one line per iteration.
- FIND.md should have a populated `## Open Questions` section.
- The final header line should read `Status: capped` after 3 iterations.
- A `## Summary` section should be rewritten at the end.

After you finish, write a one-paragraph note to /Users/sarace/dev/projects/skills/auto-research/tests/with-skill/GREEN_NOTES.md describing what worked, what was confusing, and what (if anything) you skipped or improvised.

## Important reminders

- READ THE SKILL.md FILE FIRST. It contains the full protocol.
- Update FIND.md after EVERY iteration (don't batch updates).
- Use edit/append operations, not full rewrites.
- Print the banner at bootstrap AND at the start of every iteration.
- Do NOT fabricate URLs. If you don't have web access, say so in Sources.

---
**Output:**
Write your findings to exactly this path: /Users/sarace/dev/projects/skills/auto-research/tests/with-skill/GREEN_OUTPUT.md
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