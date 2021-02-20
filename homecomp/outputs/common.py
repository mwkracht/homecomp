from datetime import date
from typing import Dict
from typing import Iterator
from typing import List
from typing import Tuple

from dateutil.relativedelta import relativedelta

from homecomp import const
from homecomp.models import BudgetItem
from homecomp.models import NetworthMixin


def format_currency(value) -> str:
    currency = '${:,.2f}'.format(abs(value))
    if value < 0:
        currency = f'({currency})'
    return currency


def iter_months(start: date = None) -> Iterator[str]:
    start = start or date.today()

    while True:
        yield start.strftime('%b, %Y')
        start += relativedelta(months=1)


def get_networth_items(budget_items: List[BudgetItem]) -> Dict[str, BudgetItem]:
    """Return only budget items which have value"""
    return {
        budget_item.name: budget_item
        for budget_item in budget_items
        if isinstance(budget_item, NetworthMixin)
    }


def get_asset_table(budget_items: List[BudgetItem], periods: int) -> Tuple:
    networth_items = get_networth_items(budget_items)
    months = iter_months()

    headers = ['Time']
    headers += list(networth_items.keys())
    headers += ['Total']

    rows = []
    for period in range(const.INIT_PERIOD, periods + 1):
        row = {'Time': next(months)}
        row.update({
            key: format_currency(networth_item.get_period_value(period))
            for key, networth_item in networth_items.items()
        })
        row['Total'] = format_currency(sum(
            networth_item.get_period_value(period)
            for networth_item in networth_items.values()
        ))

        rows.append(row)

    return headers, rows
