# auto-research

A focused distillation of [Karpathy's autoresearch](https://github.com/karpathy/autoresearch): autonomous, multi-iteration research with structured findings — no code modification, no metric, no git. Just a goal, an iteration loop, and a saturation check.

## What it does

You write a research goal in `GOAL.md`. The skill reads it, dispatches a fresh-context subagent per iteration to answer one focused question, appends structured findings (claim + sources + confidence) to `FIND.md`, and stops on saturation (3 consecutive no-progress iterations) or iteration cap.

## Files

```
auto-research/
├── SKILL.md              # The skill protocol — read this to understand the loop
├── template-FIND.md      # Starter template for FIND.md
└── tests/
    ├── baseline/         # RED-phase: what an agent does WITHOUT the skill
    ├── with-skill/       # GREEN-phase: 3-iter run, killed by timeout mid-iter-3
    ├── completion-test/  # Focused 1-iter test for completion behaviors
    ├── BASELINE_FINDINGS.md
    └── GREEN_FINDINGS.md
```

## Quick start

```
/skill auto-research
```

If `GOAL.md` exists in the current directory, the skill reads it and starts. Otherwise it runs an interactive setup wizard (1–3 questions) and writes `GOAL.md` for you.

Optional inline overrides:
- `Iterations: N` — set explicit cap (default 25).
- `Iterations: unlimited` — no cap (loop until saturated or user stops).

## Install (pi-coding-agent)

Pi's documented pattern for loading skills from a specific path is `settings.json`'s `skills` array, not symlinks. Symlinks work but cause confusion (the `<location>` in the system prompt shows the symlink path, not the real file), and they break silently if the source moves.

Add to `~/.pi/agent/settings.json`:

```json
{
  "skills": [
    "/Users/sarace/dev/projects/skills/auto-research"
  ]
}
```

The path can be a directory containing `SKILL.md` (pi discovers it as a skill root) or a single `.md` file. Directory is preferred — it lets `SKILL.md` reference sibling files like `template-FIND.md` via relative paths.

Restart pi, then `/skill auto-research` becomes available. Edits to files in this project are picked up on the next session — no reinstall needed.

To uninstall, remove the entry from `skills`.

**Other valid install locations** (per pi docs):

| Location | Scope | Trust required |
|---|---|---|
| `~/.pi/agent/skills/<name>/SKILL.md` | global (auto-loaded, no settings entry) | no |
| `~/.agents/skills/<name>/SKILL.md` | global (alternative) | no |
| `<cwd>/.pi/skills/<name>/SKILL.md` | project | yes |
| `<cwd>/.agents/skills/<name>/SKILL.md` | project | yes |
| `settings.json` → `skills: ["…"]` | global (explicit path) | no |
| CLI: `--skill <path>` | per-invocation | no |

For a skill under active development in a project repo, the `settings.json` approach is the cleanest — path is explicit, no indirection, no breakage if either side moves.

## How it differs from autoresearch

| autoresearch | auto-research |
|---|---|
| Optimize code against a metric | Research and discover |
| Mechanical success predicate | Saturation detection |
| Git-as-memory (commits, diffs) | FIND.md as memory |
| Atomic code changes | Atomic research questions |
| Modify → verify → keep/discard | Reflect → research → record |

Both share the same loop shape: iterate, atomic steps, automatic stop.

## See also

- [Design spec](docs/superpowers/specs/2026-07-05-auto-research-design.md) — full design rationale
- [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) — the inspiration
- [Claude Autoresearch](https://github.com/uditgoenka/autoresearch) — the code-optimization cousin this was distilled from