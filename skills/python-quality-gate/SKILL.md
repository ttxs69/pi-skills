---
name: python-quality-gate
description: Set up or repair a Python repository's single quality gate — ruff format and lint, mypy strict typing, pytest branch coverage at or above 90%, and cyclomatic complexity at most 10 — all run by one scripts/quality.sh that CI reuses. Use when the user wants unified Python code standards, asks to configure ruff/mypy/pytest/coverage, mentions 90% 覆盖率, 圈复杂度, 统一配置, or 代码规范, or when a repo's Python checks are scattered, missing, or non-blocking.
---

# Python Quality Gate

One command, five failures: `./scripts/quality.sh` stops on unformatted code, lint findings, type errors, branch coverage under 90%, or any function whose cyclomatic complexity exceeds 10. The script is the single entry point — developers and CI run the same file, and the 90% threshold is written once. The same block goes into every Python repo; only the adapters marked `<...>` change.

## Steps

### 1. Survey the repo

```sh
sed -n '1,40p' pyproject.toml      # name, requires-python, build backend
ls pyproject.toml poetry.lock uv.lock setup.cfg .flake8 mypy.ini pytest.ini tox.ini 2>/dev/null
ls src 2>/dev/null || ls -d */ | grep -v -E 'tests|node_modules'
```

Completion criterion: you can name the Python lower bound, the package name, every import root (`src/` layout or flat `<pkg>/`), the dependency manager (uv / poetry / pip), and every existing config file that the block will absorb.

### 2. Put the whole gate in `pyproject.toml`

Paste this block, replace every `<...>` adapter, and keep the existing `[project]` fields. Where the file already has `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]`, or `[tool.coverage.*]`, merge these keys into those tables — a repeated table header is a TOML parse error that kills every command.

The five import-root adapters must agree:

| adapter | `src/` layout | flat layout |
| --- | --- | --- |
| `ruff` `src` | `["src", "tests"]` | `["."]` |
| `mypy` `files` | `["src", "tests"]` | `["<pkg>", "tests"]` |
| `pytest` `pythonpath` | `["src"]` | `["."]` |
| `coverage` `source` | `["src"]` | `["<pkg>"]` |
| `ruff` `isort` `known-first-party` | `["<pkg>"]` | `["<pkg>"]` |

Then, before running anything:

- `mkdir -p tests` when the repo has none — `mypy files`, `pytest testpaths`, and the coverage report all name `tests/`, and mypy aborts the whole run when a named path is missing.
- Add every other first-party Python root (`scripts/`, `examples/`, `tools/`) to `mypy files`: `ruff check .` already covers them, but mypy would otherwise skip them silently. Keep `coverage source` on the package, so scripts and examples do not dilute the 90%.
- Move each tool's settings out of `setup.cfg`, `tox.ini`, `mypy.ini`, `pytest.ini`, and `.flake8`, then delete a file only when nothing else remains in it — `setup.cfg` often holds setuptools metadata and `tox.ini` the test environments.

```toml
[tool.ruff]
line-length = 100
target-version = "py310"            # <lower bound of requires-python>
src = ["src", "tests"]              # <adapter table>
extend-exclude = ["build", "dist"]

[tool.ruff.format]
docstring-code-format = true

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "SIM", "C90", "RUF"]
ignore = ["E501"]                   # the formatter owns line width

[tool.ruff.lint.mccabe]
max-complexity = 10                 # cyclomatic complexity, per function

[tool.ruff.lint.isort]
known-first-party = ["<package>"]

[tool.mypy]
python_version = "3.10"             # <same lower bound as target-version>
strict = true
warn_unreachable = true
enable_error_code = ["ignore-without-code", "redundant-expr", "truthy-bool"]
files = ["src", "tests"]            # <adapter table>

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]                # <adapter table>
addopts = "-ra --strict-config --strict-markers"

[tool.coverage.run]
branch = true
source = ["src"]                    # <production package only; tests and scripts stay out>
relative_files = true

[tool.coverage.report]
fail_under = 90
precision = 2
show_missing = true
skip_covered = true
exclude_also = [
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
    "raise NotImplementedError",
    "@(abc\\.)?abstractmethod",
    "@(typing\\.)?overload",
]
```

`fail_under = 90` is the only place 90 appears. `precision = 2` compares `round(total, 2)` with 90, so 89.99 fails and 89.996 rounds up and passes — the gate is exact to two decimals, never rounded up from 89.5. `--cov` reads `source` and `fail_under` from here, so neither value is repeated on a command line.

Completion criterion: the block is in the file with all five adapters pointing at directories that exist (`ls src tests`, or `ls <pkg> tests`). The gate fails loudly on a duplicated table header, so a broken merge surfaces in step 4.

### 3. Install the four dev tools

Pick the manager already present in the repo:

```sh
uv add --dev ruff mypy pytest pytest-cov            # uv
poetry add --group dev ruff mypy pytest pytest-cov  # poetry
```

For pip projects, write these floors into `requirements-dev.txt` and pin the resolved set with `pip-compile` or `uv export`: `ruff>=0.11`, `mypy>=1.15`, `pytest>=8.3`, `pytest-cov>=6.2` (it brings `coverage>=7.5`, whose `exclude_also` the block uses). Install the `types-*` stub package for each untyped third-party import mypy reports; a global `ignore_missing_imports` would type-check that library as `Any` everywhere.

Completion criterion: the lockfile or a fully pinned requirements file records exact versions for all four tools, so local and CI resolve the same ones, and `uv run pytest --collect-only -q` reports `no tests collected` with exit 5 (a duplicated table never reaches pytest: uv rejects the file and exits 2).

### 4. Create the one entry point

`scripts/quality.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest --cov --cov-report=term-missing
```

Then:

- `chmod +x scripts/quality.sh`.
- Swap `uv run` for `poetry run` or `python -m` to match the manager, in all four lines.
- Keep the order: fast checks first, tests last, so a coverage or test failure never hides a type error.
- Append `.coverage`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, and `htmlcov/` to `.gitignore`.

Completion criterion: `./scripts/quality.sh` invokes all four tools from any directory in the repo and from a clean checkout after the dependency sync. Until step 6 adds real tests, `pytest` exits 5 (`no tests collected`) — that is the only expected non-zero at this point.

### 5. Make lint and types pass

```sh
uv run ruff format .          # apply formatting
uv run ruff check --fix .     # apply safe autofixes
uv run ruff check .           # the rest needs a human edit
uv run mypy
```

- **C90 findings** (`is too complex (N > 10)`): extract branches into named helpers, replace `if/elif` ladders with a lookup table, return early. A `# noqa: C901` is allowed only when the function is a flat table that reads worse split, with the reason on the same line.
- **Type errors**: annotate the definition, not the call site; install the stub package; validate the boundary value into a typed one instead of letting `Any` flow inward. A `# type: ignore[<code>]` carries its specific code and a one-line reason.
- **Tests are checked too**: every test function is annotated under `strict`, `def test_x() -> None`.

Completion criterion: `uv run ruff check . && uv run mypy` exits 0, `uv run ruff check --select C901 .` is clean, and no new suppression lacks its reason.

### 6. Reach 90% branch coverage

```sh
uv run pytest --cov --cov-report=term-missing
```

`Missing` lists uncovered lines and partially taken branches. Add behavior tests under `tests/` mirroring the source module: both outcomes of every condition, every operand combination of a short-circuit `and`/`or` (TT/TF/FT), and the error path that each `try`/`except` and early `raise` protects. Coverage measures the package only, so tests never inflate their own number.

While the gate is red, add tests — do not lower `fail_under`, add `--cov-omit`, or scatter `# pragma: no cover` beyond the five patterns already in the block. Those three moves are how a coverage gate stops meaning anything. A legacy repo that cannot reach 90 in one change ratchets: set `fail_under` to today's floor and raise it in the same commit that adds the tests, with 90 as the destination for every repo and the starting point for a new one.

Completion criterion: `./scripts/quality.sh` exits 0 from a clean checkout, `uv run pytest --cov --cov-report=term-missing` reports `>= 90.00%`, and `uv run ruff check --select C901 .` is clean.

### 7. Hand CI the same script

Replace every ad-hoc Python step in the CI job with:

```yaml
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v10
        with:
          python-version: "<lower bound>"
      - run: uv sync --locked
      - run: ./scripts/quality.sh
```

On GitLab or another runner, the job is the same two commands. Mark the job required: CI runs the identical file developers run, so the two cannot drift.

## Legacy repos: ratchet, don't ignore

A 4000-line repo will not reach zero on day one — mpdt's first run reported 2423 ruff
findings and 836 mypy-strict errors. Two wrong exits and one right one:

- **Ignore the rules.** The gate stops seeing new violations too; the debt becomes invisible
  and nothing ever converges.
- **Fix everything in one commit.** On a repo with thin tests this is where regressions land,
  and the highest-risk code (the report generator, the send path) is exactly what you'd touch.
- **Ratchet.** Commit the number, fail on any increase, update the baseline only downward.

```python
# tools/quality_budget.py — counts ruff + mypy findings, compares to a committed baseline
cur = {"ruff": count_ruff(), "mypy": count_mypy()}
regressed = {k: v for k, v in cur.items() if v > base.get(k, 0)}
if regressed:
    sys.exit(1)          # prints the new findings
# --update refuses to raise a baseline
```

Commit the baseline JSON, list the categories and their counts in a `QUALITY.md`
(biggest first, with the reason each one is deferred), and keep the rules **enabled**.
Coverage is the exception: `fail_under` starts at today's floor and rises in the same
commit that adds the tests.

Two exemptions are legitimate and worth writing down explicitly:

- **Non-ASCII text.** `RUF001/002/003` (`ambiguous-unicode-character-*`) fire on every
  full-width comma and colon in a Chinese codebase — 2077 of mpdt's 2423 findings, none of
  them a real confusable-character bug. Ignore those three, keep the rest of `RUF`.
- **`E501`** when the formatter owns line width.

## CI parity: coverage must not depend on the developer's machine

The gate went green locally at 90.01% and red in CI at 88.87% — same code, same tool versions.
The cause: two functions read `~/.hermes/.env`, which exists on the dev box and not on the
runner, so the parsing branch was covered by accident locally and never in CI.

Rules:

- **Any branch guarded by `Path.exists()` on a home-directory file needs a fixture that
  creates the file.** Point the env var (`MP_DOTENV`) at a temp file inside the test.
- **Verify parity, don't assume it:** rerun the suite with `HOME` pointed at an empty temp
  directory. Local and CI must report the same `Missing` count. If they differ, that diff
  *is* the environment dependence.
- Tests that `skipTest` on a shallow checkout are fine; tests whose coverage changes with
  the environment are not.

## Resolve the interpreter inside `quality.sh`

`python -m ruff` fails on machines where `python` is not the project interpreter, and the
error reads like the gate is broken rather than the environment. Resolve it once:

```bash
if [ -n "${PYTHON:-}" ]; then PY="$PYTHON"
elif [ -x .venv/bin/python ]; then PY=".venv/bin/python"
else PY="python3"; fi
"$PY" -m ruff format --check .
```

## Expect the first run to find real bugs

The gate pays for itself immediately on legacy code. mpdt's first run surfaced two:

- a format string with 7 arguments for 6 placeholders — a guaranteed `TypeError` on a branch
  the existing tests deliberately avoided (`verdict != "FAMILY_SPLIT"`);
- `result()` returning `0` unconditionally while `payload()` hardcoded `"ok": True`, so a
  failed send exited 0 and cron recorded success.

Budget time for fixing what it finds, and add a **negative control** for each fix: put the bug
back, confirm the test goes red, then remove it. A regression test you never saw fail is a
test you don't know works.

