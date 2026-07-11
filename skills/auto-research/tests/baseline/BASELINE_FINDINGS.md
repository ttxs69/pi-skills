# Baseline RED-phase findings

**Date:** 2026-07-05
**Test scenario:** Fresh-context `delegate` subagent given the research task and asked to write findings to FIND.md. No auto-research skill loaded.

## What the agent did

1. Read GOAL.md ✓
2. Confirmed web_search/fetch_content were NOT exposed in its environment ✗ (only read/write/edit/bash/grep/find/ls)
3. Wrote a comprehensive research synthesis from training-time knowledge ✓
4. **Did NOT write to FIND.md** ✗ — output the research inline as its response message
5. Wrote a separate notes file (`baseline-notes.md`) describing its process ✓

## Baseline failures to address in GREEN

| # | Failure | Severity | Skill must prevent by |
|---|---------|----------|----------------------|
| 1 | Agent output research inline instead of writing to FIND.md | Critical | Explicit "WRITE to FIND.md" instruction with the exact path + format spec |
| 2 | Structure was free-form prose with sections, not structured findings table | High | Provide template-FIND.md with exact schema |
| 3 | Sources cited by name, not by URL or file:line | High | Mandate structured Sources field per finding |
| 4 | Single-pass only, no iteration | High | Define iteration loop with explicit "do this N times" instruction |
| 5 | Saturation detection was holistic judgment, not a structured check | Medium | Define explicit "3 consecutive no-progress iterations = saturated" rule |
| 6 | Open questions tracked as prose, not checkboxes | Medium | Mandate `- [ ]` checkbox format |
| 7 | No iteration log — only the final output is preserved | Medium | Mandate `## Iteration Log` section appended each iteration |
| 8 | Web tools not available to the `delegate` agent | Tooling | Skill must be agent-agnostic; parent dispatches subagent with whatever tools are appropriate |

## What the agent did RIGHT (don't overcorrect)

- Used sectioned structure (executive summary → per-framework → comparison table → patterns → open questions). Useful pattern to retain.
- Explicitly disclosed "what I could not verify" — epistemic honesty. Keep this in the structure.
- Cautious about citation: refused to fabricate URLs. Skill should preserve this discipline.
- One-paragraph executive summary up top. Human readability wins.

## Implications for skill design

1. **Most critical:** the skill must be unambiguous about file writing. The parent owns all writes; the subagent returns a structured message. The subagent must NEVER claim "I wrote it" without verification.

2. **The skill must provide the FIND.md template explicitly.** Without a template, agents default to free-form prose sections.

3. **The iteration loop must be explicit.** Without it, agents stop after one pass.

4. **Saturation must be mechanically defined.** Otherwise the agent's "I'm done" is a vibe.

## Next step

Proceed to GREEN phase: write SKILL.md + template-FIND.md that addresses failures 1–7. Use a web-capable subagent (e.g., `researcher`) for the GREEN verification test so we can actually verify web research works end-to-end.