import bs4
import requests

from homecomp import const
from homecomp.models import HousingDetail


HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}


def currency_to_int(value):
    """Convert currency string to integer"""
    return int(value.strip('$').strip('/mo.').replace(',', ''))


def parse_details_li(items, key, default=None):
    return next((
        currency_to_int(item.get_text(strip=True).strip(key))
        for item in items
        if key in item.text
    ), default)


def get_home_details(shareable_link: str) -> HousingDetail:
    """
    Return all home details which can be used for computation values.

    Shareable link can be generated from a listing page.
    """
    resp = requests.get(shareable_link, headers=HEADERS)
    resp.raise_for_status()

    soup = bs4.BeautifulSoup(resp.text, 'html.parser')
    name = soup.find('title').get_text(strip=True).split('|')[0].strip()

    carousel = soup.find('div', {'class': 'carousel-scroller-wrapper'})
    image = carousel.find('img')
    image = image['src'] if image else None

    price = soup.find('h2', {'class': 'price-block-sale-price'}).get_text(strip=True)
    price = currency_to_int(price)

    hoa = soup.find('small', text='HOA')
    if hoa:
        hoa = hoa.find_next_sibling('div').get_text(strip=True)
        hoa = currency_to_int(hoa)
    else:
        hoa = 0

    hoa_amenities = soup.find('dt', {'class': 'home-attributes-list-label'}, text='HOA/Condo/Coop Fee:')
    if hoa_amenities:
        hoa_amenities = hoa_amenities.find_next_sibling('dd').get_text(strip=True).split(', ')

    tax = soup.find('dt', {'class': 'home-attributes-list-label'}, text='Tax Annual Amount:')
    if hoa_amenities and 'Taxes' in hoa_amenities:
        effective_tax_rate = 0
    elif tax:
        tax = currency_to_int(tax.find_next_sibling('dd').get_text(strip=True))
        effective_tax_rate = tax / price
    else:
        effective_tax_rate = const.DEFAULT_PROPERTY_TAX_PCT

    details_li = soup.find('ul', {'class': 'listing-basic-details'}).find_all('li')

    return HousingDetail(
        name=name,
        type=const.HOUSING_TYPE_HOME,
        link=shareable_link,
        image=image,
        price=price,
        hoa=hoa,
        property_tax_rate=effective_tax_rate,
        bedrooms=parse_details_li(details_li, 'beds'),
        bathrooms=parse_details_li(details_li, 'baths'),
        home_size=parse_details_li(details_li, 'sqft'),
        lot_size=parse_details_li(details_li, 'sqft lot'),
    )
