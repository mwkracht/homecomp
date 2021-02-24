from homecomp import const
from homecomp.models import BudgetItem
from homecomp.models import MonthlyBudget
from homecomp.models import MonthlyExpense
from homecomp.budget_items.assets import Home


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
        costs = 0

        if self.home.is_owned(self.period):
            costs = -self.hoa_fee

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
        costs = 0

        if self.home.is_owned(self.period):
            costs = -(self.home.value * self.rate)

        return MonthlyExpense(costs=costs)


class PropertyTax(BudgetItem):
    """Property tax assessed once per year against a given home"""

    def __init__(self,
                 home: Home,
                 property_tax_rate: float = const.DEFAULT_PROPERTY_TAX_PCT,
                 **kwargs):
        super().__init__(**kwargs)
        self.home = home
        self.rate = property_tax_rate

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        if self.home.is_owned(self.period) and self.period % 12 == 11:
            return MonthlyExpense(
                costs=-(self.home.value * self.rate)
            )

        return MonthlyExpense()


class HomeInsurance(BudgetItem):

    def __init__(self,
                 home: Home,
                 home_insurance_rate: float = const.DEFAULT_HOME_INURANCE_PCT,
                 **kwargs):
        super().__init__(**kwargs)
        self.home = home
        self.rate = home_insurance_rate

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        if self.home.is_owned(self.period) and self.period % 12 == 11:
            return MonthlyExpense(
                costs=-(self.home.value * self.rate)
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
