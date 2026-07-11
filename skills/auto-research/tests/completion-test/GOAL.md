# Research goal

Investigate the differences between `fetch_content` and `ctx_fetch_and_index`
in the pi-coding-agent harness. Focus on when each is the right choice.

## Scope
- Token economics (per-call vs cached)
- Content fidelity (markdown conversion, code blocks, JSON chunking)
- Index persistence (FTS5 storage, retrieval)

## Out of scope
- Other ctx_* tools
- web_search specifics