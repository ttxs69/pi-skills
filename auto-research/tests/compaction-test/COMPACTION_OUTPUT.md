# Compaction test output — iter 13

## Banners

Per-iteration banner (printed at start of iter 13):

```
[auto-research] goal: fetch_content vs ctx_fetch_and_index in pi-coding-agent | iter: 13/13 | saturation: 0/3
```

Final DONE banner (printed on stop):

```
[auto-research] DONE — status: capped | iterations: 13 | findings: 10 visible (3 total in FIND-archive.md) | open questions: 0
```

## Triggers that fired at iter 13

1. `## Findings` count > 10 (was 12 before this iter, becomes 13 → triggers compaction)
2. FIND.md size > 8 KB — did **NOT** fire (3.7 KB before, 4.3 KB after)
3. Iterations since last compaction > 5 (13 iterations, never compacted) — fired

## Compaction actions

- Demoted 3 findings (lowest-confidence + oldest-first): Finding 4 (medium, 2026-07-05), Finding 8 (low, 2026-07-05), Finding 12 (low, 2026-07-05).
- Appended demoted blocks verbatim to `FIND-archive.md` (new file) under headers `### Archived at iter 13 — Finding N`.
- Replaced demoted `### Finding N` blocks in `FIND.md` with one-line stubs preserving the finding number.
- Rewrote `## Summary` to reflect only the 10 currently visible full findings.
- Updated `## Archived Findings` to: `3 earlier findings → FIND-archive.md (last archived at iter 13)`.

## Files

- `FIND.md` — 4398 bytes, 10 visible full findings + 3 stub lines = 13 entries in `## Findings`.
- `FIND-archive.md` — 859 bytes (created), 3 demoted findings preserved verbatim.

## Verification

All 5 verification points from the task passed (see `COMPACTION_NOTES.md`).