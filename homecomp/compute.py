from typing import Dict

from homecomp.models import BudgetItem
from homecomp.models import MonthlyBudget
from homecomp.models import MonthlyExpense


def compute(budget: MonthlyBudget,
            budget_items: Dict[str, BudgetItem],
            periods: int):
    """Run computation over the given periods of time"""
    computation = compute_iter(budget, budget_items)

    return [
        next(computation)
        for _ in range(periods)
    ]


def compute_iter(budget: MonthlyBudget,
                 budget_items: Dict[str, BudgetItem]):
    """
    Budget computation iterator where each item returned is a single period's budget.
    """
    while True:
        m_expenses = []
        m_budget = budget.new()

        for budget_item in budget_items:
            m_expenses.append(budget_item.step(m_budget))
            m_budget -= m_expenses[-1]

        yield MonthlyExpense.join('total', m_expenses)
