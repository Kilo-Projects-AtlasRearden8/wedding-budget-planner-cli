"""Local JSON storage for the wedding budget planner."""

from __future__ import annotations

import json
import os
import uuid
from typing import Any

from .models import BudgetPlan, DEFAULT_CATEGORIES, LineItem


class StorageError(Exception):
    """Raised when reading or writing the storage file fails."""


class BudgetStorage:
    """Persists a BudgetPlan to a single local JSON file."""

    def __init__(self, path: str) -> None:
        self.path = path

    def _empty_plan(self) -> BudgetPlan:
        return BudgetPlan(
            items=[],
            category_limits={category: 0.0 for category in DEFAULT_CATEGORIES},
        )

    def load(self) -> BudgetPlan:
        """Load the plan from disk, creating a blank one if missing."""
        if not os.path.exists(self.path):
            return self._empty_plan()
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                content = handle.read()
        except OSError as exc:
            raise StorageError(f"Unable to read budget file {self.path}: {exc}") from exc
        if not content.strip():
            return self._empty_plan()
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise StorageError(f"Unable to read budget file {self.path}: {exc}") from exc

        items = [LineItem.from_dict(item) for item in data.get("items", [])]
        limits = {
            str(category): float(value or 0.0)
            for category, value in data.get("category_limits", {}).items()
        }
        for category in DEFAULT_CATEGORIES:
            limits.setdefault(category, 0.0)
        return BudgetPlan(items=items, category_limits=limits)

    def save(self, plan: BudgetPlan) -> None:
        """Persist the plan to disk atomically."""
        data = {
            "items": [item.to_dict() for item in plan.items],
            "category_limits": plan.category_limits,
        }
        directory = os.path.dirname(os.path.abspath(self.path))
        try:
            tmp_path = f"{self.path}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2)
                handle.write("\n")
            os.replace(tmp_path, self.path)
        except OSError as exc:
            raise StorageError(f"Unable to write budget file {self.path}: {exc}") from exc

    @staticmethod
    def new_item_id() -> str:
        return uuid.uuid4().hex[:8]
