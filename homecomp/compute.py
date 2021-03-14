from typing import Dict
from typing import List
from typing import Tuple

from homecomp import const
from homecomp.budget_items.assets import Investment
from homecomp.budget_items.composite import HomeLifetime
from homecomp.budget_items.liabilities import MaxMortgage
from homecomp.budget_items.liabilities import MinMortgage
from homecomp.budget_items.misc import Rent
from homecomp.models import BudgetItem
from homecomp.models import HousingDetail
from homecomp.models import MonthlyBudget
from homecomp.models import MonthlyExpense
from homecomp.models import PurchaserProfile



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


def buy(purchaser: PurchaserProfile,
        housing: HousingDetail,
        years: int) -> Tuple[List[MonthlyExpense], List[BudgetItem]]:
    """Compute monthly expenses and asset values over the given years"""
    periods = years * const.PERIODS_PER_YEAR
    mortgage_cls = {
        'min': MinMortgage,
        'max': MaxMortgage,
    }[purchaser.mortgage_type]
    
    budget_items = [
        HomeLifetime(
            name=f'{housing.name}',
            lifetime=list(range(periods)),
            price=housing.price,
            property_tax_rate=housing.property_tax_rate,
            hoa_fee=housing.hoa,
            appreciation=const.yearly_to_period_rate(purchaser.home_appreciation)
        ),
        mortgage_cls(
            price=housing.price,
            start=0,
        ),
        Investment(purchaser.cash),
    ]

    expenses = compute(
        MonthlyBudget(purchaser.budget),
        budget_items,
        periods=periods + 1
    )

    return expenses, budget_items


def rent(purchaser: PurchaserProfile,
         housing: HousingDetail,
         years: int) -> Tuple[List[MonthlyExpense], List[BudgetItem]]:
    periods = years * const.PERIODS_PER_YEAR

    budget_items = [
        Rent(housing.price),
        Investment(purchaser.cash),
    ]

    budget = MonthlyBudget(purchaser.budget)

    expenses = compute(
        budget,
        budget_items,
        periods=periods + 1
    )

    return expenses, budget_items