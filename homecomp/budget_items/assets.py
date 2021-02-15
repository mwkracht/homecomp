from homecomp.base import Asset
from homecomp.base import MonthlyBudget
from homecomp.base import MonthlyExpense
from homecomp import const


class Investment(Asset):
    """
    Simple Investment.

    Always generates expected return and invests remaining budget. If the
    budget is negative then the assumption is that the investment is liquid
    enough to fill any budget gaps.
    """

    def __init__(self,
                 principal=0,
                 rate=const.DEFAULT_INVESTMENT_RETURN_RATE):
        super().__init__(value=principal)
        self.rate = rate

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        """Calculate cost for current period"""
        self.value = round(self.value * (1 + self.rate), 2)
        self.value += budget.remaining

        return MonthlyExpense(
            savings=-budget.remaining,
            costs=0
        )


class Home(Asset):
    """
    Simple Home.

    Behaves the same way as an investment only with different default rate of return
    and no monthly budget contribution.
    """

    def __init__(self,
                 list_price,
                 rate=const.DEFAULT_HOME_APPRECIATION_RATE):
        super().__init__(value=list_price)
        self.rate = rate

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        """Calculate cost for current period"""
        self.value = round(self.value * (1 + self.rate), 2)
        return MonthlyExpense()
