# STATUS — Wedding Budget Planner CLI

## What was built

A local-first Python CLI for couples to build a wedding budget. Core pieces:

- `budget_planner/models.py` — `LineItem` and `BudgetPlan` data models with category
  totals, grand totals, overspending detection, and item CRUD.
- `budget_planner/storage.py` — `BudgetStorage` persisting a plan to a single local
  JSON file atomically (temp file + `os.replace`), with a blank plan created when the
  file is missing or empty.
- `budget_planner/budget.py` — `BudgetPlanner` engine: add/update/remove items,
  per-category budget limits, category and grand summaries, overspending alerts, and
  CSV export (to string or file).
- `budget_planner/cli.py` — argparse CLI with `add-item`, `set-budget`, `list-items`,
  `summary`, `remove-item`, `update-item`, and `export-csv` commands plus `--file`.
- `tests/test_budget.py` — 13 unittest tests covering totals, category totals,
  overspending alerts, persistence round-trips, CSV export, and input validation.
- `LICENSE` — MIT, copyright line exactly `Copyright (c) 2026 Asdale Dynamics, LLC`.
- `README.md` — usage, commands, example output, philosophy, credits Asdale Dynamics, LLC.
- `.gitignore`, git repo initialized with one commit.

Built for Asdale Dynamics, LLC (Indiana), credited in LICENSE and README. Local-first,
no accounts, no API keys, no network, no secrets or personal data.

## How to run it

Requires Python 3.8+ (tested on Python 3.13.5). No dependencies to install.

```bash
cd wedding-budget-planner-cli

# Add items and set limits
python3 -m budget_planner.cli --file my_wedding.json add-item "Main Hall" venue --estimated 3000 --actual 3200 --notes "reception hall"
python3 -m budget_planner.cli --file my_wedding.json add-item "Wedding Cake" catering --estimated 400 --actual 450
python3 -m budget_planner.cli --file my_wedding.json set-budget venue 3000

# View totals and overspending alerts
python3 -m budget_planner.cli --file my_wedding.json summary

# List items and export to CSV
python3 -m budget_planner.cli --file my_wedding.json list-items
python3 -m budget_planner.cli --file my_wedding.json export-csv my_wedding.csv
```

Categories: `venue`, `catering`, `attire`, `vendors`.

## Verification results

- `python3 -m unittest discover -s tests` → 13 tests, 0 failures, 0 errors. OK.
- Manual CLI exercise (add items, set budget, summary, list, export CSV) → works;
  overspending alert displays correctly when actual exceeds a category limit.
- Import `budget_planner` package → OK.

## Known gaps

- No packaging (`pyproject.toml`/`setup.py`) or console-script entry point; run via
  `python3 -m budget_planner.cli`.
- No code formatter/linter configured (ruff/black/etc.). Add one if the project is
  published.
- CLI runs one command per invocation; no interactive/TUI mode.
- Storage file path defaults to `budget.json` in the current directory; no platform
  config dir (e.g. XDG) resolution.
- Tests live in `tests/` but there is no CI config (`.github/workflows` deliberately
  omitted per project constraints).

## Commit

Single commit on `master`: "Add wedding budget planner CLI with JSON storage, CSV export, and overspending alerts". Committed as existing git identity; not pushed; no remote created.
