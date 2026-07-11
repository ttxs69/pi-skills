# Research findings — fetch_content vs ctx_fetch_and_index in pi-coding-agent

_Started: 2026-07-05 | Last updated: 2026-07-05 | Iterations: 1 | Status: capped_

## Summary

The pi-coding-agent harness ships exactly seven built-in tools: `read`, `write`, `edit`, `bash`, `grep`, `find`, and `ls`. A direct recursive grep across the entire installed package (`/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/`) finds zero matches for either `fetch_content` or `ctx_fetch_and_index` — they are not implemented in source, declared in docs, or mentioned in examples. Because the named tools do not exist in this harness, there is nothing to compare; the open question is now where these names actually come from (a sibling harness or extension).

## Findings

### Finding 1 — The pi-coding-agent harness ships exactly seven built-in tools (`read`, `write`, `edit`, `bash`, `grep`, `find`, `ls`); neither `fetch_content` nor `ctx_fetch_and_index` is among them.
- Sources: file:/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/dist/core/tools/index.js:21 (line `export const allToolNames = new Set(["read", "bash", "edit", "write", "grep", "find", "ls"]);`)
- Confidence: high
- Added: 2026-07-05

### Finding 2 — Neither `fetch_content` nor `ctx_fetch_and_index` appears anywhere in the installed pi-coding-agent package: zero matches across the entire recursive grep of source (.js), docs (.md), and examples directories.
- Sources: file:/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/ (recursive grep returned 0 matches for both `fetch_content` and `ctx_fetch_and_index`)
- Confidence: high
- Added: 2026-07-05

## Open Questions
- [ ] Do `fetch_content` / `ctx_fetch_and_index` exist in a sibling harness (e.g., pi-mono, pi-subagents, Claude Code) or only in an unrelated tool family? If they exist elsewhere, what do they actually do?

## Iteration Log

- iter 0 (2026-07-05): bootstrap — created FIND.md from template-FIND.md
- iter 1 (2026-07-05): tool census — searched pi-coding-agent install for `fetch_content` / `ctx_fetch_and_index`; found neither; strongest finding is that pi-coding-agent ships exactly seven built-in tools and the two named tools are not among them.