from typing import List

from homecomp.base import AssetMixin
from homecomp.base import BudgetLineItem
from homecomp.base import MonthlyBudget
from homecomp.base import MonthlyExpense
from homecomp.budget_items.assets import Home
from homecomp.budget_items.misc import HomeBuyingCosts
from homecomp.budget_items.misc import HomeInsurance
from homecomp.budget_items.misc import HomeSellingCosts
from homecomp.budget_items.misc import Maintenance
from homecomp.budget_items.misc import PropertyTax


class HomeLifetime(AssetMixin, BudgetLineItem):
    """
    Composite object with all underlying BudgetItems associated with home ownership
    """

    def __init__(self,
                 name: str,
                 lifetime: List[int],
                 premium: int,
                 **kwargs):

        home = Home(lifetime=lifetime, **kwargs)

        super().__init__(
            name=name,
            budget_items=[
                home,
                HomeBuyingCosts(home=home, **kwargs),
                HomeSellingCosts(home=home, **kwargs),
                Maintenance(home=home,  **kwargs),
                PropertyTax(home=home,  **kwargs),
                HomeInsurance(home=home, premium=premium, **kwargs),
            ]
        )

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        expense = super()._step(budget)

        # track composite asset value to the underlying home value
        self.value = self.budget_items[0].value

        return expense
