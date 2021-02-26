# pylint: disable=too-many-arguments,redefined-outer-name,redefined-builtin
import os

import click

from homecomp import clients
from homecomp import const
from homecomp import errors
from homecomp import outputs
from homecomp.models import PurchaserProfile
from homecomp.models import HousingDetail
from homecomp.models import MonthlyBudget
from homecomp.budget_items.assets import Investment
from homecomp.budget_items.composite import HomeLifetime
from homecomp.budget_items.liabilities import MaxMortgage
from homecomp.budget_items.liabilities import MinMortgage
from homecomp.budget_items.misc import Rent
from homecomp.compute import compute
from homecomp.storage import DataclassFileStorage


def get_purchaser_profile(name: str) -> PurchaserProfile:
    try:
        with DataclassFileStorage() as storage:
            return storage.profiles.find(name)
    except errors.NoEntryFound as error:
        raise click.ClickException(f'No profile found for {name}') from error


def get_housing_detail(name: str) -> HousingDetail:
    try:
        with DataclassFileStorage() as storage:
            return storage.housing.find(name)
    except errors.NoEntryFound as error:
        raise click.ClickException(f'No housing found for {name}') from error



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
def housing():
    """Commands for manipulating housing details"""


@housing.command(name='add')
@click.option('--link', '-l', help='Shareable link to housing')
def housing_add(link):
    if link:
        _housing = clients.get_home_details(link)
    else:
        raise click.UsageError('Must provide link or name, price, type inputs')

    with DataclassFileStorage() as storage:
        storage.housing.save(_housing, overwrite=False)


@housing.command(name='update')
@click.argument('name')
def housing_update(name):
    try:
        with DataclassFileStorage() as storage:
            _housing = storage.housing.find(name)

            # remove old housing option in case name has changed
            storage.housing.delete(_housing.name)

            if _housing.link:
                _housing = clients.get_home_details(_housing.link)
            else:
                raise click.ClickException('Can only update housing with link')

            storage.housing.save(_housing)

    except errors.NoEntryFound:
        click.echo(f'No housing found for {name}')


@housing.command(name='list')
@click.argument('name', nargs=-1)
def housing_list(name):
    with DataclassFileStorage() as storage:
        _housings = storage.housing.find_all(name[0]) if name else storage.housing

        for _housing in _housings:
            click.echo(_housing)


@housing.command(name='remove')
@click.argument('name')
def housing_remove(name):
    try:
        with DataclassFileStorage() as storage:
            storage.housing.delete(name)
    except errors.NoEntryFound:
        click.echo(f'No housing found for {name}')


@click.command()
@click.argument('purchaser')
@click.argument('housing')
@click.option('--time', '-t', type=click.INT, default=5, help='Number of years to run calculation')
@click.option('--output', '-o', default=os.getenv('HOUSING_DIR', '.'), help='Output directory')
@click.option('--format', type=click.Choice(outputs.FORMATS), default=outputs.DEFAULT_FORMAT)
@click.option('--max-mortgage/--min-mortgage', default=False)
def buy(purchaser, housing, time, output, format, max_mortgage):
    """
    Simple buy calculation with a fixed monthly housing budget.

    Home will be sold during the last period of the calculation.
    """
    periods = time * const.PERIODS_PER_YEAR
    purchaser_profile = get_purchaser_profile(purchaser)
    details = get_housing_detail(housing)

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

    outputs.write(format, details, budget_items, expenses, output)


@click.command()
@click.argument('purchaser')
@click.argument('housing')
@click.option('--time', '-t', type=click.INT, default=5, help='Number of years to run calculation')
@click.option('--output', '-o', default=os.getenv('HOUSING_DIR', '.'), help='Output directory')
@click.option('--format', type=click.Choice(outputs.FORMATS), default=outputs.DEFAULT_FORMAT)
def rent(purchaser, housing, time, output, format):  # pylint: disable=redefined-builtin,redefined-outer-name
    """
    Simple rental calculation with a fixed monthly housing budget.
    """
    periods = time * const.PERIODS_PER_YEAR
    purchaser_profile = get_purchaser_profile(purchaser)
    details = get_housing_detail(housing)

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

    outputs.write(format, details, budget_items, expenses, output)


@click.group()
def cli():
    pass


cli.add_command(profiles)
cli.add_command(housing)
cli.add_command(buy)
cli.add_command(rent)


def main():
    cli()


if __name__ == "__main__":
    main()
