# pylint: disable=too-many-arguments,redefined-outer-name,redefined-builtin
import os
from itertools import product

import click

from homecomp import clients
from homecomp import const
from homecomp import errors
from homecomp import outputs
from homecomp.models import PurchaserProfile
from homecomp.models import HousingDetail
from homecomp.models import MonthlyBudget
from homecomp.outputs.html import write_multi_year
from homecomp.outputs.common import get_asset_delta
from homecomp.outputs.common import get_average_cost
from homecomp import compute
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
@click.option('--max-mortgage/--min-mortgage', default=False)
@click.option('--yearly-appreciation', type=click.FLOAT, default=const.DEFAULT_HOME_APPRECIATION)
def profiles_add(name, cash, budget, max_mortgage, yearly_appreciation):
    with DataclassFileStorage() as storage:
        profile = PurchaserProfile(
            name=name,
            cash=cash,
            budget=budget,
            mortgage_type='max' if max_mortgage else 'min',
            home_appreciation=yearly_appreciation,
        )

        storage.profiles.save(profile, overwrite=False)


@profiles.command(name='update')
@click.argument('name')
@click.argument('cash', type=click.INT)
@click.argument('budget', type=click.INT)
@click.option('--max-mortgage/--min-mortgage', default=False)
@click.option('--yearly-appreciation', type=click.FLOAT, default=const.DEFAULT_HOME_APPRECIATION)
def profiles_update(name, cash, budget, max_mortgage, yearly_appreciation):
    with DataclassFileStorage() as storage:
        profile = PurchaserProfile(
            name=name,
            cash=cash,
            budget=budget,
            mortgage_type='max' if max_mortgage else 'min',
            home_appreciation=yearly_appreciation,
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
            _profile = storage.profiles.find(name)
            storage.profiles.delete(_profile.name)
    except errors.NoEntryFound:
        click.echo(f'No profile found for {name}')


@click.group()
def housing():
    """Commands for manipulating housing details"""


@housing.command(name='add')
@click.option('--link', '-l', help='Shareable link to housing')
@click.option('--name', '-n')
@click.option('--price', '-p', type=click.INT, help='Monthly rent or list price')
@click.option(
    '--type', '-t',
    type=click.Choice(const.HOUSING_TYPES),
    default=const.HOUSING_TYPE_HOME
)
def housing_add(link, name, price, type):
    if link:
        _housing = clients.get_home_details(link)
    elif name and price and type:
        _housing = HousingDetail(
            name=name,
            price=price,
            type=type
        )
    else:
        raise click.UsageError('Must provide link or name, price, type inputs')

    with DataclassFileStorage() as storage:
        storage.housing.save(_housing, overwrite=False)


@housing.command(name='update')
@click.argument('name')
def housing_refresh(name):
    """Reload most recent housing details from link"""
    try:
        with DataclassFileStorage() as storage:
            _housing = storage.housing.find(name)

            # remove old housing option in case name has changed
            storage.housing.delete(_housing.name)

            if _housing.link:
                _housing = clients.get_home_details(_housing.link)
            else:
                raise click.ClickException('Can only refresh housing with link')

            storage.housing.save(_housing)

    except errors.NoEntryFound:
        click.echo(f'No housing found for {name}')


@housing.command(name='list')
@click.argument('name', nargs=-1)
def housing_list(name):
    with DataclassFileStorage() as storage:
        _housings = storage.housing.find_all(name[0]) if name else storage.housing

        for idx, _housing in enumerate(_housings):
            price = outputs.format_currency(_housing.price)
            click.echo(f'{idx}\t{_housing.type}\t{price}\t{_housing.name}')


@housing.command(name='remove')
@click.argument('name')
def housing_remove(name):
    try:
        with DataclassFileStorage() as storage:
            _housing = storage.housing.find(name)
            storage.housing.delete(_housing.name)
    except errors.NoEntryFound:
        click.echo(f'No housing found for {name}')


def _run(purchaser, housing, time, output, format):
    purchaser = get_purchaser_profile(purchaser) if isinstance(purchaser, str) else purchaser
    details = get_housing_detail(housing) if isinstance(housing, str) else housing

    method = compute.buy if details.type == const.HOUSING_TYPE_HOME else compute.rent
    expenses, budget_items = method(
        purchaser=purchaser,
        housing=details,
        years=time
    )

    output_dir = os.path.join(output, purchaser.name)
    outputs.write(format, details, budget_items, expenses, output_dir)


@click.command()
@click.argument('purchaser')
@click.argument('housing')
@click.option('--time', '-t', type=click.INT, default=5, help='Number of years to run calculation')
@click.option('--output', '-o', default=os.getenv('HOUSING_DIR', '.'), help='Output directory')
@click.option('--format', type=click.Choice(outputs.FORMATS), default=outputs.DEFAULT_FORMAT)
def run(purchaser, housing, time, output, format):
    """Run a single housing computation for the given profile"""
    _run(purchaser, housing, time, output, format)


@click.command()
@click.option('--time', '-t', type=click.INT, default=5, help='Number of years to run calculation')
@click.option('--output', '-o', default=os.getenv('HOUSING_DIR', '.'), help='Output directory')
@click.option('--format', type=click.Choice(outputs.FORMATS), default=outputs.DEFAULT_FORMAT)
def run_all(time, output, format):
    """Run all buy/rent calculations crossing each housing option with each profile"""
    with DataclassFileStorage() as storage:
        for purchaser, details in product(storage.profiles, storage.housing):
            _run(purchaser, details, time, output, format)


@click.command()
@click.argument('purchaser')
@click.argument('limit', type=click.INT)
@click.option('--output', '-o', default=os.getenv('HOUSING_DIR', '.'), help='Output directory')
def multi_year(purchaser, limit, output):
    """
    Run all buy/rent calculations over different time ranges with simplified output.

    Calculations will be run from 1 to limit number of years.
    """
    purchaser = get_purchaser_profile(purchaser)

    with DataclassFileStorage() as storage:
        rows = []

        for time in range(1, limit + 1):
            row = []

            for details in storage.housing:
                method = compute.buy if details.type == const.HOUSING_TYPE_HOME else compute.rent
                expenses, budget_items = method(
                    purchaser=purchaser,
                    housing=details,
                    years=time
                )

                row.extend([
                    get_average_cost(expenses),
                    get_asset_delta(budget_items),
                ])

            rows.append(row)

        write_multi_year(
            storage.housing,
            rows,
            purchaser=purchaser,
            directory=output
        )


@click.group()
def cli():
    pass


cli.add_command(profiles)
cli.add_command(housing)
cli.add_command(run)
cli.add_command(run_all)
cli.add_command(multi_year)


def main():
    cli()


if __name__ == "__main__":
    main()
