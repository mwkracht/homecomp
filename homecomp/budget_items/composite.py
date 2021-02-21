from typing import List

from homecomp.models import AssetMixin
from homecomp.models import BudgetLineItem
from homecomp.models import MonthlyBudget
from homecomp.models import MonthlyExpense
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
                 **kwargs):

        home = Home(lifetime=lifetime, **kwargs)

        super().__init__(
            name=name,
            budget_items=[
                HomeBuyingCosts(home=home, **kwargs),
                HomeSellingCosts(home=home, **kwargs),
                Maintenance(home=home,  **kwargs),
                PropertyTax(home=home,  **kwargs),
                HomeInsurance(home=home, **kwargs),
                home,
            ]
        )

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        expense = super()._step(budget)

        # track composite asset value to the underlying home value
        self.value = self.budget_items[-1].value

        return expense
