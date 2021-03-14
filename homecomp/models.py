# pylint: disable=too-many-instance-attributes
from abc import abstractmethod
from abc import ABC
from abc import ABCMeta
from dataclasses import dataclass
from dataclasses import field
from typing import List

from homecomp import const


@dataclass
class HousingDetail:
    name: str
    price: int
    type: str
    link: str = None
    image: str = None
    hoa: int = 0
    property_tax_rate: float = const.DEFAULT_PROPERTY_TAX_PCT
    bedrooms: int = None
    bathrooms: int = None
    home_size: int = None
    lot_size: int = None


@dataclass
class PurchaserProfile:
    name: str
    cash: int
    budget: int
    mortgage_type: str = 'min'
    home_appreciation: float = const.DEFAULT_HOME_APPRECIATION


@dataclass
class MonthlyExpense:
    """
    Each BudgetItem will produce a MonthlyExpense which represents the
    total impact of the BudgetItem on the monthly budget.

    Savings would be an expense to the budget that builds value while cost
    is a budget expense which does not have any impact on value of underlying
    assets.
    """
    period: int = const.NEVER_PERIOD
    name: str = ''
    savings: int = 0
    costs: int = 0
    components: List = field(default_factory=list)

    @classmethod
    def join(cls, name: str, expenses: List):
        """Join mulitiple expenses under a single name"""
        periods = set(expense.period for expense in expenses)
        if len(periods) != 1:
            raise ValueError('Cannot join expenses from different periods')

        return MonthlyExpense(
            period=list(periods)[0],
            name=name,
            savings=sum(expense.savings for expense in expenses),
            costs=sum(expense.costs for expense in expenses),
            components=expenses
        )

    @property
    def total(self):
        return self.savings + self.costs


@dataclass
class MonthlyBudget:
    """Fixed budget which MonthlyExpenses can be deducted from"""
    budget : int
    remaining : int = None

    def __post_init__(self):
        if self.remaining is None:
            self.remaining = self.budget

    def __sub__(self, other):
        if not isinstance(other, MonthlyExpense):
            raise RuntimeError('Cannot subtract MonthlyBudget with {}'.format(type(other)))

        return MonthlyBudget(
            budget=self.budget,
            remaining=self.remaining + other.total
        )

    def __rsub__(self, other):
        return self.__sub__(other)

    def new(self):
        """Create new budget instance with full budget remaining"""
        return self.__class__(budget=self.budget)


class BudgetItem(ABC):

    def __init__(self, name: str = None, **kwargs):  # pylint: disable=unused-argument
        self.name = name or self.__class__.__name__
        self.period = const.INIT_PERIOD

    @abstractmethod
    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        pass

    def step(self, budget: MonthlyBudget) -> MonthlyExpense:
        expense = self._step(budget)
        expense.name = self.name
        expense.period = self.period

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
        """
        Read value of asset from most recently set period.

        This means the first value read will be from the current period. Once
        a value is written then the next read from self.value will return the
        value from the next period (not the current period)
        """
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
