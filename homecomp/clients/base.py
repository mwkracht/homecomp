from dataclasses import dataclass

from homecomp import const


@dataclass
class HomeDetails:
    """Common object returned by clients to set properties on BudgetItems"""
    name: str
    link: str
    price: int
    hoa: int = 0
    property_tax_rate: float = const.DEFAULT_PROPERTY_TAX_PCT
