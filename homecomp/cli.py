# pylint: disable=too-many-arguments,redefined-outer-name,function-redefined
from collections import OrderedDict
import csv
from datetime import date

import click
from dateutil.relativedelta import relativedelta

from homecomp import const
from homecomp.base import MonthlyBudget
from homecomp.base import NetworthBudgetItem
from homecomp.budget_items.assets import Home
from homecomp.budget_items.assets import Investment
from homecomp.budget_items.liabilities import VariablePaymentMortgage
from homecomp.budget_items.misc import HomeBuyingCosts
from homecomp.budget_items.misc import HomeInsurance
from homecomp.budget_items.misc import HomeSellingCosts
from homecomp.budget_items.misc import Maintenance
from homecomp.budget_items.misc import PropertyTax
from homecomp.budget_items.misc import Rent
from homecomp.simulator import run


def format_value(value):
    return "{:.2f}".format(value)


def iter_months(start=None):
    start = start or date.today()

    while True:
        yield start.strftime('%b, %Y')
        start += relativedelta(months=1)


def write_networth_csv(output, budget_items, periods):
    with open(output, mode='w') as output_fd:
        networth_items = {
            key: value
            for key, value in budget_items.items()
            if isinstance(value, NetworthBudgetItem)
        }

        months = iter_months()
        writer = csv.DictWriter(
            output_fd,
            fieldnames=['Time'] + list(networth_items.keys()) + ['total']
        )
        writer.writeheader()

        for period in range(periods + 1):
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
    """Subset of simulations available for buying housing"""


@buy.command()
@click.argument('cash', type=click.INT)
@click.argument('budget', type=click.INT)
@click.argument('list_price', type=click.INT)
@click.option('--premium', '-p', type=click.INT, default=1200, help='Home insurance annual premium')
@click.option('--time', '-t', type=click.INT, default=5, help='Number of years to run simulation')
@click.option('--output', '-o', default='buy_simple.csv', help='Output csv file')
def simple(cash, budget, list_price, premium, time, output):
    """
    Simple buy simulation with a fixed monthly housing budget.

    Home will be sold during the last period of the simulation.
    """
    down_payment = list_price * const.DEFAULT_DOWN_PAYMENT_PCT
    periods = time * const.PERIODS_PER_YEAR

    cash -= down_payment
    if cash < 0:
        raise click.UsageError('Required down payment is larger than available cash')

    home = Home(list_price)

    budget_items = OrderedDict({
        'home': home,
        'buying_costs': HomeBuyingCosts(home=home),
        'selling_costs': HomeSellingCosts(home=home, sell_period=periods-1),
        'maintenance': Maintenance(home=home),
        'property_tax': PropertyTax(home=home),
        'insurance': HomeInsurance(premium=premium),
        'mortgage': VariablePaymentMortgage(
            principal=list_price - down_payment,
        ),
        'cash': Investment(cash),
    })

    budget = MonthlyBudget(budget)

    run(
        budget,
        budget_items,
        periods=periods
    )

    write_networth_csv(output, budget_items, periods)


@click.group()
def rent():
    """Subset of simulations available for renting housing"""


@rent.command()
@click.argument('cash', type=click.INT)
@click.argument('budget', type=click.INT)
@click.argument('rent', type=click.INT)
@click.option('--time', '-t', type=click.INT, default=5, help='Number of years to run simulation')
@click.option('--output', '-o', default='rent_simple.csv', help='Output csv file')
def simple(cash, budget, rent, time, output):
    """
    Simple rental simulation with a fixed monthly housing budget.
    """
    periods = time * const.PERIODS_PER_YEAR

    budget_items = OrderedDict({
        'rent': Rent(rent),
        'cash': Investment(cash),
    })

    budget = MonthlyBudget(budget)

    run(
        budget,
        budget_items,
        periods=periods
    )

    write_networth_csv(output, budget_items, periods)


@click.group()
def cli():
    pass


cli.add_command(buy)
cli.add_command(rent)


def main():
    cli()


if __name__ == "__main__":
    main()
