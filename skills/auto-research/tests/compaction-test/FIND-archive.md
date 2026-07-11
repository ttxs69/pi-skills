# FIND archive — fetch_content vs ctx_fetch_and_index in pi-coding-agent

_Holds demoted findings from FIND.md, preserved verbatim for provenance. Append-only._

### Archived at iter 13 — Finding 4

### Finding 4 — `bash` is the only external-content path; no typed fetcher.
- Sources: file:/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/dist/core/tools/bash.js:194
- Confidence: medium
- Added: 2026-07-05

### Archived at iter 13 — Finding 8

### Finding 8 — No `WebFetch` type in Anthropic SDK exports the harness uses.
- Sources: file:node_modules/@anthropic-ai/sdk/...
- Confidence: low
- Added: 2026-07-05

### Archived at iter 13 — Finding 12

### Finding 12 — Some users wrap `curl` in a `bash` tool to fetch external content.
- Sources: https://github.com/earendil-works/pi-coding-agent/issues/42
- Confidence: low
- Added: 2026-07-05