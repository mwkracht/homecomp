from urllib.parse import urlparse

from homecomp import errors
from homecomp.clients import estately
from homecomp.clients import zillow
from homecomp.models import HousingDetail


_URL_MAPPING = {
    'www.estately.com': estately.get_home_details,
    'www.zillow.com': zillow.get_home_details,
}


def get_home_details(shareable_link: str) -> HousingDetail:
    """
    Return normalized housing detail from provided link.

    The link must come from a supported site otherwise error
    will raised.
    """
    parsed = urlparse(shareable_link)

    try:
        return _URL_MAPPING[parsed.netloc](shareable_link)
    except KeyError as error:
        raise errors.ClientNotSupported(f'No client implementation for {parsed.netloc}') from error
