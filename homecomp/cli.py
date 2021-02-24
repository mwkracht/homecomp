# pylint: disable=too-many-arguments,redefined-outer-name,function-redefined,redefined-builtin
import click

from homecomp import clients
from homecomp import const
from homecomp import outputs
from homecomp.models import HousingDetails
from homecomp.models import HousingType
from homecomp.models import MonthlyBudget
from homecomp.budget_items.assets import Investment
from homecomp.budget_items.composite import HomeLifetime
from homecomp.budget_items.liabilities import MaxMortgage
from homecomp.budget_items.liabilities import MinMortgage
from homecomp.budget_items.misc import Rent
from homecomp.compute import compute


@click.group()
def buy():
    """Subset of calculations available for buying housing"""


@buy.command()
@click.argument('cash', type=click.INT)
@click.argument('budget', type=click.INT)
@click.argument('price', type=click.INT)
@click.option('--hoa', '-h', type=click.INT, default=0, help='Monthly HOA fee')
@click.option('--time', '-t', type=click.INT, default=5, help='Number of years to run calculation')
@click.option('--output', '-o', default='SimpleHome', help='Output file basename')
@click.option('--format', type=click.Choice(outputs.FORMATS), default=outputs.DEFAULT_FORMAT)
@click.option('--max-mortgage/--min-mortgage', default=False)
def simple(cash, budget, price, hoa, time, output, format, max_mortgage):
    """
    Simple buy calculation with a fixed monthly housing budget.

    Home will be sold during the last period of the calculation.
    """
    periods = time * const.PERIODS_PER_YEAR
    details = HousingDetails(
        name=output,
        price=price,
        hoa=hoa,
        type=HousingType.home
    )

    mortgage_cls = MaxMortgage if max_mortgage else MinMortgage

    budget_items = [
        HomeLifetime(
            name=f'{details.name}',
            lifetime=list(range(periods)),
            price=details.price,
            hoa_fee=details.hoa
        ),
        mortgage_cls(
            price=details.price,
            start=0,
        ),
        Investment(cash),
    ]

    budget = MonthlyBudget(budget)

    expenses = compute(
        budget,
        budget_items,
        periods=periods + 1
    )

    outputs.write(format, details, budget_items, expenses)


@buy.command()
@click.argument('cash', type=click.INT)
@click.argument('budget', type=click.INT)
@click.argument('link')
@click.option('--time', '-t', type=click.INT, default=5, help='Number of years to run calculations')
@click.option('--format', type=click.Choice(outputs.FORMATS), default=outputs.DEFAULT_FORMAT)
@click.option('--max-mortgage/--min-mortgage', default=False)
def zillow(cash, budget, link, time, format, max_mortgage):
    """Perform computation using Zillow shareable property link"""
    periods = time * const.PERIODS_PER_YEAR
    details = clients.zillow.get_home_details(link)

    mortgage_cls = MaxMortgage if max_mortgage else MinMortgage

    budget_items = [
        HomeLifetime(
            name=f'{details.name}',
            lifetime=list(range(periods)),
            price=details.price,
            hoa_fee=details.hoa,
            property_tax_rate=details.property_tax_rate
        ),
        mortgage_cls(
            price=details.price,
            start=0,
        ),
        Investment(cash),
    ]

    budget = MonthlyBudget(budget)

    expenses = compute(
        budget,
        budget_items,
        periods=periods + 1
    )

    outputs.write(format, details, budget_items, expenses)


@click.group()
def rent():
    """Subset of calculations available for renting housing"""


@rent.command()
@click.argument('cash', type=click.INT)
@click.argument('budget', type=click.INT)
@click.argument('rent', type=click.INT)
@click.option('--time', '-t', type=click.INT, default=5, help='Number of years to run calculation')
@click.option('--output', '-o', default='SimpleRental', help='Output files base name')
@click.option('--format', type=click.Choice(outputs.FORMATS), default=outputs.DEFAULT_FORMAT)
def simple(cash, budget, rent, time, output, format):
    """
    Simple rental calculation with a fixed monthly housing budget.
    """
    periods = time * const.PERIODS_PER_YEAR
    details = HousingDetails(
        name=output,
        price=rent,
        type=HousingType.rental
    )

    budget_items = [
        Rent(rent),
        Investment(cash),
    ]

    budget = MonthlyBudget(budget)

    expenses = compute(
        budget,
        budget_items,
        periods=periods + 1
    )

    outputs.write(format, details, budget_items, expenses)


@click.group()
def cli():
    pass


cli.add_command(buy)
cli.add_command(rent)


def main():
    cli()


if __name__ == "__main__":
    main()
