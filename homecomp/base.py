from abc import abstractmethod
from abc import ABC
from abc import ABCMeta


class MonthlyExpense:
    """
    Each BudgetItem will produce a MonthlyExpense which represents the
    total impact of the BudgetItem on the monthly budget.

    MonthlyExpense will allow the total hit to the budget to be categorized.
    Savings would be an expense to the budget that builds value while cost
    is a budget expense which does not have any impact on value of underlying
    assets.
    """

    def __init__(self, savings=0, costs=0):
        """Costs should be provided as negative values - use positive values to represent income"""
        self.savings = savings
        self.costs = costs

    def __add__(self, other):
        if not isinstance(other, MonthlyExpense):
            raise RuntimeError('Cannot add MonthlyExpense with {}'.format(type(other)))

        return MonthlyExpense(
            savings=self.savings + other.savings,
            costs=self.costs + other.costs
        )

    def __radd__(self, other):
        return self.__add__(other)

    @property
    def total(self):
        return self.savings + self.costs

    def __repr__(self):
        return 'MonthlyExpense(savings={}, costs={})'.format(
            self.savings, self.costs
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

    def __init__(self):
        self.period = 0

    @abstractmethod
    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        pass

    def step(self, budget: MonthlyBudget) -> MonthlyExpense:
        expense = self._step(budget)

        self.period += 1
        return expense


class NetworthBudgetItem(BudgetItem, metaclass=ABCMeta):
    """Tracks underlying value while also generating monthly expenses"""

    def __init__(self, value=0):
        super().__init__()
        # track underlying value of asset for each period where each key represents the value
        # of the object at the beginning of that period
        self.values = {0: value}

    @property
    def value(self):
        """Read value of asset from most recently set period"""
        return next(
            self.values[i]
            for i in reversed(range(0, self.period + 2))
            if i in self.values
        )

    @value.setter
    def value(self, value):
        """Set value of asset for current period"""
        self.values[self.period + 1] = value

    def get_period_value(self, period):
        """Return value from a specific period"""
        return self.values.get(period, self.value)


class Asset(NetworthBudgetItem, metaclass=ABCMeta):
    """Positive value NetworthBudgetItem"""


class Liability(NetworthBudgetItem, metaclass=ABCMeta):
    """Negative value NetworthBudgetItem"""
