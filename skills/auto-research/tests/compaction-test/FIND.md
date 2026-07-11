# Research findings — fetch_content vs ctx_fetch_and_index in pi-coding-agent

_Started: 2026-07-05 | Last updated: 2026-07-05 | Iterations: 13 | Status: capped_

## Summary

pi-coding-agent ships 7 built-in tools; neither fetch_content nor ctx_fetch_and_index is among them. The 10 most recent findings confirm the tools originate outside the core harness: extensions can register custom tools, but neither `ctx_*` system tools nor `fetch_content` are wired in by default. The remaining open question is whether any opt-in plugin ships them.

## Findings

### Finding 1 — The pi-coding-agent ships exactly seven built-in tools.
- Sources: file:/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/dist/core/tools/index.js:21
- Confidence: high
- Added: 2026-07-05

### Finding 2 — Neither fetch_content nor ctx_fetch_and_index is in the codebase.
- Sources: file:/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/ (recursive grep returned 0)
- Confidence: high
- Added: 2026-07-05

### Finding 3 — `read` is strictly local; no URL field.
- Sources: file:/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/dist/core/tools/read.js:17-19
- Confidence: high
- Added: 2026-07-05

- Finding 4 (archived → FIND-archive.md): `bash` is the only external-content path; no typed fetcher | confidence: medium | added: 2026-07-05

### Finding 5 — No FTS5 store, no local retrieval cache.
- Sources: file:/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/ (FTS5 grep returned 0)
- Confidence: high
- Added: 2026-07-05

### Finding 6 — Prompt cache fields exist but are token-accounting, not local storage.
- Sources: file:.../docs/custom-provider.md:146
- Confidence: medium
- Added: 2026-07-05

### Finding 7 — Tool descriptions limit `read` to text/image files.
- Sources: file:.../dist/core/tools/read.js:136
- Confidence: high
- Added: 2026-07-05

- Finding 8 (archived → FIND-archive.md): No `WebFetch` type in Anthropic SDK exports the harness uses | confidence: low | added: 2026-07-05

### Finding 9 — Extensions can register custom tools but cannot add `ctx_*` system tools.
- Sources: file:docs/extensions.md
- Confidence: medium
- Added: 2026-07-05

### Finding 10 — The `subagent` tool is an extension that wraps subagent invocation.
- Sources: file:examples/extensions/subagent/
- Confidence: medium
- Added: 2026-07-05

### Finding 11 — `mcp` extension can register tools via MCP servers.
- Sources: file:examples/extensions/mcp.ts
- Confidence: medium
- Added: 2026-07-05

- Finding 12 (archived → FIND-archive.md): Some users wrap `curl` in a `bash` tool to fetch external content | confidence: low | added: 2026-07-05

### Finding 13 — `fetch_content` / `ctx_fetch_and_index` belong to Claude Code's toolset, not pi-coding-agent.
- Sources: file:https://docs.claude.com/en/docs/claude-code/settings#tools-available-to-claude | file:/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/dist/core/tools/index.js:21
- Confidence: medium
- Added: 2026-07-05

## Archived Findings

3 earlier findings → FIND-archive.md (last archived at iter 13)

## Open Questions
- [x] Do fetch_content / ctx_fetch_and_index exist in pi-coding-agent? — Resolved: no.
- [x] Where do `fetch_content` and `ctx_fetch_and_index` actually come from? — Resolved: Claude Code's toolset (not in pi-coding-agent).

## Iteration Log

- iter 0 (2026-07-05): bootstrap — created FIND.md from template
- iter 1 (2026-07-05): tool census — searched install for named tools; found neither +3 findings
- iter 2 (2026-07-05): capability map — read tool descriptions +1 finding
- iter 3 (2026-07-05): index check — recursive grep for FTS5 returned 0 +1 finding
- iter 4 (2026-07-05): prompt cache vs local cache distinction +1 finding
- iter 5 (2026-07-05): read tool schema limits +1 finding
- iter 6 (2026-07-05): WebFetch absence +1 finding
- iter 7 (2026-07-05): extension capability limits +1 finding
- iter 8 (2026-07-05): subagent tool architecture +1 finding
- iter 9 (2026-07-05): MCP server extensions +1 finding
- iter 10 (2026-07-05): user workaround pattern (curl) +1 finding
- iter 11 (2026-07-05): confirmed no ctx_* system tools +1 finding
- iter 12 (2026-07-05): — no work done; awaiting next iter
- iter 13 (2026-07-05): origin attribution — confirmed tools belong to Claude Code, not pi-coding-agent +1 finding