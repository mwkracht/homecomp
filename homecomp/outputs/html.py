import os
from typing import List

from jinja2 import Template

from homecomp.models import BudgetItem
from homecomp.models import HousingDetail
from homecomp.models import MonthlyExpense
from homecomp.outputs import common


TEMPLATE = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- bootstrap css only -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta2/dist/css/bootstrap.min.css"
          integrity="sha384-BmbxuPwQa2lc/FVzBcNJ7UAyJxM6wuqIj61tLrc4wSX0szH/Ev+nYRRuWlolflfl"
          rel="stylesheet"
          crossorigin="anonymous">

    <title>{{ details.name }}</title>
</head>
<body>
<main class="container">
    <div class="text-center py-5 px-3">
        <div class="text-center py-5">
            <h2>{{ details.name }}</h2>
            <h5>Cost: <span class="text-danger">{{ average_cost }}/mo<span></h5>
            <h5>Gains: <span class="text-success">{{ asset_delta }}<span></h5>
            <h5>Time: {{ asset_rows[:-1] | length }} months<span></h5>
        </div>
        <div class="container">
            <div class="row">
                <div class="col">
                    <a href="{{ details.link }}"><img src="{{ details.image }}" alt="Home Image"></a>
                </div>
                <div class="col">
                    <ul class="list-group-flush">
                        <li class="list-group-item">List price: {{ "${:,.2f}".format(details.price) }}</li>
                        <li class="list-group-item">Bedrooms: {{ details.bedrooms if details.bedrooms else 'Unknown' }}</li>
                        <li class="list-group-item">Bathrooms: {{ details.bathrooms if details.bathrooms else 'Unknown' }}</li>
                        <li class="list-group-item">Home size (sqft): {{ details.home_size if details.home_size else 'Unknown' }}</li>
                        <li class="list-group-item">Lot size (sqft): {{ details.lot_size if details.lot_size else 'Unknown' }}</li>
                        {% if details.hoa %}
                        <li class="list-group-item">HOA: {{ "${:,.2f}".format(details.hoa) }}</li>
                        {% endif %}
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <div class="text-center py-3 px-3">
        <h3 class="py-2">Assets</h3>
        <table class="table table-striped table-bordered">
            <thead class="thead-light">
                <tr>
                {% for header in asset_headers %}
                    <th scope="col">{{ header }}</th>
                {% endfor %}
                </tr>
            </thead>
            <tbody>
            {% for row in asset_rows %}
                <tr>
                {% for header in asset_headers %}
                    {% if loop.index0 == 0 %}
                        <th scope="row" style="white-space:nowrap">{{ row[header] }}</th>
                    {% else %}
                        <td style="white-space:nowrap">{{ row[header] }}</td>
                    {% endif %}
                {% endfor %}
                </tr>
            {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="text-center py-3 px-3 table-responsive">
        <h3 class="py-2">Expenses</h3>
        <table class="table table-striped table-bordered">
            <thead class="thead-light">
                {% for header_row in expense_header_spans %}
                    <tr>
                    {% for header, span in header_row %}
                        <th colspan="{{span}}" scope="col">{{ header }}</th>
                    {% endfor %}
                    </tr>
                {% endfor %}
            </thead>
            <tbody>
            {% for row in expense_rows %}
                <tr>
                {% for header in expense_headers %}
                    {% if loop.index0 == 0 %}
                        <th scope="row" style="white-space:nowrap">{{ row[header] }}</th>
                    {% else %}
                        <td style="white-space:nowrap">{{ row[header] }}</td>
                    {% endif %}
                {% endfor %}
                </tr>
            {% endfor %}
            </tbody>
        </table>
    </div>
</main>
</body>
</html>
""")


def write_html(details: HousingDetail,
               budget_items: List[BudgetItem],
               expenses: List[MonthlyExpense],
               directory: str):
    """Write all computation results to html output file"""
    output_file = os.path.join(directory, f'{details.name}.html')
    asset_headers, asset_rows = common.get_asset_table(budget_items, len(expenses) - 1)
    expense_headers, expense_rows = common.get_expense_table(expenses)

    with open(output_file, 'w') as output_fd:
        output_fd.write(TEMPLATE.render(
            details=details,
            asset_headers=asset_headers,
            asset_rows=asset_rows,
            expense_header_spans=common.get_header_spans(expense_headers),
            expense_headers=expense_headers,
            expense_rows=expense_rows,
            asset_delta=common.get_asset_delta(budget_items),
            average_cost=common.get_average_cost(expenses),
        ))
