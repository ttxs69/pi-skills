# Repo-as-Pi-Package Rebase — Design Spec

**Date:** 2026-07-11
**Status:** Draft (awaiting user review)
**Author:** Brainstorming session with user

## Summary

Restructure this repository so the **repo root** is a single installable pi package, instead of the current arrangement where only `auto-research/` is its own pi-package subdirectory. The change moves the `auto-research/` skill into a top-level `skills/` convention directory, adds a root `package.json` with the `pi-package` keyword, and rewrites both READMEs so the repo reads as "the package" rather than "a folder that happens to contain one."

After this change, `pi install /Users/sarace/dev/projects/skills` installs everything in the repo. The previously-documented `pi install .../auto-research` command becomes a no-op (no manifest at that path anymore) and is replaced by the root install.

## Motivation

The repo today is structurally confused:

- The git root (`/Users/sarace/dev/projects/skills`) is not a package.
- `auto-research/` is a package but is named the same as its sole skill, which conflates "the package" with "one of possibly many skills inside it."
- Adding a second skill today would require deciding between (a) another sub-package alongside `auto-research/`, or (b) breaking the existing install path.

Rebasing to a convention layout at the repo root makes adding new skills a one-directory change and gives the repo a stable install identity (`pi-skills`).

## Non-goals

- Publishing to npm or pushing to a git remote. Install is local-path only (`pi install <abs-path>`).
- Restructuring `docs/`. The design spec under `docs/superpowers/specs/2026-07-05-auto-research-design.md` is a historical artifact and is not edited by this change.
- Changing the `auto-research` skill protocol itself. SKILL.md, template-FIND.md, and tests move verbatim.
- Adding or removing skills. After this change the repo still ships exactly one skill.

## Target layout

```
/Users/sarace/dev/projects/skills/
├── package.json                              # NEW — root pi-package manifest
├── README.md                                 # NEW — repo landing page
├── docs/
│   └── superpowers/specs/
│       ├── 2026-07-05-auto-research-design.md
│       └── 2026-07-11-pi-package-rebase-design.md  # THIS FILE
└── skills/
    └── auto-research/
        ├── SKILL.md                          # moved from auto-research/
        ├── template-FIND.md                  # moved from auto-research/
        ├── README.md                         # moved + edited from auto-research/
        └── tests/                            # moved from auto-research/
            ├── baseline/
            ├── with-skill/
            ├── compaction-test/
            ├── completion-test/
            └── GREEN_FINDINGS.md
```

## File moves (concrete)

| Source | Destination | Notes |
|---|---|---|
| `auto-research/SKILL.md` | `skills/auto-research/SKILL.md` | verbatim |
| `auto-research/template-FIND.md` | `skills/auto-research/template-FIND.md` | verbatim |
| `auto-research/README.md` | `skills/auto-research/README.md` | edit: install path updates from `.../skills/auto-research` → `.../skills` |
| `auto-research/tests/**` | `skills/auto-research/tests/**` | verbatim, all four subdirs plus `GREEN_FINDINGS.md` |
| `auto-research/package.json` | (deleted) | superseded by root manifest |
| `auto-research/` (now empty) | (removed) | `git rm` of the directory |

Tests live inside the skill directory because they are RED/GREEN artifacts tightly coupled to this skill's behavior. Future skills would get their own `skills/<name>/tests/` — there is no top-level `tests/` in the target layout.

## Root `package.json`

```json
{
  "name": "pi-skills",
  "version": "0.1.0",
  "description": "Collection of pi skills — currently bundles auto-research.",
  "keywords": [
    "pi-package",
    "skill",
    "auto-research"
  ],
  "type": "module",
  "license": "MIT",
  "pi": {
    "skills": ["./skills"]
  }
}
```

**Field rationale:**

- `name: "pi-skills"` — signals "this is a pi skills collection," avoids the generic `skills` which would collide if anyone npm-installed it. Easy to rename later (single field).
- `version: "0.1.0"` — matches the version that was on `auto-research/package.json` before deletion.
- `keywords: ["pi-package", ...]` — `pi-package` is the gallery index keyword; the rest are search hints.
- `type: "module"` — matches the deleted `auto-research/package.json`.
- `license: "MIT"` — matches the deleted `auto-research/package.json`.
- `pi.skills: ["./skills"]` — explicit, even though the convention layout auto-discovers. Belt-and-suspenders: works even if convention paths change. The array supports glob patterns, so future additions can use `./skills/*/SKILL.md`-style selectors without renaming this.

## README updates

### Root `README.md` (NEW)

Sections, in order:

1. **What this is** — one paragraph: a pi skills package; install gives you `/skill <name>` for each skill under `skills/`.
2. **Install** — `pi install /Users/sarace/dev/projects/skills` with a one-line note about why this is a package rather than a symlink or hand-edited settings.json.
3. **Layout** — the directory tree above, annotated with which dirs are pi-discoverable.
4. **Skills** — list of skills with one-line summaries and links to their per-skill READMEs. Today: just `auto-research`.

### `skills/auto-research/README.md` (moved + edited)

All existing content preserved. **One edit:** the install command changes from:

```
pi install /Users/sarace/dev/projects/skills/auto-research
```

to:

```
pi install /Users/sarace/dev/projects/skills
```

The "Other valid install paths" section is kept as-is (it's still accurate at the repo level).

## Verification

Run all of these after implementation. Do not claim "done" until every step passes.

1. **Pre-install state** — `pi list` does NOT show `pi-skills`.
2. **Install** — `pi install /Users/sarace/dev/projects/skills` exits 0.
3. **Post-install state** — `pi list` shows `pi-skills` with source path `/Users/sarace/dev/projects/skills`.
4. **Skill registration** — starting pi shows `auto-research` in `<available_skills>` and `/skill auto-research` is invocable.
5. **No manifest at the old path** — `cat /Users/sarace/dev/projects/skills/auto-research/package.json` fails (path no longer exists).
6. **Git diff sanity** — `git status` shows: (a) `auto-research/` deleted, (b) `skills/auto-research/` created with the same file contents, (c) `package.json` added at root, (d) two READMEs in expected states. No stray files.
7. **Protocol regression** — re-run a small slice of `skills/auto-research/tests/GREEN_FINDINGS.md`-style iteration to confirm the skill still produces the same outputs after the move (e.g. the `compaction-test` or `completion-test` fixtures if they're quick to execute).

If any step fails, stop and report. Do not commit-and-pretend.

## Risks and open questions

- **Gallery discoverability** — the `pi-package` keyword puts this in the gallery, but with no npm publish or git remote, it's only installable via local path. That's the desired scope.
- **Future skill additions** — when a second skill lands, root `package.json` does not need to change (convention + explicit `pi.skills: ["./skills"]` cover it). Per-skill `package.json` is only needed if that skill also needs to be installable standalone — not required by this design.
- **Old install entry** — anyone who previously ran `pi install .../auto-research` will have a stale `settings.json` entry pointing at a path that no longer exists. This is out of scope for this change but worth flagging.
- **Existing `docs/superpowers/specs/2026-07-05-auto-research-design.md`** — references paths under `auto-research/`. The spec is historical and is not edited; new readers should be aware the path layout it describes is the previous arrangement.

## Out of scope

- Renaming the `auto-research` skill itself.
- Changing the auto-research iteration protocol.
- Adding a second skill.
- CI / publishing / npm auth.