import json

import bs4
import requests

from homecomp import const
from homecomp import errors
from homecomp.models import HousingDetail


HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}


def get_home_details(shareable_link: str) -> HousingDetail:
    """
    Return all home details which can be used for computation values.

    Shareable link can be generated from a listing page.
    """
    resp = requests.get(shareable_link, headers=HEADERS)
    resp.raise_for_status()

    soup = bs4.BeautifulSoup(resp.text, 'html.parser')
    if soup.find('h5', text="Please verify you're a human to continue."):
        raise errors.CaptchaError('You have been had!')

    name = soup.find('title').get_text(strip=True).split('|')[0].strip()

    # price = next(soup.find('div', {'class': 'ds-summary-row'}).children).get_text(strip=True)
    # price = int(price.strip('$').replace(',', ''))

    # hoa = soup.find('span', text='HOA:').next_sibling.get_text(strip=True)
    # hoa = int(hoa.strip('$').replace(',', '').strip(' monthly'))

    # instead of searching across HTML fields pull this giant json scipt field and
    # wrangle details form that - hopefully this doesn't change :)
    data = json.loads(next(soup.find(id='hdpApolloPreloadedData').children))
    cache = json.loads(data['apiCache'])
    full_data_key = next(key for key in cache if 'FullRenderQuery' in key)
    home = cache[full_data_key]['property']

    return HousingDetail(
        name=name,
        type=const.HOUSING_TYPE_HOME,
        link=shareable_link,
        image=home['mediumImageLink'],
        price=home['price'],
        hoa=home['monthlyHoaFee'],
        property_tax_rate=home['propertyTaxRate'] / 100,
        bedrooms=home['bedrooms'],
        bathrooms=home['bathrooms'],
        home_size=home['livingArea'],
        lot_size=home['lotSize'],
    )
