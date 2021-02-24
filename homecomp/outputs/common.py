import itertools
from datetime import date
from typing import Dict
from typing import Iterator
from typing import List
from typing import Tuple

from dateutil.relativedelta import relativedelta

from homecomp import const
from homecomp.models import BudgetItem
from homecomp.models import MonthlyExpense
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


def _traverse_expense(expense: MonthlyExpense, column: str = '') -> Dict:
    """
    Build an expense row by traversing expense tree.

    Flip all of the expense totals so that expenses are displayed as positives.
    """
    if not expense.components:
        return {column: format_currency(-expense.total)}

    column = f'{column}.' if column else ''
    row = {}

    for component in expense.components:
        row.update(_traverse_expense(component, f'{column}{component.name}'))

    row[f'{column}Total'] = format_currency(-expense.total)
    return row


def get_expense_table(expenses: List[MonthlyExpense]):
    months = iter_months(date.today() + relativedelta(months=1))

    rows = [
        {
            'Time': next(months),
            **_traverse_expense(expense)
        }
        for expense in expenses
    ]

    headers = list(rows[0].keys())

    if any(set(row.keys()) != set(headers) for row in rows[1:]):
        raise ValueError('Allxpenses are not available across all periods')

    return headers, rows


def get_header_spans(headers: List[str]):
    """
    Split list of composite headers into simple headers with colspan values.

    If table headers are composite values (e.x. Home.Mortage) then return a list of
    header rows that group each header value under common parent headers. For the following
    header grouping:

    |      |           Home              |       |
    | Time | Mortage | ... | Maintenance | Total |

    The output would be:

    [
        [('', 1), ('Home', 3), ('', 1)],
        [('Time', 1), ('Mortgage', 1), ('...', 1), ('Maintenance', 1), ('Total', 1)]
    ]
    """
    header_rows = []
    split_headers = [
        header.split('.')
        for header in headers
    ]
    max_split = max([len(header) for header in split_headers])

    for idx in range(-1, -max_split - 1, -1):
        header_row = []

        for header in split_headers:
            try:
                header_row.append(header[idx])
            except IndexError:
                header_row.append('')

        # group headers together into spans
        header_row = [
            (key, len(list(group)))
            for key, group in itertools.groupby(header_row)
        ]

        header_rows = [header_row] + header_rows

    return header_rows
