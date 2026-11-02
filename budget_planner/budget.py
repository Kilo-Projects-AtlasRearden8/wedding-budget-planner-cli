"""Budget engine: totals, limits, overspending alerts, and mutations."""

from __future__ import annotations

import csv
import io

from .models import BudgetPlan, DEFAULT_CATEGORIES, LineItem
from .storage import BudgetStorage


class BudgetPlanner:
    """High-level operations on a wedding budget persisted to JSON."""

    def __init__(self, storage_path: str) -> None:
        self.storage = BudgetStorage(storage_path)
        self.plan = self.storage.load()

    def reload(self) -> None:
        self.plan = self.storage.load()

    def persist(self) -> None:
        self.storage.save(self.plan)

    def set_category_budget(self, category: str, amount: float) -> None:
        category = category.lower()
        if category not in DEFAULT_CATEGORIES:
            raise ValueError(
                f"Unknown category '{category}'. Use: {', '.join(DEFAULT_CATEGORIES)}"
            )
        if amount < 0:
            raise ValueError("Budget amount cannot be negative.")
        self.plan.category_limits[category] = float(amount)
        self.persist()

    def add_item(
        self,
        name: str,
        category: str,
        estimated: float = 0.0,
        actual: float = 0.0,
        notes: str = "",
        item_id: str | None = None,
    ) -> LineItem:
        category = category.lower()
        if category not in DEFAULT_CATEGORIES:
            raise ValueError(
                f"Unknown category '{category}'. Use: {', '.join(DEFAULT_CATEGORIES)}"
            )
        if estimated < 0 or actual < 0:
            raise ValueError("Amounts cannot be negative.")
        item = LineItem(
            id=item_id or self.storage.new_item_id(),
            name=name,
            category=category,
            estimated=float(estimated),
            actual=float(actual),
            notes=notes,
        )
        self.plan.add_item(item)
        self.persist()
        return item

    def update_item(
        self,
        item_id: str,
        name: str | None = None,
        category: str | None = None,
        estimated: float | None = None,
        actual: float | None = None,
        notes: str | None = None,
    ) -> LineItem:
        item = self.plan.find_item(item_id)
        if item is None:
            raise KeyError(f"No item with id '{item_id}'.")
        if name is not None:
            item.name = name
        if category is not None:
            category = category.lower()
            if category not in DEFAULT_CATEGORIES:
                raise ValueError(
                    f"Unknown category '{category}'. Use: {', '.join(DEFAULT_CATEGORIES)}"
                )
            item.category = category
        if estimated is not None:
            if estimated < 0:
                raise ValueError("Estimated amount cannot be negative.")
            item.estimated = float(estimated)
        if actual is not None:
            if actual < 0:
                raise ValueError("Actual amount cannot be negative.")
            item.actual = float(actual)
        if notes is not None:
            item.notes = notes
        self.persist()
        return item

    def remove_item(self, item_id: str) -> LineItem:
        item = self.plan.find_item(item_id)
        if item is None:
            raise KeyError(f"No item with id '{item_id}'.")
        if not self.plan.remove_item(item_id):
            raise KeyError(f"No item with id '{item_id}'.")
        self.persist()
        return item

    def category_summary(self, category: str) -> dict:
        category = category.lower()
        limit = self.plan.category_limits.get(category, 0.0)
        estimated = self.plan.category_total(category, "estimated")
        actual = self.plan.category_total(category, "actual")
        remaining = limit - actual
        return {
            "category": category,
            "limit": limit,
            "estimated": estimated,
            "actual": actual,
            "remaining": remaining,
            "over_budget": actual > limit if limit else False,
        }

    def grand_summary(self) -> dict:
        categories = list(DEFAULT_CATEGORIES)
        limit = sum(self.plan.category_limits.get(c, 0.0) for c in categories)
        estimated = self.plan.grand_total("estimated")
        actual = self.plan.grand_total("actual")
        return {
            "categories": categories,
            "limit": limit,
            "estimated": estimated,
            "actual": actual,
            "remaining": limit - actual,
            "over_budget": actual > limit if limit else False,
            "over_budget_categories": self.plan.over_budget_categories(),
        }

    def list_items(self, category: str | None = None) -> list[LineItem]:
        if category is None:
            return list(self.plan.items)
        category = category.lower()
        return [item for item in self.plan.items if item.category == category]

    def export_csv(self) -> str:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            ["id", "name", "category", "estimated", "actual", "notes"]
        )
        for item in self.plan.items:
            writer.writerow(
                [item.id, item.name, item.category, item.estimated, item.actual, item.notes]
            )
        return buffer.getvalue()

    def export_csv_to_file(self, path: str) -> None:
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(self.export_csv())
