from typing import Dict

from homecomp.base import BudgetItem
from homecomp.base import MonthlyBudget
from homecomp.base import MonthlyExpense


def compute(budget: MonthlyBudget,
            budget_items: Dict[str, BudgetItem],
            periods: int):
    """Run computation over the given periods of time"""
    computation = compute_iter(budget, budget_items)

    return [
        next(computation)
        for i in range(periods)
    ]


def compute_iter(budget: MonthlyBudget,
                 budget_items: Dict[str, BudgetItem]):
    """
    Budget computation iterator where each item returned is a single period's budget.
    """
    while True:
        expenses = []

        for budget_item in budget_items:
            expenses.append(budget_item.step(budget))
            budget -= expenses[-1]

        # import pdb;pdb.set_trace()
        yield MonthlyExpense.join('total', expenses)
