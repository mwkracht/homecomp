from homecomp import const
from homecomp.base import BudgetItem
from homecomp.base import MonthlyBudget
from homecomp.base import MonthlyExpense
from homecomp.budget_items.assets import Home


class HomeBuyingCosts(BudgetItem):
    """
    Upfront one time costs associated with buying a home
    """

    def __init__(self,
                 home: Home = None,
                 rate: float = const.DEFAULT_HOME_BUYING_COSTS_PCT):
        super().__init__()
        self.rate = rate
        self.home = home

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        if self.period == 0:
            return MonthlyExpense(
                costs=-(self.home.value * self.rate)
            )

        return MonthlyExpense()


class HomeSellingCosts(BudgetItem):
    """
    One time costs associated with selling a home
    """

    def __init__(self,
                 home: Home,
                 sell_period: int,
                 rate: float = const.DEFAULT_HOME_SELLING_COSTS_PCT):
        super().__init__()
        self.rate = rate
        self.home = home
        self.sell_period = sell_period

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        if self.period == self.sell_period:
            return MonthlyExpense(
                costs=-(self.home.value * self.rate)
            )

        return MonthlyExpense()


class HOA(BudgetItem):
    """Monthly HOA fee"""

    def __init__(self, fee: int):
        super().__init__()
        self.fee = fee

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        return MonthlyExpense(costs=-self.fee)


class Maintenance(BudgetItem):
    """Monthly maintenance costs as a fixed ratio of home value"""

    def __init__(self,
                 home: Home = None,
                 rate: float = const.DEFAULT_HOME_MAINTENANCE_RATE):
        super().__init__()
        self.rate = rate
        self.home = home

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        return MonthlyExpense(
            costs=-(self.home.value * self.rate)
        )


class PropertyTax(BudgetItem):
    """Property tax assessed once per year against a given home"""
    def __init__(self,
                 home: Home = None,
                 rate: float = const.DEFAULT_PROPERTY_TAX_RATE):
        super().__init__()
        self.rate = rate
        self.home = home

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        if self.period % 12 == 11:
            return MonthlyExpense(
                costs=-(self.home.value * self.rate)
            )

        return MonthlyExpense()


class HomeInsurance(BudgetItem):

    def __init__(self, premium: int):
        super().__init__()
        self.premium = premium

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        if self.period % 12 == 11:
            return MonthlyExpense(
                costs=-self.premium
            )

        return MonthlyExpense()


class Rent(BudgetItem):

    def __init__(self, rent: int, rate: float = const.DEFAULT_RENT_INCREASE_PCT):
        super().__init__()
        self.rate = rate
        self.rent = rent

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        if self.period % 12 == 11:
            self.rent *= (self.rate + 1)

        return MonthlyExpense(
            costs=-self.rent
        )
