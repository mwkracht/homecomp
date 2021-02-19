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
                 home: Home,
                 buying_costs_rate: float = const.DEFAULT_HOME_BUYING_COSTS_PCT,
                 **kwargs):
        super().__init__(**kwargs)
        self.home = home
        self.rate = buying_costs_rate

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        if self.period == self.home.buying_period:
            return MonthlyExpense(
                costs=-(self.home.price * self.rate)
            )

        return MonthlyExpense()


class HomeSellingCosts(BudgetItem):
    """
    One time costs associated with selling a home
    """

    def __init__(self,
                 home: Home,
                 selling_costs_rate: float = const.DEFAULT_HOME_SELLING_COSTS_PCT,
                 **kwargs):
        super().__init__(**kwargs)
        self.home = home
        self.rate = selling_costs_rate

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        if self.home.selling_period == self.period:
            return MonthlyExpense(
                costs=-(self.home.value * self.rate)
            )

        return MonthlyExpense()


class HOA(BudgetItem):
    """Monthly HOA fee"""

    def __init__(self,
                 home: Home,
                 hoa_fee: int,
                 **kwargs):
        super().__init__(**kwargs)
        self.home = home
        self.hoa_fee = hoa_fee

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        costs = -self.hoa_fee if self.home.owned else 0

        return MonthlyExpense(costs=costs)


class Maintenance(BudgetItem):
    """Monthly maintenance costs as a fixed ratio of home value"""

    def __init__(self,
                 home: Home = None,
                 maintenance_rate: float = const.DEFAULT_HOME_MAINTENANCE_RATE,
                 **kwargs):
        super().__init__(**kwargs)
        self.home = home
        self.rate = maintenance_rate

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        costs = -(self.home.value * self.rate) if self.home.owned else 0

        return MonthlyExpense(costs=costs)


class PropertyTax(BudgetItem):
    """Property tax assessed once per year against a given home"""
    def __init__(self,
                 home: Home,
                 property_tax_rate: float = const.DEFAULT_PROPERTY_TAX_RATE,
                 **kwargs):
        super().__init__(**kwargs)
        self.home = home
        self.rate = property_tax_rate

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        if self.home.owned and self.period % 12 == 11:
            return MonthlyExpense(
                costs=-(self.home.value * self.rate)
            )

        return MonthlyExpense()


class HomeInsurance(BudgetItem):

    def __init__(self,
                 home: Home,
                 premium: int,
                 **kwargs):
        super().__init__(**kwargs)
        self.home = home
        self.premium = premium

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        if self.home.owned and self.period % 12 == 11:
            return MonthlyExpense(
                costs=-self.premium
            )

        return MonthlyExpense()


class Rent(BudgetItem):

    def __init__(self,
                 rent: int,
                 rent_increase_rate: float = const.DEFAULT_RENT_INCREASE_PCT,
                 **kwargs):
        super().__init__(**kwargs)
        self.rate = rent_increase_rate
        self.rent = rent

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        if self.period % 12 == 11:
            self.rent *= (self.rate + 1)

        return MonthlyExpense(
            costs=-self.rent
        )
