"""Command-line interface for the wedding budget planner."""

from __future__ import annotations

import argparse
import sys

from .budget import BudgetPlanner


def _money(value: float) -> str:
    return f"${value:,.2f}"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wedding-budget",
        description="Build a wedding budget with local JSON storage.",
    )
    parser.add_argument(
        "--file",
        default="budget.json",
        help="Path to the local JSON budget file (default: budget.json).",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add-item", help="Add a budget line item.")
    p_add.add_argument("name", help="Item name.")
    p_add.add_argument("category", help="Category: venue, catering, attire, vendors.")
    p_add.add_argument("--estimated", type=float, default=0.0, help="Estimated cost.")
    p_add.add_argument("--actual", type=float, default=0.0, help="Actual cost.")
    p_add.add_argument("--notes", default="", help="Notes.")
    p_add.add_argument("--id", default=None, help="Optional item id.")

    p_set = sub.add_parser("set-budget", help="Set a category spending limit.")
    p_set.add_argument("category", help="Category: venue, catering, attire, vendors.")
    p_set.add_argument("amount", type=float, help="Budget limit.")

    p_list = sub.add_parser("list-items", help="List line items.")
    p_list.add_argument("category", nargs="?", default=None, help="Filter by category.")

    p_sum = sub.add_parser("summary", help="Show totals and overspending alerts.")

    p_rm = sub.add_parser("remove-item", help="Remove a line item by id.")
    p_rm.add_argument("id", help="Item id.")

    p_upd = sub.add_parser("update-item", help="Update a line item by id.")
    p_upd.add_argument("id", help="Item id.")
    p_upd.add_argument("--name", default=None)
    p_upd.add_argument("--category", default=None)
    p_upd.add_argument("--estimated", type=float, default=None)
    p_upd.add_argument("--actual", type=float, default=None)
    p_upd.add_argument("--notes", default=None)

    p_exp = sub.add_parser("export-csv", help="Export all items to CSV.")
    p_exp.add_argument("path", help="Output CSV file path.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    planner = BudgetPlanner(args.file)

    try:
        if args.command == "add-item":
            item = planner.add_item(
                name=args.name,
                category=args.category,
                estimated=args.estimated,
                actual=args.actual,
                notes=args.notes,
                item_id=args.id,
            )
            print(f"Added {item.id}: {item.name} ({item.category})")
        elif args.command == "set-budget":
            planner.set_category_budget(args.category, args.amount)
            print(f"Set {args.category} budget to {_money(args.amount)}")
        elif args.command == "list-items":
            items = planner.list_items(args.category)
            if not items:
                print("No items.")
                return 0
            for item in items:
                print(
                    f"{item.id}  {item.name:.<40} {item.category:.<12} "
                    f"est={_money(item.estimated)} act={_money(item.actual)}"
                )
        elif args.command == "summary":
            summary = planner.grand_summary()
            print("Wedding Budget Summary")
            print("=" * 30)
            print(f"Total limit:   {_money(summary['limit'])}")
            print(f"Total est.:    {_money(summary['estimated'])}")
            print(f"Total actual:  {_money(summary['actual'])}")
            print(f"Remaining:     {_money(summary['remaining'])}")
            if summary["over_budget"]:
                print("ALERT: Over budget overall.")
            for cat in summary["categories"]:
                info = planner.category_summary(cat)
                flag = "  <-- OVER BUDGET" if info["over_budget"] else ""
                print(
                    f"  {cat:.<12} limit={_money(info['limit']):>10} "
                    f"actual={_money(info['actual']):>10} remaining={_money(info['remaining']):>10}{flag}"
                )
            if summary["over_budget_categories"]:
                print(
                    "Overspending categories: "
                    + ", ".join(summary["over_budget_categories"])
                )
        elif args.command == "remove-item":
            item = planner.remove_item(args.id)
            print(f"Removed {item.id}: {item.name}")
        elif args.command == "update-item":
            item = planner.update_item(
                args.id,
                name=args.name,
                category=args.category,
                estimated=args.estimated,
                actual=args.actual,
                notes=args.notes,
            )
            print(f"Updated {item.id}: {item.name}")
        elif args.command == "export-csv":
            planner.export_csv_to_file(args.path)
            print(f"Exported to {args.path}")
        else:  # pragma: no cover - argparse guards this
            parser.print_help()
            return 2
    except (ValueError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
