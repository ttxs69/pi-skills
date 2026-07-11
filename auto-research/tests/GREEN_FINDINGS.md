# GREEN-phase findings

**Date:** 2026-07-05
**Verdict:** PASS — all baseline failures addressed; all completion behaviors verified.

## Test 1 — Full 3-iteration run (timed out at iter 3)

**Setup:** `delegate` subagent given SKILL.md + bounded `Iterations: 3`. Workspace: `tests/with-skill/`.

**Result:** Killed by SIGTERM (exit 143) at iter 3 due to subagent runtime limit. ~17s wall clock, 21 turns, 40 tool calls.

**What passed:**
- ✅ FIND.md was created (vs baseline's inline-only failure)
- ✅ Structured findings format used (claim + sources + confidence + date)
- ✅ 5 high-quality findings produced with file:line sources from the actual codebase
- ✅ Loop iterated (iter 1 + iter 2 complete before termination)
- ✅ Iteration Log populated (2 entries)
- ✅ Open Questions tracked with `- [ ]` checkboxes + one `- [x]` resolved
- ✅ Sources were real (file:line paths, not fabricated)

**What wasn't tested (kill happened before iter 3 completion):**
- ❌ Cap stop with status `CAPPED`
- ❌ Final DONE banner
- ❌ ## Summary rewrite at exit

**Notable observation:** Agent discovered that the GOAL.md topic (`fetch_content` vs `ctx_fetch_and_index`) was a red herring — neither tool exists in pi-coding-agent. Agent correctly produced a negative-existence finding rather than fabricating a comparison. This is the kind of good research judgment the skill should produce.

## Test 2 — Focused 1-iteration completion test

**Setup:** `delegate` subagent given SKILL.md + bounded `Iterations: 1`. Workspace: `tests/completion-test/`.

**Result:** PASS — all 7 verification points satisfied. 11 tool calls total (under 15-call budget).

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Bootstrap banner `[auto-research] goal: ... \| iter: 0/1 \| saturation: 0/3` printed | PASS |
| 2 | FIND.md created from template-FIND.md (via `cp`, not edit) | PASS |
| 3 | Findings section populated (2 findings, each with claim + sources + confidence + date) | PASS |
| 4 | Iteration Log has one new entry (iter 1) plus iter 0 from template | PASS |
| 5 | Header line updated to `Iterations: 1 \| Status: capped` | PASS |
| 6 | `## Summary` rewritten with a 3-sentence synthesis | PASS |
| 7 | Final banner `[auto-research] DONE — status: capped \| iterations: 1 \| findings: 2 \| open questions: 1` printed | PASS |

## Baseline failures → GREEN outcomes

| Baseline failure (RED) | Outcome (GREEN) |
|---|---|
| Agent output inline instead of writing FIND.md | FIND.md created and populated in both tests |
| Free-form prose structure | Structured findings table enforced |
| Sources cited by name | File:line paths used (real sources) |
| Single-pass only | Iterations logged; multi-iteration loop demonstrated |
| Holistic saturation judgment | Mechanical counter + cap both worked |
| Prose open questions | `- [ ]` checkbox format with `- [x]` for resolved |
| No iteration log | Per-iteration entries in ## Iteration Log |

## REFACTOR decision: minimal

No new rationalizations or loopholes emerged from the GREEN tests. The skill's wording held up under both bounded iteration runs. Specifically:

- **Negative findings:** Agent handled a topic where the comparison was impossible. The skill didn't need special guidance for this — the structured format naturally accommodates negative-existence findings.
- **Template bootstrap entry:** Agent correctly kept the `iter 0` bootstrap entry from `template-FIND.md`, then appended iter 1. This matches the SKILL.md schema; no wording change needed.
- **Banner format:** Both bootstrap and DONE banners printed in the exact format specified.

**Minor possible enhancement (deferred):** The SKILL.md could explicitly say "negative findings are valid findings (a finding that X does not exist is still a finding)". But the agent already handled this correctly without the wording, so adding it would be overcorrection.

## Files shipped

- `/Users/sarace/dev/projects/skills/auto-research/SKILL.md` — main skill protocol
- `/Users/sarace/dev/projects/skills/auto-research/template-FIND.md` — starter template
- `/Users/sarace/dev/projects/skills/auto-research/tests/baseline/` — RED phase artifacts
- `/Users/sarace/dev/projects/skills/auto-research/tests/with-skill/FIND.md` — full 3-iter test artifact
- `/Users/sarace/dev/projects/skills/auto-research/tests/completion-test/FIND.md` — focused 1-iter test artifact
- `/Users/sarace/dev/projects/skills/auto-research/docs/superpowers/specs/2026-07-05-auto-research-design.md` — design spec

## Test 3 — Compaction pass (FIND.md stays bounded over long runs)

**Setup:** `delegate` subagent given SKILL.md + bounded `Iterations: 13`. Workspace: `tests/compaction-test/`. Pre-populated FIND.md with 12 findings + iter 12 logged; FIND-archive.md does not exist.

**Trigger conditions at start of iter 13:**
- `## Findings` has 12 entries (> 10 cap) ✓
- FIND.md is 3.7 KB (under 8 KB cap) ✗
- 13 iterations since last compaction (never compacted) ✓ (> 5)

Triggers 1 and 3 fire; size trigger doesn't.

**Result:** PASS — all 5 verification points satisfied.

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Compaction happens: 3 findings (4, 8, 12) demoted to FIND-archive.md; FIND.md stubs in place | PASS |
| 2 | `## Summary` rewritten to reflect only visible findings | PASS |
| 3 | Header line updated to `Iterations: 13 \| Status: capped` | PASS |
| 4 | Loop stops with status `CAPPED` | PASS |
| 5 | Final DONE banner: `findings: 10 visible (3 total in FIND-archive.md)` | PASS |

**Outcomes:**
- FIND.md after compaction: 4398 bytes (~4.3 KB), under the 8 KB cap.
- Visible full findings: 1, 2, 3, 5, 6, 7, 9, 10, 11, 13 (10 total).
- Archived: 4, 8, 12 (3 total, full text preserved in FIND-archive.md).
- Demotion rule applied correctly: lowest confidence first (`low` → `medium` → `high`), then oldest `Added` date.

**Observation:** Demoted findings stay in FIND.md as one-line stubs, interleaved with the full findings at their original chronological position. This preserves cross-references and chronological context without bloating the file.

## Skill ready for use.

The skill works as designed (now with bounded FIND.md via compaction pass).