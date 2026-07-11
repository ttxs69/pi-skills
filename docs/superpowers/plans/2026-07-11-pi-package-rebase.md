# Pi-Package Rebase Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure this repository so `pi install /Users/sarace/dev/projects/skills` works as a single installable pi package, replacing the current `auto-research/` sub-package layout with a convention layout at the repo root.

**Architecture:** Move `auto-research/*` into `skills/auto-research/`, place the template under `assets/` per the Agent Skills standard, add a root `package.json` with the `pi-package` keyword and explicit `pi.skills: ["./skills"]`, and add a root `README.md`. The old `auto-research/package.json` is removed; the `auto-research/` directory is deleted. The 38 tracked files under `auto-research/` (1 README + 1 SKILL.md + 1 template + 1 root package.json + 34 files under `tests/`) all move together via `git mv`.

**Tech Stack:** Git, `pi` CLI (npm: `@earendil-works/pi-coding-agent`), Agent Skills standard (skills/<name>/SKILL.md + assets/ + references/).

## Global Constraints

- All file moves use `git mv` so git tracks renames and preserves file history. After `git mv`, the source path no longer exists on disk; the destination path is what gets committed as a rename.
- Historical test artifacts under `auto-research/tests/` (e.g. `BASELINE_FINDINGS.md`, `GREEN_FINDINGS.md`, `COMPLETION_OUTPUT.md`, the `.pi-subagents/artifacts/*.md` files) reference the old absolute path. They are historical records of past test runs and **must not be edited**. Move them verbatim.
- Test-local fixture copies of `template-FIND.md` exist at `auto-research/tests/completion-test/template-FIND.md` and `auto-research/tests/with-skill/template-FIND.md`. These are test-fixture-local copies, NOT the skill's canonical template. **Do not delete, move, or edit** them — they stay at their current paths under the new `skills/auto-research/tests/...` tree.
- Commit messages follow the existing repo convention: `feat:`, `fix:`, `chore:`, `docs:`, `spec:`, `refactor:` prefixes (see `git log`).
- All file moves preserve content byte-for-byte EXCEPT where path-or-name edits are explicitly listed in Tasks 4 and 5.
- `pi install /Users/sarace/dev/projects/skills` is the install command. The previously-documented `pi install .../auto-research` becomes invalid after Task 6.
- No `.gitignore` exists in the repo today. Do not add one as part of this change (out of scope).
- The plan runs against the repo at `/Users/sarace/dev/projects/skills`. All file paths in this plan are absolute.

---

### Task 1: Capture pre-flight baseline

**Files:** none modified

**Interfaces:**
- Produces: a captured baseline that Task 7 (verification) diffs against to prove the package wasn't already installed.

- [ ] **Step 1: Verify working tree is clean**

Run: `git -C /Users/sarace/dev/projects/skills status`
Expected: `nothing to commit, working tree clean`. If anything shows up, stop and report — leftover changes from prior work would conflict with this plan.

- [ ] **Step 2: Capture pre-install pi state**

Run: `pi list 2>&1 | grep -q pi-skills && echo "ALREADY INSTALLED" || echo "NOT INSTALLED (expected baseline)"`
Expected: outputs `NOT INSTALLED (expected baseline)`. If `ALREADY INSTALLED`, stop — Task 7's verification step 1 will be meaningless and the package was installed in a previous run that should be cleaned up first.

- [ ] **Step 3: No commit (no changes yet)**

This task is read-only. No commit.

---

### Task 2: Create root-level files (package.json + README.md)

**Files:**
- Create: `/Users/sarace/dev/projects/skills/package.json`
- Create: `/Users/sarace/dev/projects/skills/README.md`

**Interfaces:**
- Produces: `package.json` with `name: "pi-skills"` and `pi.skills: ["./skills"]`, used by Task 7 step 2's `pi install`.
- Produces: root `README.md` referencing the `skills/<name>/` layout (the directories don't need to exist yet — the README is just text).

- [ ] **Step 1: Write the root package.json**

Write `/Users/sarace/dev/projects/skills/package.json` with this exact content:

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

- [ ] **Step 2: Verify package.json is valid JSON**

Run: `python3 -c "import json; json.load(open('/Users/sarace/dev/projects/skills/package.json'))" && echo OK`
Expected: outputs `OK`. Any JSON parse error means the file is malformed — fix and re-run.

- [ ] **Step 3: Write the root README.md**

Write `/Users/sarace/dev/projects/skills/README.md` with this exact content:

```markdown
# pi-skills

A collection of pi skills bundled as a single installable package. Install the repo and each skill under `skills/<name>/` becomes available as `/skill <name>`.

## Install

```bash
pi install /Users/sarace/dev/projects/skills
```

The repo root is the package — installing it adds every skill under `skills/` to your pi agent's available skills. No symlinks, no hand-edited `settings.json`.

## Layout

```
.
├── package.json          # pi-package manifest (pi-package keyword, pi.skills: ["./skills"])
├── README.md             # this file
├── docs/                 # design specs, plans
└── skills/
    └── <skill-name>/     # one directory per skill
        ├── SKILL.md      # required — frontmatter + instructions
        ├── assets/       # templates and resources (Agent Skills standard)
        ├── README.md     # per-skill docs
        └── tests/        # RED/GREEN artifacts
```

Pi auto-discovers skills from the `skills/` directory; the explicit `pi.skills` entry in `package.json` is belt-and-suspenders.

## Skills

| Skill | Description |
|---|---|
| [auto-research](skills/auto-research/) | Autonomous goal-directed research loop: reads `GOAL.md`, dispatches a fresh-context subagent per iteration, records structured findings in `FIND.md`, stops on saturation or iteration cap. |
```

- [ ] **Step 4: Verify both files exist**

Run:
```bash
ls -la /Users/sarace/dev/projects/skills/package.json /Users/sarace/dev/projects/skills/README.md
```
Expected: both files listed with sensible sizes (`package.json` ~280 bytes, `README.md` ~1.5 KB).

- [ ] **Step 5: Commit**

Run:
```bash
cd /Users/sarace/dev/projects/skills
git add package.json README.md
git commit -m "feat: add root pi-package manifest and README"
```

Expected: one commit created. `git status` shows clean working tree.

---

### Task 3: Move skill files into skills/auto-research/ (verbatim content)

**Files:**
- Move (rename): `auto-research/SKILL.md` → `skills/auto-research/SKILL.md`
- Move (rename): `auto-research/template-FIND.md` → `skills/auto-research/assets/template-FIND.md`
- Move (rename): `auto-research/README.md` → `skills/auto-research/README.md`
- Move (rename, recursive): `auto-research/tests/` → `skills/auto-research/tests/` (34 files including `.pi-subagents/artifacts/`, test fixture template copies, and historical FINDINGS notes)

**Interfaces:**
- Consumes: Task 2's `package.json` (which references `./skills`).
- Produces: skill files at the new paths. Content is byte-for-byte identical to the originals — path edits come in Tasks 4 and 5.

- [ ] **Step 1: Create the target directory tree**

Run:
```bash
mkdir -p /Users/sarace/dev/projects/skills/skills/auto-research/assets
```
Expected: command exits 0.

- [ ] **Step 2: git mv the four top-level skill items**

Run:
```bash
cd /Users/sarace/dev/projects/skills
git mv auto-research/SKILL.md          skills/auto-research/SKILL.md
git mv auto-research/README.md         skills/auto-research/README.md
git mv auto-research/tests             skills/auto-research/tests
git mv auto-research/template-FIND.md  skills/auto-research/assets/template-FIND.md
```

Expected: each command exits 0. Note that `git mv` physically moves each file (the source path is gone after the move). The recursive `git mv auto-research/tests skills/auto-research/tests` moves all 34 files under `tests/` including `.pi-subagents/artifacts/`.

- [ ] **Step 3: Verify the move produced the expected layout**

Run:
```bash
cd /Users/sarace/dev/projects/skills
echo "--- auto-research/ (should contain only package.json) ---"
ls -la auto-research/
echo "--- skills/auto-research/ ---"
ls skills/auto-research/
echo "--- skills/auto-research/assets/ ---"
ls skills/auto-research/assets/
echo "--- skills/auto-research/tests/ ---"
ls skills/auto-research/tests/
```

Expected:
- `auto-research/` shows only `package.json` (and `.`, `..`)
- `skills/auto-research/` shows `SKILL.md`, `README.md`, `tests/`
- `skills/auto-research/assets/` shows `template-FIND.md`
- `skills/auto-research/tests/` shows `baseline/`, `compaction-test/`, `completion-test/`, `with-skill/`, `GREEN_FINDINGS.md`

- [ ] **Step 4: Verify file counts match pre-move state**

Run:
```bash
cd /Users/sarace/dev/projects/skills
echo "tracked files now under skills/:"
git ls-files skills/ | wc -l
echo "tracked files still under auto-research/ (should be 1 — package.json only):"
git ls-files auto-research/ | wc -l
```

Expected: 37 under `skills/` (38 minus the package.json that's still at the old path) and 1 under `auto-research/` (just `package.json`).

- [ ] **Step 5: Spot-check that one historical artifact moved verbatim**

Run:
```bash
cd /Users/sarace/dev/projects/skills
head -3 skills/auto-research/tests/GREEN_FINDINGS.md
```

Expected: file starts with a markdown heading (pre-move content). The contents of every file under `tests/` should be unchanged — git's rename detection at commit time is what preserves history.

- [ ] **Step 6: Commit the moves**

Run:
```bash
cd /Users/sarace/dev/projects/skills
git commit -m "refactor: move skill files into skills/auto-research/"
```

Expected: one commit with a substantial number of renames. `git status` shows only `auto-research/package.json` remaining as a modified-but-not-yet-deleted file (deleted in Task 6).

---

### Task 4: Update SKILL.md path references (template under assets/)

**Files:**
- Modify: `/Users/sarace/dev/projects/skills/skills/auto-research/SKILL.md` (lines 79 and 101)

**Interfaces:**
- Consumes: moved SKILL.md from Task 3
- Produces: SKILL.md with `assets/template-FIND.md` paths, required for the skill's bootstrap step to find the template at runtime

- [ ] **Step 1: Update line 79**

In `skills/auto-research/SKILL.md`, find the exact text:
```
A starter template is at `template-FIND.md` — copy it if `FIND.md` does not exist.
```

Replace with:
```
A starter template is at `assets/template-FIND.md` — copy it if `FIND.md` does not exist.
```

- [ ] **Step 2: Update line 101**

In `skills/auto-research/SKILL.md`, find the exact text:
```
   - If `template-FIND.md` exists at the skill's path → copy it to `FIND.md`.
```

Replace with:
```
   - If `assets/template-FIND.md` exists at the skill's path → copy it to `FIND.md`.
```

- [ ] **Step 3: Verify both updates landed and no bare references remain**

Run:
```bash
cd /Users/sarace/dev/projects/skills
grep -n 'template-FIND' skills/auto-research/SKILL.md
```

Expected: exactly TWO lines of output, and both must contain `assets/template-FIND.md`. Any line containing only `template-FIND.md` (without `assets/` prefix) means a step was missed.

- [ ] **Step 4: Commit**

Run:
```bash
cd /Users/sarace/dev/projects/skills
git add skills/auto-research/SKILL.md
git commit -m "fix: update template-FIND.md path in SKILL.md to assets/"
```

---

### Task 5: Update auto-research/README.md (6 path/name edits)

**Files:**
- Modify: `/Users/sarace/dev/projects/skills/skills/auto-research/README.md`

**Interfaces:**
- Consumes: moved README.md from Task 3
- Produces: README.md at the new path with all six edits applied

- [ ] **Step 1: Edit line 14 (layout tree)**

In `skills/auto-research/README.md`, find:
```
├── template-FIND.md      # Starter template for FIND.md
```

Replace with:
```
├── assets/
│   └── template-FIND.md  # Starter template for FIND.md
```

- [ ] **Step 2: Edit the manifest description (~line 50)**

In `skills/auto-research/README.md`, find:
```
(see `package.json` with `pi-package` keyword and `pi.skills: ["./SKILL.md"]`)
```

Replace with:
```
(see root `package.json` with `pi-package` keyword and `pi.skills: ["./skills"]`)
```

- [ ] **Step 3: Edit the install command (line 53)**

In `skills/auto-research/README.md`, find:
```
pi install /Users/sarace/dev/projects/skills/auto-research
```

Replace with:
```
pi install /Users/sarace/dev/projects/skills
```

- [ ] **Step 4: Edit the remove command (line 61)**

In `skills/auto-research/README.md`, find:
```
pi remove /Users/sarace/dev/projects/skills/auto-research
```

Replace with:
```
pi remove /Users/sarace/dev/projects/skills
```

- [ ] **Step 5: Edit the npm example (line 75)**

In `skills/auto-research/README.md`, find:
```
pi install npm:auto-research                 # if published to npm
```

Replace with:
```
pi install npm:pi-skills                 # if published to npm
```

- [ ] **Step 6: Edit the git example (line 76)**

In `skills/auto-research/README.md`, find:
```
pi install git:github.com/you/auto-research  # if published to a git repo
```

Replace with:
```
pi install git:github.com/you/pi-skills  # if published to a git repo
```

- [ ] **Step 7: Verify all six edits landed**

Run:
```bash
cd /Users/sarace/dev/projects/skills
grep -nE 'pi install|pi remove|pi.skills|template-FIND' skills/auto-research/README.md
```

Expected:
- All `pi install` / `pi remove` lines use `/Users/sarace/dev/projects/skills` (no `auto-research` suffix)
- The `pi.skills:` reference shows `["./skills"]` (not `["./SKILL.md"]`)
- Any `template-FIND` reference uses `assets/template-FIND.md` (not bare `template-FIND.md`)
- The npm example reads `npm:pi-skills`; the git example reads `github.com/you/pi-skills`

If any line still references the old path or old package name, stop and identify which edit was missed.

- [ ] **Step 8: Commit**

Run:
```bash
cd /Users/sarace/dev/projects/skills
git add skills/auto-research/README.md
git commit -m "fix: update install path and package name in skill README"
```

---

### Task 6: Remove the old auto-research/ subdirectory

**Files:**
- Delete: `/Users/sarace/dev/projects/skills/auto-research/package.json`
- Delete (empty dir): `/Users/sarace/dev/projects/skills/auto-research/`

**Interfaces:**
- Consumes: the leftover `auto-research/package.json` from the old layout (Tasks 1–5 left it untouched)
- Produces: a clean target layout matching the spec

- [ ] **Step 1: Confirm auto-research/ contains only package.json**

Run:
```bash
ls -la /Users/sarace/dev/projects/skills/auto-research/
```

Expected: output shows only `package.json` (and `.`, `..`). If other files appear, stop — Task 3 missed something.

- [ ] **Step 2: git rm the old package.json**

Run:
```bash
cd /Users/sarace/dev/projects/skills
git rm auto-research/package.json
```

Expected: command exits 0. The file is staged for deletion.

- [ ] **Step 3: Remove the now-empty auto-research/ directory**

Run:
```bash
cd /Users/sarace/dev/projects/skills
rmdir auto-research
```

Expected: command exits 0. `ls auto-research/` fails with "No such file or directory".

- [ ] **Step 4: Verify final target layout**

Run:
```bash
cd /Users/sarace/dev/projects/skills
ls -la
echo "---"
ls skills/auto-research/
```

Expected top level: `package.json`, `README.md`, `docs/`, `skills/`, `.git/` (and no `auto-research/`). Expected `skills/auto-research/`: `SKILL.md`, `assets/`, `README.md`, `tests/`.

- [ ] **Step 5: Commit cleanup**

Run:
```bash
cd /Users/sarace/dev/projects/skills
git commit -m "chore: remove superseded auto-research/ subdirectory"
```

Expected: clean working tree.

---

### Task 7: Verification (8 steps from the spec)

**Files:** none modified

**Interfaces:**
- Consumes: the complete restructured repo from Tasks 1–6
- Produces: evidence the package installs and the skill registers correctly

Run every step. **If any step fails, stop and report — do not claim done.** Do not commit anything in this task; verification is a check, not a code change.

- [ ] **Step 1: Pre-install state (re-confirm)**

Run: `pi list 2>&1 | grep -q pi-skills && echo "ALREADY INSTALLED" || echo "NOT INSTALLED (expected)"`
Expected: `NOT INSTALLED (expected)`. (Task 1 captured this baseline; this re-confirms nothing changed the install state during the moves.)

- [ ] **Step 2: Install**

Run: `pi install /Users/sarace/dev/projects/skills`
Expected: command exits 0. Output describes what was added to `~/.pi/agent/settings.json`.

- [ ] **Step 3: Post-install state**

Run: `pi list`
Expected: output includes an entry for `pi-skills` with source path `/Users/sarace/dev/projects/skills`.

- [ ] **Step 4: Skill registration**

Run: `pi -p "what skills are available?" 2>&1 | head -30` (or start pi interactively and check `<available_skills>`).
Expected: `auto-research` appears in the available skills list. `/skill auto-research` should be invocable in interactive mode.

- [ ] **Step 5: Old manifest gone**

Run: `test ! -f /Users/sarace/dev/projects/skills/auto-research/package.json && echo "OK: old manifest gone" || echo "FAIL: old manifest still present"`
Expected: `OK: old manifest gone`. If `FAIL`, Task 6 didn't run or didn't complete.

- [ ] **Step 6: Git diff sanity**

Run: `git -C /Users/sarace/dev/projects/skills status`
Expected: clean working tree (`nothing to commit, working tree clean`). All tasks should have ended with a commit.

- [ ] **Step 7: Frontmatter sanity**

Run: `head -10 /Users/sarace/dev/projects/skills/skills/auto-research/SKILL.md`
Expected: first 10 lines include `name: auto-research` and a non-empty `description:` (frontmatter intact from before the move).

- [ ] **Step 8: Path consistency**

Run:
```bash
cd /Users/sarace/dev/projects/skills
grep -rn 'template-FIND' skills/auto-research/SKILL.md skills/auto-research/README.md
```

Expected: every match contains `assets/template-FIND.md`. Any match showing bare `template-FIND.md` (without `assets/`) means a path update was missed.

- [ ] **Step 9: Report verification outcome**

If all 8 steps pass: write a brief summary message confirming the package installs and the skill registers. Implementation is complete.
If any step fails: write a summary listing exactly which steps failed and the actual output, then stop. Do not proceed.