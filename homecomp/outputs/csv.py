import csv
import os
from typing import List

from homecomp.models import BudgetItem
from homecomp.models import HousingDetail
from homecomp.models import MonthlyExpense
from homecomp.outputs import common


def write_expenses_csv(filename: str, expenses: List[MonthlyExpense]):  # pylint: disable=unused-argument
    with open(filename, mode='w') as output_fd:  # pylint: disable=unused-variable
        pass


def write_assets_csv(filename: str, budget_items: List[BudgetItem], periods: int):
    with open(filename, mode='w') as output_fd:
        headers, rows = common.get_asset_table(budget_items, periods)

        writer = csv.DictWriter(output_fd, fieldnames=headers)
        writer.writeheader()

        for row in rows:
            writer.writerow(row)


def write_csv(details: HousingDetail,
              budget_items: List[BudgetItem],
              expenses: List[MonthlyExpense],
              directory: str):
    """Write all computation results to csv output files"""
    write_assets_csv(
        filename=os.path.join(directory, f'{details.name}.expenses.csv'),
        budget_items=budget_items,
        periods=len(expenses) - 1
    )
    write_expenses_csv(
        filename=os.path.join(directory, f'{details.name}.assets.csv'),
        expenses=expenses
    )
