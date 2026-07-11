---
name: auto-research
description: Use when you have a research goal to investigate autonomously over many iterations — the skill reads GOAL.md, dispatches a fresh-context subagent per iteration to answer one focused question, records structured findings with sources and confidence in FIND.md, and stops on saturation (3 consecutive no-progress iterations) or iteration cap. Triggers on "research this", "investigate", "find information about", "keep digging until covered", or any request for autonomous multi-iteration research with a persistent record. NOT for code modification (use autoresearch), single-pass Q&A, or tasks with a mechanical success predicate.
---

# Auto-Research — Autonomous Goal-Directed Research Loop

## Overview

A focused distillation of [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) — same loop shape (iterate, atomic steps, automatic stop), but redirected from **code modification against a metric** to **research with structured findings**.

You read `GOAL.md`, dispatch a fresh-context subagent per iteration to answer ONE focused question, append structured findings (claim + sources + confidence) to `FIND.md`, and stop on saturation or iteration cap.

**Core principle:** research is iteration, not a single pass. One subagent, one question, one finding (or a few). The parent owns all file writes; subagents return messages.

## When to Use

**Use when:**
- You have a research goal in `GOAL.md` (or want to define one) and want autonomous investigation
- The goal has no mechanical success predicate — saturation is the only completion signal
- You want a persistent, structured record of findings with sources and confidence
- You want both web and local files as research sources
- The research may take many iterations to complete

**Do NOT use when:**
- You want to modify code (that's autoresearch)
- You have a single research question with a known short answer (just ask directly)
- The task has a mechanical success predicate (e.g., "make tests pass")
- You want subjective-quality evaluation (no LLM-judge is involved; saturation is the only signal)
- You need git-as-memory (this skill does NOT touch git)

## State

Two files in the working directory. The split keeps `FIND.md` bounded regardless of run length.

### `GOAL.md`

Free-form markdown written by the user. The skill reads it verbatim. It does NOT parse structure — only checks existence and non-emptiness.

### `FIND.md` — current state (always small)

Structured markdown maintained by the skill. The parent reads this file **every iteration**. It is kept bounded via the **Compaction Pass** (Phase 4 step 5). Schema:

```markdown
# Research findings — <goal title from first H1 of GOAL.md>

_Started: <YYYY-MM-DD> | Last updated: <YYYY-MM-DD> | Iterations: N | Status: in-progress | saturated | capped | interrupted_

## Summary

<2–3 sentence prose synthesis. Rewritten EVERY iteration to stay current.>

## Findings

### Finding 1 — <one-line claim>
- Sources: <url> | <file:line>
- Confidence: high | medium | low
- Added: <YYYY-MM-DD>

### Finding 2 — <one-line claim>
- Sources: <url>
- Confidence: high | medium | low
- Added: <YYYY-MM-DD>

## Archived Findings

<One-line pointer, e.g., `37 earlier findings → see FIND-archive.md` (last archived at iter 18)>

## Open Questions
- [ ] <question the next iteration should answer>
- [x] <resolved question>

## Iteration Log

- iter 1 (<YYYY-MM-DD>): <one-line on what was researched and the strongest finding>
- iter 2 (<YYYY-MM-DD>): <one-line>
```

A starter template is at `template-FIND.md` — copy it if `FIND.md` does not exist.

### `FIND-archive.md` — full history (append-only)

Created on first compaction. Holds demoted findings in full so the parent never has to lose provenance. Each entry:

```markdown
### Archived at iter K — Finding M

(Full original `### Finding M — <claim>` block, verbatim, with all sources, confidence, and date)
```

The parent reads `FIND.md` every iteration. `FIND-archive.md` is **read on demand only** — when an open question references an archived finding, or when provenance must be verified.

## The Loop — 5 Phases

The parent agent runs phases 1, 2, 4, 5. Phase 3 runs in a fresh-context subagent.

### Phase 1 — Bootstrap

1. **Read `GOAL.md`.** If missing or empty → run the **Setup Wizard** (see below). If after the wizard the file is still empty → STOP with status `EMPTY_GOAL`.
2. **Read `FIND.md`.** If missing:
   - If `template-FIND.md` exists at the skill's path → copy it to `FIND.md`.
   - Else → create a minimal scaffold with empty `## Summary`, `## Findings`, `## Open Questions`, `## Iteration Log` sections, and the header line set to `Iterations: 0 | Status: in-progress`.
3. **Parse invocation for `Iterations: N`** (default 25) or `Iterations: unlimited`.
4. **Print the banner:**
   ```
   [auto-research] goal: <first line of GOAL.md> | iter: 0/<max> | saturation: 0/3
   ```

### Setup Wizard (when GOAL.md is missing)

Ask 1–3 questions in a single `ask_user_question` batch:

- **Q1 (Goal):** "What do you want to research?" — free-text or refined choice.
- **Q2 (Scope):** "Any frameworks, time windows, or domains to focus on / exclude?"
- **Q3 (Format):** "Any preference on output style?" (default: structured findings table)

Then write `GOAL.md` from the answers using the same free-form markdown style as the user would. Proceed immediately to phase 2.

### Phase 2 — Reflect (parent)

1. Read `FIND.md` end-to-end. Identify what's known and what's missing.
2. Decide the **next research focus** as 1–3 specific questions. Pick the **single most important one** for this iteration. Don't pick questions already in `## Open Questions` unless re-prioritizing (and remove the old one if re-prioritized).
3. **Saturation check:**
   - Maintain a **consecutive no-progress counter** in memory. Starts at 0.
   - Inspect the LAST completed iteration in `## Iteration Log`:
     - If that iteration added ≥1 finding to `## Findings` → counter = 0.
     - Else → counter += 1.
   - If counter ≥ 3 → STOP with status `SATURATED`.
4. **Cap check:** if iteration count ≥ max → STOP with status `CAPPED`.
5. **Print the banner** with the updated iter counter and saturation counter.
6. Otherwise proceed.

### Phase 3 — Research (subagent, fresh context)

Dispatch a subagent using the **Subagent Task Template** below. The subagent has access to `web_search`, `fetch_content`, `read`, `grep`, `glob`, `bash`. The subagent does **NOT** write to any files — it returns findings as its message.

Wait for the subagent's response. Do not interleave writes between subagent calls.

### Phase 4 — Record (parent)

1. Parse the subagent's response. It should contain 1–3 findings in the structured format (claim + sources + confidence).
2. **If findings are well-formed:**
   - For each finding, append a `### Finding N — <claim>` block to `## Findings` with sources, confidence, date. Increment N from the last finding's number (never reuse a number).
   - For each new open question returned, append `- [ ] <question>` to `## Open Questions`.
   - Mark resolved questions with `- [x]` (move them down or strike through).
   - Append one line to `## Iteration Log`: `- iter <N> (<date>): <one-line on what was researched and the strongest finding>` — include the count of findings added, e.g. `+2 findings`.
   - Update the header line: `Iterations: N | Status: in-progress`.
   - Counter is reset to 0 by phase 2 next iteration (since this iter produced ≥1 finding).
3. **If findings are malformed** (no sources, no confidence, or off-topic):
   - Do NOT append to `## Findings`.
   - Append to `## Iteration Log`: `- iter N (<date>): malformed — <reason>`.
   - Counter is **NOT** incremented (malformed ≠ no-progress; the question may still be valid).
   - **Iteration DOES count toward the cap** (a malformed iteration is still an iteration).
4. **EVERY iteration** AND on stop: rewrite `## Summary` as a 2–3 sentence synthesis of the most important findings currently visible in `## Findings` (do NOT include archived findings). Keep it tight — the summary is what the parent scans first.
5. **Compaction pass** (check EVERY iteration; act only when a trigger fires):
   - **Triggers (any one):**
     - `## Findings` has more than 10 entries
     - `FIND.md` size exceeds 8 KB
     - 5 iterations have elapsed since the last compaction
   - **Action:**
     a. Pick demotion candidates from `## Findings`. Order: lowest confidence first (`low` → `medium` → `high`), then oldest `Added: <date>` first. Keep the most recent 10 (or fewer, if a smaller cap better satisfies the size trigger).
     b. For each demoted finding, append to `FIND-archive.md` with header `### Archived at iter K — Finding M` followed by the full original block (claim + sources + confidence + date), verbatim.
     c. If `FIND-archive.md` does not exist, create it with a header: `# FIND archive — <goal title>` and a one-line note explaining it holds demoted findings.
     d. In `FIND.md`, replace each demoted `### Finding M` block with a single-line stub: `- Finding M (archived → FIND-archive.md): <one-line claim> | confidence: <level> | added: <date>`. Keep the finding number to preserve cross-references.
     e. Update the `## Archived Findings` section header line with the current count: `<N> earlier findings → FIND-archive.md (last archived at iter K)`.
     f. Rewrite `## Summary` to reflect only currently visible findings.
   - **What compaction does NOT change:** finding numbers (preserved for cross-reference), the cumulative archive (always append, never delete), the iteration log entry that referenced the finding.

### Phase 5 — Loop or Stop

Go to Phase 2 unless one of:
- Saturation counter ≥ 3 → stop with status `SATURATED`.
- Iteration count ≥ max → stop with status `CAPPED`.
- User interrupt (Ctrl+C, message saying "stop", etc.) → stop with status `INTERRUPTED`.

**On stop:**
1. Run one final compaction pass (Phase 4 step 5) so `FIND.md` is tidy.
2. Rewrite `## Summary` (see Phase 4 step 4).
3. Update the header line: `Status: <final status>`.
4. Print the final banner:
   ```
   [auto-research] DONE — status: <status> | iterations: N | findings: M visible (T total in FIND-archive.md) | open questions: K
   ```

## Subagent Task Template

Use this exact template when dispatching a research subagent. Fill in the placeholders.

```
You are researching ONE focused question as part of an auto-research loop.
You have fresh context. You will return findings as your message; you will NOT write to any files.

## Goal (full text of GOAL.md)
<contents of GOAL.md verbatim>

## Findings so far (full text of FIND.md)
<contents of FIND.md verbatim>

## Your question for this iteration
<the single question chosen by the parent>

## Your job
1. Use web_search, fetch_content, read, grep, glob, and bash to investigate.
2. Investigate ONLY this question. Do not expand scope.
3. Return: 1–3 new findings in this exact format:

   Finding: <one-line claim>
   Sources: <url> | <url> | <file:line>
   Confidence: high | medium | low

   (Repeat for each finding, separated by blank lines.)

4. Also return any new open questions you discovered while researching:
   Open question: <question>

## Quality bar
- Every claim MUST cite a source. If you cannot find a source, do not include the claim.
- No speculation. If sources disagree, return the disagreement as a finding rather than picking a side.
- DO NOT write to any files. Your message IS the output.
```

## Saturation Heuristic

**Definition:** Three consecutive iterations that produced zero net-new findings.

**Mechanics:**
- The consecutive no-progress counter lives in the parent's working memory.
- At the START of each phase 2 (before dispatching the subagent), inspect the LAST completed iteration's `## Iteration Log` entry.
- Count "findings added" as the number reported in the log entry (added by the subagent during that iter), NOT the net change to `## Findings` after compaction. A finding added and then immediately archived in the same iter still counts as progress — the iteration produced new knowledge.
- A "progress" iteration added ≥1 finding. Reset counter to 0.
- A "no-progress" iteration added 0 findings. Increment counter.
- A "malformed" iteration does NOT change the counter.
- Counter ≥ 3 → STOP with status `SATURATED`.

**Why three:** Two false-positives are common (transient bad question). Four delays legitimate exit. Three is the sweet spot.

**Note on compaction interaction:** Compaction moves findings OUT of `FIND.md` and INTO `FIND-archive.md`. This does NOT affect saturation — the iteration still produced those findings; they just got demoted to keep `FIND.md` small. The counter only resets based on what was added in the iter, regardless of where it lives now.

## Tools Used

**Parent agent (loop controller):**
- `read`, `write`, `edit` — read GOAL.md, maintain FIND.md and FIND-archive.md
- `ask_user_question` — setup wizard when GOAL.md is missing
- `bash` — print banners, parse iteration counts, check file size for compaction trigger (no other shell use)

**Subagent (per iteration):**
- `web_search` — external research
- `fetch_content` / `ctx_fetch_and_index` — pull full web content
- `read`, `grep`, `glob` — inspect local files
- `bash` — local file inspection (no destructive commands)

**Explicitly forbidden in subagent:** `write`, `edit`. The parent owns all file mutation. This prevents the subagent from racing the parent on FIND.md.

## Invocation

```
/skill auto-research
```

Optional inline overrides in the same message:
- `Iterations: N` — set explicit cap (default 25).
- `Iterations: unlimited` — no cap (loop until saturated or user stops).

The skill does not currently accept scope flags (web-only, local-only) — those are future enhancements.

## Common Mistakes

| Mistake | Why it breaks the skill | Fix |
|---|---|---|
| Subagent writes to FIND.md | Race condition with parent; double-writes; lost updates | Subagent returns findings as message only. Parent owns writes. |
| Parent skips Phase 2 reflect | Picks the same question twice; loop stalls | Always read FIND.md and pick a NEW or re-prioritized question |
| Parent doesn't update header line | Iteration count drifts; saturation check breaks | Update `Iterations: N \| Status: ...` after every phase 4 |
| Parent forgets to print banner | User can't tell if the loop is making progress | Print at bootstrap and at the start of every iteration |
| Parent fabricates findings when subagent returns nothing | "I'm done" isn't a real finding | If subagent returns zero findings, log as no-progress, do NOT invent |
| Parent stops after one iteration because "looks good" | Defeats the entire iteration loop | Always check saturation AND cap, not subjective judgment |
| Findings lack sources or confidence | The whole point of structured findings is traceability | Reject malformed findings; log as malformed; do not append |
| Parent skips compaction pass | FIND.md grows unbounded; re-read cost grows linearly with iteration count | Run compaction check EVERY iteration; act when triggers fire (count > 10, size > 8 KB, or every 5 iters) |
| Parent deletes findings instead of archiving | Loses provenance; can't audit the research path | Always APPEND demoted findings to FIND-archive.md; never delete |

## Quick Reference

**Banner formats:**

Bootstrap / per-iteration:
```
[auto-research] goal: <first line of GOAL.md> | iter: N/<max> | saturation: K/3
```

Final (on stop):
```
[auto-research] DONE — status: <status> | iterations: N | findings: M | open questions: K
```

**Exit statuses:**
- `SATURATED` — 3 consecutive no-progress iterations
- `CAPPED` — iteration count ≥ max
- `INTERRUPTED` — user stopped
- `EMPTY_GOAL` — setup wizard did not produce a usable goal

**Per-iteration mechanics:**
- Read FIND.md → pick question → dispatch subagent → record → loop or stop.
- Counter resets to 0 on any progress iteration.
- Malformed iterations count toward cap but not toward saturation.

**File ownership:**
- Parent: writes to FIND.md and FIND-archive.md exclusively. Compaction is the parent's job.
- Subagent: returns findings as message only.
- Both: read GOAL.md and FIND.md (parent reads to plan, subagent reads to ground itself). FIND-archive.md is read on demand only — when an open question references an archived finding.

**Compaction triggers (any one):**
- `## Findings` count > 10
- FIND.md size > 8 KB
- 5 iterations since last compaction

**Compaction rule:**
- Demote lowest-confidence, oldest-date findings first.
- Append to FIND-archive.md (full text). Never delete.
- In FIND.md, replace each demoted block with a one-line stub preserving the finding number.
- Rewrite `## Summary` to reflect only currently visible findings.