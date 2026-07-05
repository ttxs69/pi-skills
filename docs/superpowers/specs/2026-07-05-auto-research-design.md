# Auto-Research Skill — Design Spec

**Date:** 2026-07-05
**Status:** Draft (awaiting user review)
**Author:** Brainstorming session with user

## Summary

A new pi skill, `auto-research`, that autonomously investigates a research goal expressed in `GOAL.md` and accumulates structured findings in `FIND.md`. The loop reads both files each iteration, dispatches a fresh-context subagent to fill the next open question, appends findings, and stops on saturation or iteration cap.

The skill is a focused distillation of [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) — same loop shape (iterate until done, atomic steps, automatic stop), but redirected from **code modification against a metric** to **research with structured findings**. No git, no commits, no mechanical success predicate.

## Goals

- Provide a single-file interface (`GOAL.md` + `FIND.md`) for autonomous research over long horizons.
- Stay out of the way of the user's existing tooling — no git coupling, no daemon, no hooks.
- Produce a FIND.md that is readable both by humans (prose summary at top) and by agents (structured findings table).
- Detect saturation automatically so the loop ends naturally when research is exhausted.

## Non-goals

- Code modification. That is the existing autoresearch project's job.
- Git-as-memory. FIND.md is the sole persistent memory.
- Multi-command surface (no `:debug`, `:fix`, `:web`, `:local` variants). Single-purpose skill.
- Subjective-quality evaluation (no LLM-judge, no convergence-on-debate). Saturation is the only quality signal.
- Hooks, safety scripts, or session notifications. The skill does not touch git, push, deploy, or run destructive commands.

## Architecture

```
/Users/sarace/dev/projects/skills/auto-research/
├── SKILL.md              # Full protocol (single file, ~300 lines)
└── template-FIND.md      # Optional starter template for empty FIND.md
```

**Approach chosen:** Single SKILL.md with the full loop protocol inline. The state is just two markdown files; no JSON ledger, no handoffs. Modularization can be added later if subcommands appear.

## State

Two files in the user's working directory:

### `GOAL.md`

Free-form markdown. The user writes what they want researched. Examples:

```markdown
# Research goal

Investigate how modern LLM agent frameworks handle context-window
management in long-horizon tasks. Focus on the last 18 months.

## Scope
- Frameworks: LangChain, LlamaIndex, OpenAI Assistants, Anthropic SDK
- Exclude: research-only prototypes, closed-source agent platforms

## Out of scope
- Pure RAG chunking strategies (covered in earlier research)
```

The skill reads GOAL.md verbatim each iteration. It does not parse or validate structure — only the existence and non-emptiness of the file.

### `FIND.md`

Structured markdown. Maintained by the skill. Schema:

```markdown
# Research findings — <goal title>

_Started: <date> | Last updated: <date> | Iterations: N | Status: in-progress | saturated | capped | interrupted_

## Summary

<2–5 sentence prose synthesis of the most important findings so far,
written for a human reader. Updated every 5 iterations or on exit.>

## Findings

### Finding 1 — <one-line claim>
- Sources: <url> | <file:line>
- Confidence: high | medium | low
- Added: <date>

### Finding 2 — <one-line claim>
- Sources: <url>
- Confidence: high | medium | low
- Added: <date>

## Open Questions
- [ ] <question the next iteration should answer>
- [ ] <another open question>

## Iteration Log

- iter 1 (<date>): <one-line on what was researched and why>
- iter 2 (<date>): <one-line>
```

The skill maintains:
- `## Findings` — append-only, never reorders or rewrites.
- `## Open Questions` — agent adds new questions and checks off resolved ones.
- `## Iteration Log` — append one line per iteration.
- `## Summary` — rewritten on exit and every 5 iterations (humans skim this first).

## Loop protocol

Five phases, executed by the parent agent. Phase 3 runs in a subagent.

### Phase 1 — Bootstrap (parent)

1. Read `GOAL.md`. If missing or empty → run setup wizard:
   - Ask 1–3 quick questions (what to research, scope, format preference).
   - Write `GOAL.md` from the answers.
   - Proceed.
2. Read `FIND.md`. If missing → copy `template-FIND.md` if present, else create a minimal scaffold with empty sections.
3. Parse `Iterations: N` (default 25) or `Iterations: unlimited` from the invocation, if present. Otherwise use default.
4. Print banner (now and at the start of every iteration): `[auto-research] goal: <first line of GOAL.md> | iter: N/<max> | saturation: K/3`.

### Phase 2 — Reflect (parent)

1. Read `FIND.md` end-to-end. Identify what's already known and what's missing.
2. Decide the **next research focus** as 1–3 specific questions that, if answered, would materially advance the goal. Pick the single most important one for this iteration. Do not pick questions already in `## Open Questions` unless re-prioritizing.
3. **Saturation check:**
   - Maintain a **consecutive no-progress counter**. Starts at 0.
   - At the start of each iteration, inspect the LAST completed iteration in `## Iteration Log`.
   - If that iteration produced zero net-new findings in `## Findings` → counter += 1.
   - Else (it produced ≥1 finding) → counter = 0.
   - If counter ≥ 3 → stop with status `SATURATED`.
4. **Cap check:** if iteration count ≥ max → stop with status `CAPPED`.
5. Otherwise proceed.

### Phase 3 — Research (subagent, fresh context)

Dispatch a subagent with this exact task:

> You are researching one focused question as part of an auto-research loop.
>
> **Goal (full text of GOAL.md):**
> <contents of GOAL.md>
>
> **Findings so far (full text of FIND.md):**
> <contents of FIND.md>
>
> **Your question for this iteration:**
> <the single question chosen by the parent>
>
> **Your job:**
> 1. Use web_search, fetch_content, read, grep, glob, and bash to investigate.
> 2. Return: 1–3 new findings (claim + sources + confidence: high/medium/low), and any new open questions you discovered.
> 3. DO NOT modify any files. Return your findings as your message.
>
> **Quality bar:** every claim must cite a source. No speculation. If sources disagree, return the disagreement as a finding rather than picking a side.

The subagent has fresh context. The parent receives the subagent's message verbatim.

### Phase 4 — Record (parent)

1. Parse the subagent's message. For each finding:
   - Append a `### Finding N — <claim>` block to `## Findings` in FIND.md with sources, confidence, date.
   - Increment N from the last finding's number (never reuse a number).
2. For each new open question returned → append `- [ ] <question>` to `## Open Questions`.
3. Mark resolved open questions with `- [x]`.
4. Append one line to `## Iteration Log`: `- iter <N> (<date>): <one-line on what was researched and the strongest finding>`.
5. Update the header line: `Iterations: N | Status: in-progress`.

### Phase 5 — Loop or stop

Go to Phase 2 unless:
- Saturation counter ≥ 3 → stop with status `SATURATED`.
- Iteration count ≥ max → stop with status `CAPPED`.
- User interrupts (Ctrl+C, message saying "stop") → stop with status `INTERRUPTED`.

**On stop:**
1. Rewrite `## Summary` in FIND.md as a 2–5 sentence synthesis of the most important findings.
2. Update header line: `Status: <final status>`.
3. Print final banner with iteration count, finding count, open-question count, final status.

## Saturation heuristic

Detects "research is exhausted" by inspecting `## Iteration Log`:

- A **net-new finding** = any finding added in `## Findings` during the iteration.
- An iteration that produced **zero** net-new findings is a no-progress iteration.
- **Saturated** = three consecutive no-progress iterations.

Why this works: a focused subagent given a well-chosen question usually returns at least one new finding. Three consecutive failures to do so is strong evidence the open questions are stale, off-topic, or the goal is fully covered.

Why three (not two or four): two false-positives are common (a transient bad question); four delays legitimate exit. Three is the sweet spot used by autoresearch's saturation loops.

## Tools used

**Parent agent (loop controller):**
- `read`, `write`, `edit` — read GOAL.md, maintain FIND.md
- `ask_user_question` — setup wizard when GOAL.md is missing
- `bash` — print banner, count iterations (no other shell use)

**Subagent (per iteration):**
- `web_search` — external research
- `fetch_content` / `ctx_fetch_and_index` — pull full web content
- `read`, `grep`, `glob` — inspect local files
- `bash` — local file inspection (no destructive commands)

**Explicitly forbidden in subagent:** `write`, `edit` (parent owns all file mutation). This prevents the subagent from racing the parent on FIND.md.

## Invocation

```
/skill auto-research
```

Optional inline overrides:
- `Iterations: N` — set explicit cap (default 25).
- `Iterations: unlimited` — no cap (loop until saturated or user stops).

The skill does not currently accept scope flags (web-only, local-only) — those are future enhancements. The design supports adding them as Phase-3 subagent-task modifiers if needed.

## Failure modes and recovery

| Failure | Response |
|---|---|
| `GOAL.md` empty after setup wizard | Stop with `EMPTY_GOAL`. Tell user the wizard did not produce a usable goal. |
| Subagent returns no findings (genuine dead-end) | Treated as no-progress iteration. Saturation counter increments. |
| Subagent returns malformed output (no sources, no confidence, or off-topic) | Parent discards the subagent's output, does NOT append to `## Findings`, does NOT append a normal line to `## Iteration Log` (instead appends `- iter N (date): malformed — <reason>`). **Counts toward the iteration cap** (a malformed iteration is still an iteration) but **does NOT count toward saturation** (malformed ≠ no-progress; the question may still be valid). |
| `FIND.md` accidentally corrupted between iterations | Parent re-creates from template (data loss is acceptable — FIND.md is regenerable from sources cited in any preserved copy). |
| User edits GOAL.md mid-loop | Allowed. Parent re-reads GOAL.md each iteration. The skill continues toward the updated goal. |
| Two parallel invocations on same GOAL.md | Allowed but warn — both will append to FIND.md and may produce duplicate findings. Saturation detection degrades (duplicate entries are not net-new). Document this in the skill as a caveat. |

## Test plan (writing-skills RED phase)

Per `superpowers:writing-skills`, before deploying the skill we run baseline scenarios without the skill to identify rationalizations and gaps, then with the skill to verify compliance.

**Baseline scenarios (without skill):**
1. "Research <topic> and write findings to FIND.md" — does the agent produce structured findings or free-form prose? Does it iterate or stop after one pass?
2. "Keep researching <topic> until you've covered all the angles" — does the agent detect saturation or run forever?
3. "Read GOAL.md and FIND.md, plan next research" — does the agent choose good follow-up questions or just keep researching the same angle?

**Targeted compliance scenarios (with skill):**
1. Setup wizard: invoke with no GOAL.md present → expect a wizard, then a written GOAL.md, then the loop starting.
2. Structured FIND.md: after 2 iterations, FIND.md should have populated `## Findings` with sources + confidence, `## Open Questions`, and `## Iteration Log`.
3. Saturation: after 3 no-progress iterations, the loop stops with `SATURATED` status.
4. Subagent isolation: subagent must return findings without writing files. Verify parent owns all writes.
5. Banner: every iteration prints the banner with iter counter and saturation counter.

## Out-of-scope (won't ship in v1)

- Subcommands (e.g., `/auto-research:web`, `/auto-research:local`).
- Multiple FIND.md files per project.
- Cross-session memory (FIND.md lives in cwd; deleting cwd loses memory).
- Hooks or session notifications.
- Git integration (no commits, no version history beyond FIND.md's own log).
- Quality-judge loops (no LLM-judge ranking of findings — saturation is the only quality signal).

## Future enhancements (v2 candidates)

- **Scope flags:** `--web-only`, `--local-only`, `--budget <N>` for token cost control.
- **Citation validation:** subagent re-verifies sources before parent appends (catches hallucinated URLs).
- **FIND.md export:** convert findings to a different format (CSV, JSON) for downstream tooling.
- **Goal refinement:** detect when GOAL.md is vague and prompt the user to tighten scope.
- **Multi-FIND:** support parallel research streams writing to different FIND.md files.

## Risks

1. **Token cost:** each subagent starts cold. For research that touches many sources, the per-iteration cost can be substantial. Mitigation: keep iterations focused (one question each) and let saturation end the loop fast.
2. **Hallucinated citations:** LLM subagents may invent plausible-looking URLs. Mitigation: instructions require `fetch_content` to confirm before citing; v2 may add a verifier step.
3. **Saturation misfire:** three consecutive no-progress iterations may fire prematurely if the goal is genuinely hard. Mitigation: the cap provides a hard backstop; the user can re-prompt to keep going.
4. **Parallel-invocation corruption:** two loops writing to the same FIND.md will produce noisy output. Mitigation: documented caveat; v2 may add file-level locking.