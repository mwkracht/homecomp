from typing import List

from homecomp.base import AssetMixin
from homecomp.base import BudgetItem
from homecomp.base import BudgetLineItem
from homecomp.base import MonthlyBudget
from homecomp.base import MonthlyExpense
from homecomp import const


class Investment(AssetMixin, BudgetItem):
    """
    Simple Investment.

    Always generates expected return and invests remaining budget. If the
    budget is negative then the assumption is that the investment is liquid
    enough to fill any budget gaps.
    """

    def __init__(self,
                 principal: int = 0,
                 roi: float = const.DEFAULT_INVESTMENT_RETURN_RATE,
                 **kwargs):
        super().__init__(value=principal, **kwargs)
        self.rate = roi

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        """Calculate cost for current period"""
        self.value = round(self.value * (1 + self.rate), 2)
        self.value += budget.remaining

        return MonthlyExpense(
            savings=-budget.remaining,
            costs=0
        )


class Home(AssetMixin, BudgetItem):
    """
    Simple Home.

    Behaves the same way as an investment only with different default rate of return
    and no monthly budget contribution.
    """

    def __init__(self,
                 price: int,
                 lifetime: List[int] = None,
                 down_payment_pct: float = const.DEFAULT_DOWN_PAYMENT_PCT,
                 appreciation: float = const.DEFAULT_HOME_APPRECIATION_RATE,
                 **kwargs):
        lifetime = lifetime or []
        initial_value = price if const.INIT_PERIOD in lifetime else 0

        super().__init__(value=initial_value, **kwargs)
        self.price = price
        self.rate = appreciation
        self.lifetime = lifetime
        self.down_payment_pct = down_payment_pct

    @property
    def owned(self):
        if not self.lifetime:
            return True

        return self.period in self.lifetime

    @property
    def buying_period(self):
        if not self.lifetime:
            return const.NEVER_PERIOD

        return self.lifetime[0] - 1  # bought period before the first period the home is owned
    
    @property
    def selling_period(self):
        if not self.lifetime:
            return const.NEVER_PERIOD

        return self.lifetime[-1]
    
    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        """Calculate cost for current period"""
        if self.period == self.buying_period:
            # set asset value and remove down payment from cash flow
            self.value = self.price
            return MonthlyExpense(costs=-(self.price * self.down_payment_pct))

        elif self.period == self.selling_period:
            sell_price = self.value
            self.value = 0
            return MonthlyExpense(savings=sell_price)

        self.value = round(self.value * (1 + self.rate), 2)
        return MonthlyExpense()
