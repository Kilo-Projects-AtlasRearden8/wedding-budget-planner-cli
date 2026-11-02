"""Data models for the wedding budget planner."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

DEFAULT_CATEGORIES = ("venue", "catering", "attire", "vendors")


@dataclass
class LineItem:
    """A single budget line item."""

    id: str
    name: str
    category: str
    estimated: float = 0.0
    actual: float = 0.0
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "estimated": self.estimated,
            "actual": self.actual,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LineItem":
        return cls(
            id=str(data["id"]),
            name=str(data.get("name", "")),
            category=str(data.get("category", "")),
            estimated=float(data.get("estimated", 0.0) or 0.0),
            actual=float(data.get("actual", 0.0) or 0.0),
            notes=str(data.get("notes", "")),
        )


@dataclass
class BudgetPlan:
    """A collection of line items with per-category budget limits."""

    items: list[LineItem] = field(default_factory=list)
    category_limits: dict[str, float] = field(default_factory=dict)

    def category_total(self, category: str, field_name: str = "actual") -> float:
        total = 0.0
        for item in self.items:
            if item.category == category:
                total += getattr(item, field_name)
        return total

    def grand_total(self, field_name: str = "actual") -> float:
        return sum(getattr(item, field_name) for item in self.items)

    def category_over_budget(self, category: str) -> bool:
        limit = self.category_limits.get(category)
        if limit is None:
            return False
        return self.category_total(category) > limit

    def over_budget_categories(self) -> list[str]:
        return [
            category
            for category in self.category_limits
            if self.category_over_budget(category)
        ]

    def find_item(self, item_id: str) -> LineItem | None:
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def add_item(self, item: LineItem) -> None:
        self.items.append(item)

    def remove_item(self, item_id: str) -> bool:
        for index, item in enumerate(self.items):
            if item.id == item_id:
                del self.items[index]
                return True
        return False

    def categories_used(self) -> Iterable[str]:
        seen: set[str] = set()
        for item in self.items:
            seen.add(item.category)
        return seen
