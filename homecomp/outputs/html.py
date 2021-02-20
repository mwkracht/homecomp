from typing import List

from jinja2 import Template

from homecomp.models import BudgetItem
from homecomp.models import HousingDetails
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
        <h2 class="text-center py-5">{{ details.name }}</h2>
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
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <div class="text-center py-3 px-3">
        <h3 class="py-1">Assets over Lifetime</h3>
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
                        <th scope="row">{{ row[header] }}</th>
                    {% else %}
                        <td>{{ row[header] }}</td>
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


def write_html(details: HousingDetails,
               budget_items: List[BudgetItem],
               expenses: List[MonthlyExpense]):
    """Write all computation results to html output file"""
    asset_headers, asset_rows = common.get_asset_table(budget_items, len(expenses))

    with open(f'{details.name}.html', 'w') as output_fd:
        output_fd.write(TEMPLATE.render(
            details=details,
            asset_headers=asset_headers,
            asset_rows=asset_rows,
        ))
