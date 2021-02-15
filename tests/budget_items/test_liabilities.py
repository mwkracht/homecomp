import pytest

from homecomp.budget_items.liabilities import calculate_min_payment


@pytest.mark.parametrize("principal, rate, periods, output", [
    (400000, 0.03 / 12, 360, 1686.42),
    (100000, 0.025 / 12, 180, 666.79)
])
def test_calculate_min_payment(principal, rate, periods, output):
    """Ensure method correctly calculates minimum monthly payment for given loan params"""
    assert output == calculate_min_payment(principal, rate, periods)
