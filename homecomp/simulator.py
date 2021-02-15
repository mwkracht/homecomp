from typing import Dict

from homecomp.base import BudgetItem
from homecomp.base import MonthlyBudget


def run(budget: MonthlyBudget,
        budget_items: Dict[str, BudgetItem],
        periods: int):
    """Run simulation over the given periods of time"""
    simulation = sim_iter(budget, budget_items)

    return [
        next(simulation)
        for i in range(periods)
    ]


def sim_iter(budget: MonthlyBudget,
             budget_items: Dict[str, BudgetItem]):
    """
    Budget simulation iterator where each item returned is a single period's budget.
    """
    while True:
        expenses = {}

        for name, budget_item in budget_items.items():
            expense = budget_item.step(budget)

            expenses[name] = expense
            budget -= expense

        yield expenses
