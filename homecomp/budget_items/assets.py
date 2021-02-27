from typing import List

from homecomp.models import AssetMixin
from homecomp.models import BudgetItem
from homecomp.models import BudgetLineItem
from homecomp.models import MonthlyBudget
from homecomp.models import MonthlyExpense
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
                 buying_costs_rate: float = const.DEFAULT_HOME_BUYING_COSTS_PCT,
                 selling_costs_rate: float = const.DEFAULT_HOME_SELLING_COSTS_PCT,
                 **kwargs):
        lifetime = lifetime or []
        initial_value = price if const.INIT_PERIOD in lifetime else 0

        super().__init__(value=initial_value, **kwargs)
        self.price = price
        self.rate = appreciation
        self.lifetime = lifetime
        self.down_payment_pct = down_payment_pct
        self.buying_costs_rate = buying_costs_rate
        self.selling_costs_rate = selling_costs_rate

    def is_owned(self, period):
        if not self.lifetime:
            return True

        return period in self.lifetime

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

    def _purchasing_step(self, budget: MonthlyBudget) -> MonthlyExpense:
        """Set asset value and remove down payment and buying costs from cash flow"""
        self.value = self.price

        buying_costs = self.price * self.buying_costs_rate
        down_payment = self.price * self.down_payment_pct

        return MonthlyExpense(
            costs=-buying_costs,
            savings=-down_payment
        )

    def _selling_step(self, budget: MonthlyBudget) -> MonthlyExpense:
        """Clear asset value and add liquid asset value to budget minus selling costs"""        
        sell_price = self.value
        selling_costs = sell_price * self.selling_costs_rate

        self.value = 0

        return MonthlyExpense(
            costs=-selling_costs,
            savings=sell_price
        )

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        """Calculate cost for current period"""
        if self.period == self.buying_period:
            return self._purchasing_step(budget)
        elif self.period == self.selling_period:
            return self._selling_step(budget)

        self.value = round(self.value * (1 + self.rate), 2)
        return MonthlyExpense()
