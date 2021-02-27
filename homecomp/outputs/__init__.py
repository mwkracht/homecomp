from typing import List
import os

from homecomp.models import BudgetItem
from homecomp.models import HousingDetail
from homecomp.models import MonthlyExpense
from homecomp.outputs.common import format_currency
from homecomp.outputs.csv import write_csv
from homecomp.outputs.html import write_html


FORMAT_MAP = {
    'html': write_html,
    'csv': write_csv,
}
FORMATS = list(FORMAT_MAP.keys())
DEFAULT_FORMAT = FORMATS[0]


def write(choice: str,
          details: HousingDetail,
          budget_items: List[BudgetItem],
          expenses: List[MonthlyExpense],
          directory: str):
    if choice not in FORMATS:
        raise ValueError(f'{choice} is not an acceptable format')

    os.makedirs(directory, exist_ok=True)

    return FORMAT_MAP[choice](details, budget_items, expenses, directory)
