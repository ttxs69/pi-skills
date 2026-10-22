# pi-skills

A collection of [Agent Skills](https://agentskills.io/specification) packaged as one installable pi package. Every skill under `skills/<name>/` works in pi, and the same directory installs into any Agent Skills-compatible harness (Claude Code, Codex, Cursor, Gemini CLI, DeepSeek Harness, ...) through the [skills CLI](https://github.com/vercel-labs/skills).

## Install

Install into any supported agent (the skills CLI writes to `~/.agents/skills` and links each agent's own skills directory):

```bash
npx skills add ttxs69/pi-skills --list
npx skills add ttxs69/pi-skills --skill python-quality-gate -g -y
npx skills add ttxs69/pi-skills --skill agent-ecosystem-intel -g -y
```

Or install this repository as a pi package, which adds every skill under `skills/` at once:

```bash
pi install git:github.com/ttxs69/pi-skills
pi list
```

Uninstall with `npx skills remove <skill> -g` or `pi remove git:github.com/ttxs69/pi-skills`.

## Layout

```
.
├── package.json          # pi-package manifest (pi-package keyword, pi.skills: ["./skills"])
├── README.md             # this file
├── LICENSE
├── docs/                 # design specs, plans
└── skills/
    └── <skill-name>/     # one directory per skill
        ├── SKILL.md      # required — frontmatter + instructions
        ├── README.md     # per-skill docs
        ├── agents/       # optional per-harness metadata
        ├── assets/       # templates and resources (Agent Skills standard)
        └── tests/        # RED/GREEN artifacts
```

Pi auto-discovers skills from the `skills/` directory; the explicit `pi.skills` entry in `package.json` is belt-and-suspenders.

## Skills

| Skill | Description |
|---|---|
| [auto-research](skills/auto-research/) | Autonomous goal-directed research loop: reads `GOAL.md`, dispatches a fresh-context subagent per iteration, records structured findings in `FIND.md`, stops on saturation or iteration cap. |
| [python-quality-gate](skills/python-quality-gate/) | One Python quality gate — ruff format and lint (mccabe complexity ≤10), mypy strict, pytest branch coverage ≥90% — all run by one `scripts/quality.sh` that CI reuses. |
| [agent-ecosystem-intel](skills/agent-ecosystem-intel/) | Positions a project in the AI-agent ecosystem: which of 8 lanes it occupies, how crowded that lane is, and which projects it competes with — from 34 days of GitHub Trending records (402 records, nothing deleted) that ship with the skill. |

## agent-ecosystem-intel

Ask the agent where a project sits in the agent ecosystem and how crowded that lane is:

```bash
npx skills add ttxs69/pi-skills --skill agent-ecosystem-intel -g -y
```

```bash
cd ~/.agents/skills/agent-ecosystem-intel
python3 scripts/project_positioning.py --repo owner/repo   # locate one project
python3 scripts/agent_landscape.py --verify                # recompute the lane table
```

The 8 lanes are defined by *which step of an agent's workflow a project replaces*
(skills / memory / runtime / harness / orchestration / CLI-ification / vertical / vendor),
not by tech stack. 34 days of raw Trending records ship with the skill, so every
number can be recomputed by the reader.

**Scope limit:** the data source is the English GitHub Trending feed — Chinese and
niche projects are often absent (0 hits means "not in my sample", not "not worth doing").

## License

MIT — see [LICENSE](LICENSE).
