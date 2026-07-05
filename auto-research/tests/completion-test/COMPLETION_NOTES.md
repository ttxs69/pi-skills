# Completion-behavior test notes

## Result: PASS (all 7 verification points satisfied)

### Verification checklist

1. **PASS — Bootstrap banner printed.** `[auto-research] goal: # Research goal | iter: 0/1 | saturation: 0/3` printed before any iteration began. Note: the test goal's first line is literally `# Research goal` (a markdown H1), so the banner uses that as the goal descriptor; this matches the SKILL.md spec which says "first line of GOAL.md".
2. **PASS — FIND.md created from template-FIND.md.** File did not exist before; `cp template-FIND.md FIND.md` ran successfully. The file was created (not edited), preserving the bootstrap iter 0 entry from the template.
3. **PASS — Findings section populated after iter 1.** Two `### Finding N — ...` blocks present, each with claim, sources, confidence, and `Added: 2026-07-05` date.
4. **PASS — Iteration Log has one new entry.** Iter 1 entry present plus the iter 0 bootstrap entry copied from the template (per SKILL.md schema, the iter 0 line is part of the starter template).
5. **PASS — Header line updated.** Final header: `_Started: 2026-07-05 | Last updated: 2026-07-05 | Iterations: 1 | Status: capped_`.
6. **PASS — `## Summary` rewritten.** Replaced the template's "Empty" placeholder with a 3-sentence synthesis grounded in the two findings (seven built-in tools; zero matches for the named tools; nothing to compare).
7. **PASS — Final DONE banner printed.** `[auto-research] DONE — status: capped | iterations: 1 | findings: 2 | open questions: 1`.

### Tool budget

Total tool calls: ~11 (well under the 15-call budget). No nested subagents dispatched (per test parameters, used my own tools directly).

### Notable observations

- The research topic in GOAL.md (`fetch_content` vs `ctx_fetch_and_index`) is itself a red-herring: neither tool exists in the pi-coding-agent harness. The strongest possible single-iteration finding is therefore the negative-existence finding rather than a comparison, and the synthesis honestly says "there is nothing to compare". The remaining work was correctly logged as an open question (where do these tools come from?).
- The default `summary` field template says "Iterations: N | Status: in-progress | saturated | capped | interrupted" — the final value `capped` is from the legitimate cap-exit path, not from a malformed iteration.
- One minor wording choice: I kept the template's iter 0 bootstrap entry in the Iteration Log, then appended iter 1. This matches the SKILL.md schema which lists `iter 0` as the standard template starter.