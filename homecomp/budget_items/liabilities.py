from homecomp.base import BudgetItem
from homecomp.base import LiabilityMixin
from homecomp.base import MonthlyBudget
from homecomp.base import MonthlyExpense
from homecomp import const


def calculate_min_payment(principal, rate, length):
    x = (1 + rate) ** length
    return round(principal * (rate * x) / (x - 1), 2)


class Mortgage(LiabilityMixin, BudgetItem):
    """
    Equated Monthly Installment (EMI) Mortgage
    """

    def __init__(self,
                 price: int,
                 payment: int = 0,
                 down_payment_pct: float = const.DEFAULT_DOWN_PAYMENT_PCT,
                 rate: float = const.DEFAULT_MORTGAGE_RATE,
                 start: int = const.INIT_PERIOD,
                 **kwargs):
        super().__init__(**kwargs)
        self.principal = price * (1 - down_payment_pct)
        self.rate = rate
        self.payment = payment
        self.start = start

    @property
    def total_paid(self):
        return self.period * self.payment

    @property
    def principal_paid(self):
        return self.principal + self.value

    @property
    def interest_paid(self):
        return self.total_paid - self.principal_paid

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        """Calculate cost for current period"""
        if self.start == self.period:
            self.value = -self.principal
        if self.value >= 0:
            return MonthlyExpense()

        interest = round(abs(self.value * self.rate), 2)
        self.value -= interest

        payment = min([self.payment, -self.value])
        self.value += payment

        return MonthlyExpense(
            savings=-(payment - interest),
            costs=-interest
        )


class MinimumPaymentMortgage(Mortgage):
    """
    Make the same minimum payment every month.
    """

    def __init__(self,
                 length: int = const.DEFAULT_MORTGAGE_PERIODS,
                 **kwargs):
        super().__init__(**kwargs)
        self.payment = calculate_min_payment(self.principal, self.rate, length)


class VariablePaymentMortgage(MinimumPaymentMortgage):
    """
    All excess budget goes towards paying down the principal.
    """

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        """Calculate cost for current period"""
        if self.start - 1 == self.period:
            self.value = -self.principal  # set value but do not accrue interest
            return MonthlyExpense()

        if self.value >= 0:
            return MonthlyExpense()

        interest = round(abs(self.value * self.rate), 2)
        self.value -= interest

        payment = max([budget.remaining, self.payment])
        payment = min([payment, -self.value])
        self.value += payment

        return MonthlyExpense(
            savings=-(payment - interest),
            costs=-interest
        )
