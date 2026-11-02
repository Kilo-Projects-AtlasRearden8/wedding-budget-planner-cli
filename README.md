# Wedding Budget Planner CLI

A small, local-first Python command-line tool that helps couples build a wedding
budget together. Track venue, catering, attire, and vendor costs, set spending
limits per category, get overspending alerts, and export your budget to CSV.
Everything is stored in a single local JSON file — no accounts, no API keys, no
network calls.

Built and maintained by **Asdale Dynamics, LLC** (Indiana). Part of our
beginner-friendly, practical open-source tools for small business and life
admin.

## Who this is for

Couples planning a wedding who want a simple, transparent way to track spending
without signing up for another app. Also a handy template if you're learning to
build small local-first CLI tools in Python.

## Features

- **Four built-in categories:** venue, catering, attire, vendors
- **Line items** with name, estimated cost, actual cost, and notes
- **Per-category spending limits** with overspending alerts
- **Grand-total summary** showing estimated vs. actual vs. remaining
- **Local JSON storage** — one file, lives on your machine
- **CSV export** — open your budget in any spreadsheet
- **No accounts, no keys, no network** — local-first by design

## Install

No installation required. You need Python 3.8 or later.

```bash
git clone <this-repo>
cd wedding-budget-planner-cli
```

Or just copy the `budget_planner/` folder into your own project.

## Run it

The CLI is a module you run directly with Python:

```bash
python3 -m budget_planner.cli --file my_wedding.json add-item "Main Hall" venue --estimated 3000 --actual 3200 --notes "reception hall"
python3 -m budget_planner.cli --file my_wedding.json add-item "Wedding Cake" catering --estimated 400 --actual 450
python3 -m budget_planner.cli --file my_wedding.json set-budget venue 3000
python3 -m budget_planner.cli --file my_wedding.json summary
python3 -m budget_planner.cli --file my_wedding.json list-items
python3 -m budget_planner.cli --file my_wedding.json export-csv my_wedding.csv
```

### Commands

| Command | What it does |
|---------|--------------|
| `add-item NAME CATEGORY` | Add a line item (`--estimated`, `--actual`, `--notes`, `--id`) |
| `set-budget CATEGORY AMOUNT` | Set a spending limit for a category |
| `list-items [CATEGORY]` | List line items, optionally filtered by category |
| `summary` | Show totals, remaining, and overspending alerts |
| `remove-item ID` | Remove a line item |
| `update-item ID` | Update a line item (`--name`, `--category`, `--estimated`, `--actual`, `--notes`) |
| `export-csv PATH` | Export all items to a CSV file |

`--file` sets the JSON storage file (default: `budget.json`).

Categories are: `venue`, `catering`, `attire`, `vendors`.

## Example output

```
Wedding Budget Summary
==============================
Total limit:   $3,000.00
Total est.:    $3,400.00
Total actual:  $3,650.00
Remaining:     $-650.00
ALERT: Over budget overall.
  venue....... limit= $3,000.00 actual= $3,200.00 remaining=  $-200.00  <-- OVER BUDGET
  catering.... limit=     $0.00 actual=   $450.00 remaining=  $-450.00
  attire...... limit=     $0.00 actual=     $0.00 remaining=     $0.00
  vendors..... limit=     $0.00 actual=     $0.00 remaining=     $0.00
Overspending categories: venue, catering
```

## Tests

Run the test suite with Python's standard library (no dependencies needed):

```bash
python3 -m unittest discover -s tests
```

Tests cover totals, category totals, overspending alerts, persistence round-trips,
CSV export, and input validation.

## Project structure

```
wedding-budget-planner-cli/
├── LICENSE
├── README.md
├── STATUS.md
├── budget_planner/
│   ├── __init__.py
│   ├── budget.py     # engine: totals, limits, alerts, CSV export
│   ├── cli.py        # argparse command-line interface
│   ├── models.py     # LineItem and BudgetPlan data models
│   └── storage.py    # local JSON persistence
└── tests/
    └── test_budget.py
```

## Philosophy

This tool follows the Asdale Dynamics, LLC style: plain English, step by step,
never condescending, local-first, tested, and free of secrets or personal data.
It's designed to be approachable for beginners and useful enough to publish or
sell as a template for small-business and life-admin tools.

Learn more about Asdale Dynamics, LLC and our beginner-friendly AI education,
books, and practical tools at dylanasdale.github.io.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE` for details.
