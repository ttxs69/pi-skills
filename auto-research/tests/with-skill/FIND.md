# Research findings — fetch_content vs ctx_fetch_and_index in pi-coding-agent

_Started: 2026-07-05 | Last updated: 2026-07-05 | Iterations: 2 | Status: in-progress_

## Summary

_Empty. Will be rewritten after the first 5 iterations and on every stop._

## Findings

### Finding 1 — The pi-coding-agent harness ships exactly seven built-in tools (`read`, `bash`, `edit`, `write`, `grep`, `find`, `ls`); neither `fetch_content` nor `ctx_fetch_and_index` is among them.
- Sources: file:/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/dist/core/tools/index.js:23 (allToolNames Set)
- Confidence: high
- Added: 2026-07-05

### Finding 2 — Neither `fetch_content` nor `ctx_fetch_and_index` appears anywhere in pi-coding-agent's installed package: zero matches across source, docs, and examples.
- Sources: file:/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/ (recursive grep: 0 matches for `fetch_content` and 0 matches for `ctx_fetch_and_index` in .md/.ts/.js/.d.ts files)
- Confidence: high
- Added: 2026-07-05

### Finding 3 — pi-coding-agent has NO built-in HTTP/web fetch tool; the only built-in path for retrieving external content is the generic `bash` tool (e.g. `curl`/`wget` inside a shell command), which is untyped shell exec, not a structured fetcher.
- Sources: file:/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/dist/core/tools/bash.js:194 (tool description); file:/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/dist/core/tools/index.js:23 (allToolNames)
- Confidence: high
- Added: 2026-07-05

### Finding 4 — The `read` tool is strictly local: its schema is `{path: string, offset?: number, limit?: number}` with no URL field, and its description limits it to text and image files. There is no HTML→markdown conversion, no JSON chunking, and no token-aware summarisation step in the read pipeline.
- Sources: file:/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/dist/core/tools/read.js:17-19 (schema); file:/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/dist/core/tools/read.js:136 (tool description)
- Confidence: high
- Added: 2026-07-05

### Finding 5 — pi-coding-agent ships NO local FTS5 index, NO persistent retrieval cache, and NO `ctx_*` tools. A recursive grep for `FTS5` returned zero matches; the only `cache*` fields in the codebase are server-side prompt-cache accounting on provider/model definitions (`cacheRead`, `cacheWrite`, `cacheControlFormat`), not local retrieval storage.
- Sources: file:/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/ (recursive grep for `FTS5` / `fts5`: 0 matches); file:/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/docs/custom-provider.md:146,176,529 (cacheRead/cacheWrite fields are token-accounting, not local index); file:/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/docs/models.md:208,364,366,406 (same — prompt-cache knobs only)
- Confidence: high
- Added: 2026-07-05

## Open Questions
- [ ] Do `fetch_content` / `ctx_fetch_and_index` exist in some related harness (pi-mono, pi-subagents, Claude Code) rather than pi-coding-agent, and if so what do they do?
- [ ] What external-content capability does pi-coding-agent actually expose (e.g., `WebFetch` Anthropic SDK type, custom extensions, `bash` curl)?
- [x] What mechanisms does pi-coding-agent actually expose for fetching external web content? — Resolved: only `bash` (generic shell); no built-in HTTP tool, no `ctx_*` indexing tool, no FTS5 store.

## Iteration Log

- iter 0 (2026-07-05): bootstrap — created FIND.md from template
- iter 1 (2026-07-05): tool census — searched pi-coding-agent install for `fetch_content` / `ctx_fetch_and_index`; found neither; confirmed the seven built-in tools via `dist/core/tools/index.js`.
- iter 2 (2026-07-05): capability map — read tool descriptions for `bash` and `read`; grep'd `FTS5` and `WebFetch`. Strongest finding: pi has zero local retrieval cache/index; `bash` is the only fetch path; prompt-cache fields exist but are provider-side token accounting, not local storage.