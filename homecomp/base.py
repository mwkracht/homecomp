from abc import abstractmethod
from abc import ABC
from abc import ABCMeta
from typing import List

from homecomp import const


class MonthlyExpense:
    """
    Each BudgetItem will produce a MonthlyExpense which represents the
    total impact of the BudgetItem on the monthly budget.

    MonthlyExpense .

    Savings would be an expense to the budget that builds value while cost
    is a budget expense which does not have any impact on value of underlying
    assets.
    """

    def __init__(self,
                 name: str = '',
                 savings: int = 0,
                 costs: int = 0,
                 components: List = None):
        """Costs should be provided as negative values - use positive values to represent income"""
        self.name = name
        self.savings = savings
        self.costs = costs
        self.components = components or []

    @classmethod
    def join(cls, name: str, expenses: List):
        """Join mulitiple expenses under a single name"""
        return MonthlyExpense(
            name=name,
            savings=sum(expense.savings for expense in expenses),
            costs=sum(expense.costs for expense in expenses),
            components=[
                component
                for expense in expenses
                for component in expense.components
            ]
        )

    @property
    def total(self):
        return self.savings + self.costs

    def __repr__(self):
        return 'MonthlyExpense(name={}, savings={}, costs={})'.format(
            self.name, self.savings, self.costs
        )


class MonthlyBudget:
    """Fixed budget which MonthlyExpenses can be deducted from"""

    def __init__(self, budget: int, remaining: int = None):
        self.budget = budget
        self.remaining = remaining or budget

    def __sub__(self, other):
        if not isinstance(other, MonthlyExpense):
            raise RuntimeError('Cannot subtract MonthlyBudget with {}'.format(type(other)))

        return MonthlyBudget(
            budget=self.budget,
            remaining=self.remaining + other.total
        )

    def __rsub__(self, other):
        return self.__sub__(other)

    def __repr__(self):
        return 'MonthlyBudget(budget={}, remaining={})'.format(
            self.budget, self.remaining
        )


class BudgetItem(ABC):

    def __init__(self, name: str = None, **kwargs):  # pylint: disable=unused-argument
        self.name = name or self.__class__.__name__
        self.period = const.INIT_PERIOD

    @abstractmethod
    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        pass

    def step(self, budget: MonthlyBudget) -> MonthlyExpense:
        expense = self._step(budget)
        if not expense.name:
            expense.name = self.name

        self.period += 1
        return expense


class BudgetLineItem(BudgetItem):
    """BudgetItem composite class"""

    def __init__(self, budget_items: List[BudgetItem] = None, **kwargs):
        super().__init__(**kwargs)
        self.budget_items = budget_items or []

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        expenses = []

        for budget_item in self.budget_items:
            expenses.append(budget_item.step(budget))
            budget -= expenses[-1]

        return MonthlyExpense.join(self.name, expenses)


class NetworthMixin(metaclass=ABCMeta):
    """Tracks underlying value over time"""

    def __init__(self, value=0, **kwargs):
        super().__init__(**kwargs)

        # track underlying value of asset for each period where each key represents the value
        # of the object at the beginning of that period
        self.values = {const.INIT_PERIOD: value}

    @property
    def value(self):
        """Read value of asset from most recently set period"""
        return next(
            self.values[i]
            for i in reversed(range(const.INIT_PERIOD, self.period + 2))
            if i in self.values
        )

    @value.setter
    def value(self, value):
        """Set value of asset for current period"""
        self.values[self.period + 1] = value

    def get_period_value(self, period):
        """Return value from a specific period"""
        return self.values.get(period, self.value)


class AssetMixin(NetworthMixin, metaclass=ABCMeta):
    """Positive value categorization of NetworthMixin"""


class LiabilityMixin(NetworthMixin, metaclass=ABCMeta):
    """Negative value categorization NetworthMixin"""
