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
