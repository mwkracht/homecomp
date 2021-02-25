# pylint: disable=too-many-arguments
import click

from homecomp import clients
from homecomp import const
from homecomp import errors
from homecomp import outputs
from homecomp.models import PurchaserProfile
from homecomp.models import HousingDetail
from homecomp.models import HousingType
from homecomp.models import MonthlyBudget
from homecomp.budget_items.assets import Investment
from homecomp.budget_items.composite import HomeLifetime
from homecomp.budget_items.liabilities import MaxMortgage
from homecomp.budget_items.liabilities import MinMortgage
from homecomp.budget_items.misc import Rent
from homecomp.compute import compute
from homecomp.storage import DataclassFileStorage


def get_purchaser_profile(purchaser):
    try:
        with DataclassFileStorage() as storage:
            return storage.profiles.find(purchaser)
    except errors.NoEntryFound as error:
        raise click.ClickException(f'No profile found for {purchaser}') from error


@click.group()
def profiles():
    """Commands for manipulating purchasing profiles"""


@profiles.command(name='add')
@click.argument('name')
@click.argument('cash', type=click.INT)
@click.argument('budget', type=click.INT)
def profiles_add(name, cash, budget):
    with DataclassFileStorage() as storage:
        profile = PurchaserProfile(
            name=name,
            cash=cash,
            budget=budget
        )

        storage.profiles.save(profile, overwrite=False)


@profiles.command(name='update')
@click.argument('name')
@click.argument('cash', type=click.INT)
@click.argument('budget', type=click.INT)
def profiles_update(name, cash, budget):
    with DataclassFileStorage() as storage:
        profile = PurchaserProfile(
            name=name,
            cash=cash,
            budget=budget
        )

        storage.profiles.save(profile)


@profiles.command(name='list')
@click.argument('name', nargs=-1)
def profiles_list(name):
    with DataclassFileStorage() as storage:
        _profiles = storage.profiles.find_all(name[0]) if name else storage.profiles

        for profile in _profiles:
            click.echo(profile)


@profiles.command(name='remove')
@click.argument('name')
def profiles_remove(name):
    try:
        with DataclassFileStorage() as storage:
            storage.profiles.delete(name)
    except errors.NoEntryFound:
        click.echo(f'No profile found for {name}')


@click.group()
def buy():
    """Subset of calculations available for buying housing"""


@buy.command(name='simple')
@click.argument('purchaser')
@click.argument('price', type=click.INT)
@click.option('--hoa', '-h', type=click.INT, default=0, help='Monthly HOA fee')
@click.option('--time', '-t', type=click.INT, default=5, help='Number of years to run calculation')
@click.option('--output', '-o', default='SimpleHome', help='Output file basename')
@click.option('--format', type=click.Choice(outputs.FORMATS), default=outputs.DEFAULT_FORMAT)
@click.option('--max-mortgage/--min-mortgage', default=False)
def buy_simple(purchaser, price, hoa, time, output, format, max_mortgage):  # pylint: disable=redefined-builtin
    """
    Simple buy calculation with a fixed monthly housing budget.

    Home will be sold during the last period of the calculation.
    """
    purchaser_profile = get_purchaser_profile(purchaser)

    periods = time * const.PERIODS_PER_YEAR
    details = HousingDetail(
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
        Investment(purchaser_profile.cash),
    ]

    budget = MonthlyBudget(purchaser_profile.budget)

    expenses = compute(
        budget,
        budget_items,
        periods=periods + 1
    )

    outputs.write(format, details, budget_items, expenses)


@buy.command(name='zillow')
@click.argument('purchaser')
@click.argument('link')
@click.option('--time', '-t', type=click.INT, default=5, help='Number of years to run calculations')
@click.option('--format', type=click.Choice(outputs.FORMATS), default=outputs.DEFAULT_FORMAT)
@click.option('--max-mortgage/--min-mortgage', default=False)
def buy_zillow(purchaser, link, time, format, max_mortgage):  # pylint: disable=redefined-builtin
    """Perform computation using Zillow shareable property link"""
    purchaser_profile = get_purchaser_profile(purchaser)

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
        Investment(purchaser_profile.cash),
    ]

    budget = MonthlyBudget(purchaser_profile.budget)

    expenses = compute(
        budget,
        budget_items,
        periods=periods + 1
    )

    outputs.write(format, details, budget_items, expenses)


@click.group()
def rent():
    """Subset of calculations available for renting housing"""


@rent.command(name='simple')
@click.argument('purchaser')
@click.argument('rent', type=click.INT)
@click.option('--time', '-t', type=click.INT, default=5, help='Number of years to run calculation')
@click.option('--output', '-o', default='SimpleRental', help='Output files base name')
@click.option('--format', type=click.Choice(outputs.FORMATS), default=outputs.DEFAULT_FORMAT)
def rent_simple(purchaser, rent, time, output, format):  # pylint: disable=redefined-builtin,redefined-outer-name
    """
    Simple rental calculation with a fixed monthly housing budget.
    """
    purchaser_profile = get_purchaser_profile(purchaser)

    periods = time * const.PERIODS_PER_YEAR
    details = HousingDetail(
        name=output,
        price=rent,
        type=HousingType.rental
    )

    budget_items = [
        Rent(rent),
        Investment(purchaser_profile.cash),
    ]

    budget = MonthlyBudget(purchaser_profile.budget)

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
cli.add_command(profiles)


def main():
    cli()


if __name__ == "__main__":
    main()
