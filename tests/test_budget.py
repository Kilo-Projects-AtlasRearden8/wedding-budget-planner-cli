"""Tests for the wedding budget planner."""

from __future__ import annotations

import os
import tempfile
import unittest

from budget_planner.budget import BudgetPlanner
from budget_planner.models import DEFAULT_CATEGORIES, LineItem, BudgetPlan
from budget_planner.storage import BudgetStorage


class TestLineItem(unittest.TestCase):
    def test_to_and_from_dict(self):
        item = LineItem(id="a1", name="Venue", category="venue", estimated=1000.0, actual=1100.0, notes="hall")
        data = item.to_dict()
        restored = LineItem.from_dict(data)
        self.assertEqual(restored.id, "a1")
        self.assertEqual(restored.name, "Venue")
        self.assertEqual(restored.category, "venue")
        self.assertEqual(restored.estimated, 1000.0)
        self.assertEqual(restored.actual, 1100.0)
        self.assertEqual(restored.notes, "hall")


class TestBudgetPlanTotals(unittest.TestCase):
    def setUp(self):
        self.plan = BudgetPlan()
        self.plan.add_item(LineItem(id="i1", name="Hall", category="venue", estimated=2000.0, actual=2100.0))
        self.plan.add_item(LineItem(id="i2", name="Flowers", category="venue", estimated=500.0, actual=600.0))
        self.plan.add_item(LineItem(id="i3", name="Cake", category="catering", estimated=400.0, actual=450.0))
        self.plan.category_limits = {"venue": 3000.0, "catering": 500.0}

    def test_category_total_actual(self):
        self.assertEqual(self.plan.category_total("venue", "actual"), 2700.0)
        self.assertEqual(self.plan.category_total("catering", "actual"), 450.0)

    def test_category_total_estimated(self):
        self.assertEqual(self.plan.category_total("venue", "estimated"), 2500.0)

    def test_grand_total(self):
        self.assertEqual(self.plan.grand_total("actual"), 3150.0)
        self.assertEqual(self.plan.grand_total("estimated"), 2900.0)

    def test_over_budget_category(self):
        # venue actual 2700, limit 3000 -> not over
        self.assertFalse(self.plan.category_over_budget("venue"))
        # catering actual 450, limit 500 -> not over
        self.assertFalse(self.plan.category_over_budget("catering"))

    def test_over_budget_categories(self):
        # venue not over (2700 < 3000), catering not over (450 < 500)
        self.assertEqual(self.plan.over_budget_categories(), [])
        # push venue over
        self.plan.category_limits["venue"] = 1000.0
        self.assertIn("venue", self.plan.over_budget_categories())


class TestBudgetPlanner(unittest.TestCase):
    def _planner(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        return BudgetPlanner(path), path

    def test_add_and_totals(self):
        planner, path = self._planner()
        try:
            planner.add_item("Hall", "venue", estimated=2000, actual=2100)
            planner.add_item("Cake", "catering", estimated=400, actual=450)
            summary = planner.grand_summary()
            self.assertEqual(summary["actual"], 2550.0)
            self.assertEqual(summary["estimated"], 2400.0)
            self.assertFalse(summary["over_budget"])
        finally:
            os.unlink(path)

    def test_overspending_alert(self):
        planner, path = self._planner()
        try:
            planner.set_category_budget("venue", 1000.0)
            planner.add_item("Hall", "venue", actual=2100)
            summary = planner.grand_summary()
            self.assertTrue(summary["over_budget"])
            self.assertIn("venue", summary["over_budget_categories"])
        finally:
            os.unlink(path)

    def test_persistence_roundtrip(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            planner = BudgetPlanner(path)
            planner.add_item("Hall", "venue", actual=2100)
            planner.set_category_budget("venue", 3000.0)
            planner2 = BudgetPlanner(path)
            summary = planner2.grand_summary()
            self.assertEqual(summary["actual"], 2100.0)
            self.assertEqual(planner2.plan.category_limits["venue"], 3000.0)
        finally:
            os.unlink(path)

    def test_csv_export(self):
        planner, path = self._planner()
        try:
            planner.add_item("Hall", "venue", estimated=2000, actual=2100, notes="main hall")
            csv_path = path + ".csv"
            try:
                planner.export_csv_to_file(csv_path)
                with open(csv_path, encoding="utf-8") as handle:
                    lines = handle.read().strip().splitlines()
                self.assertEqual(lines[0], "id,name,category,estimated,actual,notes")
                self.assertEqual(len(lines), 2)
                self.assertIn("venue", lines[1])
                self.assertIn("2100", lines[1])
            finally:
                os.unlink(csv_path)
        finally:
            os.unlink(path)

    def test_unknown_category_rejected(self):
        planner, path = self._planner()
        try:
            with self.assertRaises(ValueError):
                planner.add_item("Thing", "photography")
            with self.assertRaises(ValueError):
                planner.set_category_budget("photography", 100)
        finally:
            os.unlink(path)

    def test_negative_amount_rejected(self):
        planner, path = self._planner()
        try:
            with self.assertRaises(ValueError):
                planner.add_item("Thing", "venue", actual=-50)
        finally:
            os.unlink(path)

    def test_remove_and_update(self):
        planner, path = self._planner()
        try:
            item = planner.add_item("Hall", "venue", actual=100)
            updated = planner.update_item(item.id, actual=150)
            self.assertEqual(updated.actual, 150)
            removed = planner.remove_item(item.id)
            self.assertEqual(removed.id, item.id)
            self.assertIsNone(planner.plan.find_item(item.id))
        finally:
            os.unlink(path)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
