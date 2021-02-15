from homecomp.base import Liability
from homecomp.base import MonthlyBudget
from homecomp.base import MonthlyExpense
from homecomp import const


def calculate_min_payment(principal, rate, periods):
    x = (1 + rate) ** periods
    return round(principal * (rate * x) / (x - 1), 2)


class Mortgage(Liability):
    """
    Equated Monthly Installment (EMI) Mortgage
    """

    def __init__(self,
                 principal,
                 payment,
                 rate=const.DEFAULT_MORTGAGE_RATE):
        super().__init__(value=-principal)
        self.principal = principal
        self.rate = rate
        self.payment = payment

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
                 principal,
                 rate=const.DEFAULT_MORTGAGE_RATE,
                 periods=const.DEFAULT_MORTGAGE_PERIODS):
        super().__init__(
            principal=principal,
            rate=rate,
            payment=calculate_min_payment(principal, rate, periods)
        )


class VariablePaymentMortgage(MinimumPaymentMortgage):
    """
    All excess budget goes towards paying down the principal.
    """

    def _step(self, budget: MonthlyBudget) -> MonthlyExpense:
        """Calculate cost for current period"""
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
