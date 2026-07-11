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

This repo is structured as a **pi package** (see `package.json` with `pi-package` keyword and `pi.skills: ["./SKILL.md"]`). Install it with the documented `pi install` command — which writes to `~/.pi/agent/settings.json` through the proper code path, not by hand-editing:

```bash
pi install /Users/sarace/dev/projects/skills/auto-research
```

That's it. Restart pi, then `/skill auto-research` is available. Edits to files in this project are picked up on the next session — no reinstall needed.

To uninstall:

```bash
pi remove /Users/sarace/dev/projects/skills/auto-research
```

To see what's installed:

```bash
pi list
```

**Why a package, not a symlink or settings.json edit?** Pi's package system handles path resolution, dedup, and source tracking correctly. Symlinks work but show the wrong path in `<available_skills>` and dangle if the source moves. Hand-editing `settings.json` skips the install validation (path exists, manifest valid) and is what pi's docs explicitly tell you not to do.

**Other valid install paths** (per `packages.md`):

```bash
pi install npm:auto-research                 # if published to npm
pi install git:github.com/you/auto-research  # if published to a git repo
pi install ./relative/path                   # relative path
pi install -l /abs/path                      # install project-locally (.pi/settings.json)
```

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