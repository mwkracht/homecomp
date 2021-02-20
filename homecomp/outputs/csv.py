import csv
from typing import List

from homecomp.models import BudgetItem
from homecomp.models import HousingDetails
from homecomp.models import MonthlyExpense
from homecomp.outputs import common


def write_expenses_csv(filename: str, expenses: List[MonthlyExpense]):  # pylint: disable=unused-argument
    with open(f'{filename}.expenses.csv', mode='w') as output_fd:  # pylint: disable=unused-variable
        pass


def write_assets_csv(filename: str, budget_items: List[BudgetItem], periods: int):
    with open(f'{filename}.assets.csv', mode='w') as output_fd:
        headers, rows = common.get_asset_table(budget_items, periods)

        writer = csv.DictWriter(output_fd, fieldnames=headers)
        writer.writeheader()

        for row in rows:
            writer.writerow(row)


def write_csv(details: HousingDetails,
              budget_items: List[BudgetItem],
              expenses: List[MonthlyExpense]):
    """Write all computation results to csv output files"""
    write_assets_csv(details.name, budget_items, len(expenses))
    write_expenses_csv(details.name, expenses)
