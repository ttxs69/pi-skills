# Task for delegate

You are running a COMPACTION PASS test for the auto-research skill.

You are the parent agent (loop controller). First: read /Users/sarace/dev/projects/skills/auto-research/SKILL.md in full. Pay particular attention to **Phase 4 step 5 — Compaction Pass**.

## Test workspace
- GOAL.md: /Users/sarace/dev/projects/skills/auto-research/tests/compaction-test/GOAL.md
- FIND.md: /Users/sarace/dev/projects/skills/auto-research/tests/compaction-test/FIND.md (already exists, pre-populated with 12 findings and iter 12 logged)
- FIND-archive.md: DOES NOT EXIST — your compaction pass should create it.

## Test parameters
- **`Iterations: 13`** — this is iteration 13. Stop with status CAPPED after.
- Use your own tools (read, grep, find, ls, bash). No web access needed.
- One iteration = one focused research question = 1-2 findings.

## Compaction triggers expected to fire

When you start Phase 4 record for iter 13, ALL THREE triggers will fire:
1. `## Findings` already has 12 entries (> 10 cap)
2. FIND.md is already ~3.7 KB (> 8 KB? — NO, it's below. So this trigger doesn't fire. Only triggers 1 and 3 fire.)
3. Iterations since "last compaction" = 13 (never compacted) — way more than 5

## What I need to verify (only these)

1. **Compaction happens after the iter 13 finding is appended.** Action:
   - Append Finding 13 to `## Findings` (now 13 entries)
   - Run compaction: demote the lowest-confidence + oldest findings to bring `## Findings` count back to ≤10. Specifically: Findings 8 (low conf) and 12 (low conf) are clear demotion candidates; also Finding 4 or 6 (medium conf, older).
   - Create `FIND-archive.md` if it doesn't exist (header: `# FIND archive — fetch_content vs ctx_fetch_and_index in pi-coding-agent` + a one-line note).
   - Append the demoted findings to `FIND-archive.md` with headers `### Archived at iter 13 — Finding N` followed by the full original block.
   - Replace each demoted finding in `FIND.md` with a one-line stub: `- Finding N (archived → FIND-archive.md): <one-line claim> | confidence: <level> | added: <date>`.
   - Update `## Archived Findings` section to: `<N> earlier findings → FIND-archive.md (last archived at iter 13)`.
2. **Rewrite `## Summary`** to reflect only currently visible findings (do NOT include archived ones).
3. **Header line updated** to `Iterations: 13 | Status: capped`.
4. **Cap reached → stop with status CAPPED.**
5. **Final DONE banner printed**: `[auto-research] DONE — status: capped | iterations: 13 | findings: <M> visible (<T> total in FIND-archive.md) | open questions: <K>`.

## Output expectations

- FIND.md ends with `## Findings` containing exactly the 10 most recent findings (8 through 13 OR 9 through 13 + 2 demoted low-confidence ones + the new one = 10). The demoted ones appear as one-line stubs at the top of `## Findings` or grouped under `## Archived Findings`? Per the SKILL.md, **demoted findings become stubs in `## Findings`** (so they're still listed), with the `## Archived Findings` section being just a pointer line. Re-read the SKILL.md to confirm the exact placement.
- FIND-archive.md exists with at least 1 demoted finding in full.
- FIND.md size is < 8 KB after compaction (the size trigger should now be satisfied).
- Final banner prints.

## Output requirements
- Print both banners (per-iter and DONE) — should appear in your tool output / response.
- Write FIND.md and FIND-archive.md exactly as specified.
- After everything, write a one-paragraph note to /Users/sarace/dev/projects/skills/auto-research/tests/compaction-test/COMPACTION_NOTES.md confirming which of the 5 verification points passed and any that didn't.

## Time budget
Be efficient. Read SKILL.md, append one finding, run compaction, write notes. Aim for under 20 tool calls.

Read the SKILL.md first — it has the full protocol including the compaction pass.

---
**Output:**
Write your findings to exactly this path: /Users/sarace/dev/projects/skills/auto-research/tests/compaction-test/COMPACTION_OUTPUT.md
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