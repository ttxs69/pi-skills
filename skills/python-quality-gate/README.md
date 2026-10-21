# python-quality-gate

One quality gate for a Python repository: `scripts/quality.sh` fails on unformatted code, lint findings, type errors, branch coverage below 90%, or any function whose cyclomatic complexity exceeds 10.

The skill configures ruff (format + lint, mccabe `C90` `max-complexity = 10`), mypy in `strict` mode, pytest with branch coverage and `fail_under = 90`, and wires all of it into a single `scripts/quality.sh` that CI reuses. It adapts to `src/` and flat layouts, uv/poetry/pip, and includes a ratchet path for legacy repositories that cannot reach 90% in one change.

## When to use it

Ask the agent to "configure python quality standards", "add ruff/mypy/pytest coverage", or "统一 python 代码规范 / 覆盖率 90% / 圈复杂度". The skill triggers on those requests and on repositories whose Python checks are scattered, missing, or non-blocking.

## Requirements

- Python 3.10 or newer
- One dependency manager: uv, poetry, or pip
- A `tests/` directory (created by the skill when absent)

## Install

```bash
# any Agent Skills-compatible harness (DSH, Claude Code, Codex, Cursor, Gemini CLI, pi, ...)
npx skills add ttxs69/pi-skills --skill python-quality-gate -g -y

# or install this repository as a pi package
pi install git:github.com/ttxs69/pi-skills
```

See [SKILL.md](SKILL.md) for the full procedure and the configuration block.
