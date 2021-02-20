import json

import bs4
import requests

from homecomp.clients.base import HomeDetails


HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, sdch, br',
    'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/74.0.3729.131 Safari/537.36'
}


def get_home_details(shareable_link: str) -> HomeDetails:
    """
    Return all home details which can be used for computation values.

    Shareable link can be generated from a listing page.
    """
    resp = requests.get(shareable_link, headers=HEADERS)
    resp.raise_for_status()

    soup = bs4.BeautifulSoup(resp.text, 'html.parser')

    name = soup.find('title').get_text(strip=True)

    # price = next(soup.find('div', {'class': 'ds-summary-row'}).children).get_text(strip=True)
    # price = int(price.strip('$').replace(',', ''))

    # hoa = soup.find('span', text='HOA:').next_sibling.get_text(strip=True)
    # hoa = int(hoa.strip('$').replace(',', '').strip(' monthly'))

    # instead of searching across HTML fields pull this giant json scipt field and
    # wrangle details form that - hopefully this doesn't change :)
    data = json.loads(next(soup.find(id='hdpApolloPreloadedData').children))
    cache = json.loads(data['apiCache'])
    full_data_key = next(key for key in cache if 'FullRenderQuery' in key)
    full_data = cache[full_data_key]

    return HomeDetails(
        name=name,
        link=shareable_link,
        price=full_data['property']['price'],
        hoa=full_data['property']['monthlyHoaFee'],
        property_tax_rate=full_data['property']['propertyTaxRate'] / 100
    )
