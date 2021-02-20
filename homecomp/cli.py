# pylint: disable=too-many-arguments,redefined-outer-name,function-redefined
import csv
from datetime import date

import click
from dateutil.relativedelta import relativedelta

from homecomp import clients
from homecomp import const
from homecomp.base import MonthlyBudget
from homecomp.base import NetworthMixin
from homecomp.budget_items.assets import Investment
from homecomp.budget_items.composite import HomeLifetime
from homecomp.budget_items.liabilities import VariablePaymentMortgage
from homecomp.budget_items.misc import Rent
from homecomp.compute import compute


def format_value(value):
    return "{:.2f}".format(value)


def iter_months(start=None):
    start = start or date.today()

    while True:
        yield start.strftime('%b, %Y')
        start += relativedelta(months=1)


def write_expenses_csv(output, expenses):  # pylint: disable=unused-argument
    with open(f'{output}.expenses.csv', mode='w') as output_fd:  # pylint: disable=unused-variable
        pass


def write_assets_csv(output, budget_items, periods):
    with open(f'{output}.assets.csv', mode='w') as output_fd:
        networth_items = {
            budget_item.name: budget_item
            for budget_item in budget_items
            if isinstance(budget_item, NetworthMixin)
        }

        months = iter_months()
        writer = csv.DictWriter(
            output_fd,
            fieldnames=['Time'] + list(networth_items.keys()) + ['total']
        )
        writer.writeheader()

        for period in range(const.INIT_PERIOD, periods + 1):
            row = {'Time': next(months)}
            row.update({
                key: format_value(networth_item.get_period_value(period))
                for key, networth_item in networth_items.items()
            })
            row['total'] = format_value(sum(
                networth_item.get_period_value(period)
                for networth_item in networth_items.values()
            ))

            writer.writerow(row)


@click.group()
def buy():
    """Subset of calculations available for buying housing"""


@buy.command()
@click.argument('cash', type=click.INT)
@click.argument('budget', type=click.INT)
@click.argument('price', type=click.INT)
@click.option('--hoa', '-h', type=click.INT, default=0, help='Monthly HOA fee')
@click.option('--time', '-t', type=click.INT, default=5, help='Number of years to run calculation')
@click.option('--output', '-o', default='buy_simple', help='Output csv file')
def simple(cash, budget, price, hoa, time, output):
    """
    Simple buy calculation with a fixed monthly housing budget.

    Home will be sold during the last period of the calculation.
    """
    periods = time * const.PERIODS_PER_YEAR

    budget_items = [
        HomeLifetime(
            name='SimpleHome',
            lifetime=list(range(periods)),
            price=price,
            hoa_fee=hoa
        ),
        VariablePaymentMortgage(
            price=price,
            start=0,
        ),
        Investment(cash),
    ]

    budget = MonthlyBudget(budget)

    expenses = compute(
        budget,
        budget_items,
        periods=periods
    )

    write_expenses_csv(output, expenses)
    write_assets_csv(output, budget_items, periods)


@buy.command()
@click.argument('cash', type=click.INT)
@click.argument('budget', type=click.INT)
@click.argument('link')
@click.option('--time', '-t', type=click.INT, default=5, help='Number of years to run calculations')
def zillow(cash, budget, link, time):
    """Perform computation using Zillow shareable property link"""
    periods = time * const.PERIODS_PER_YEAR
    details = clients.zillow.get_home_details(link)

    budget_items = [
        HomeLifetime(
            name=f'{details.name}',
            lifetime=list(range(periods)),
            price=details.price,
            hoa_fee=details.hoa,
            property_tax_rate=details.property_tax_rate
        ),
        VariablePaymentMortgage(
            price=details.price,
            start=0,
        ),
        Investment(cash),
    ]

    budget = MonthlyBudget(budget)

    expenses = compute(
        budget,
        budget_items,
        periods=periods
    )

    write_expenses_csv(details.name, expenses)
    write_assets_csv(details.name, budget_items, periods)


@click.group()
def rent():
    """Subset of calculations available for renting housing"""


@rent.command()
@click.argument('cash', type=click.INT)
@click.argument('budget', type=click.INT)
@click.argument('rent', type=click.INT)
@click.option('--time', '-t', type=click.INT, default=5, help='Number of years to run calculation')
@click.option('--output', '-o', default='rent_simple', help='Output files base name')
def simple(cash, budget, rent, time, output):
    """
    Simple rental calculation with a fixed monthly housing budget.
    """
    periods = time * const.PERIODS_PER_YEAR

    budget_items = [
        Rent(rent),
        Investment(cash),
    ]

    budget = MonthlyBudget(budget)

    expenses = compute(
        budget,
        budget_items,
        periods=periods
    )

    write_expenses_csv(output, expenses)
    write_assets_csv(output, budget_items, periods)


@click.group()
def cli():
    pass


cli.add_command(buy)
cli.add_command(rent)


def main():
    cli()


if __name__ == "__main__":
    main()
