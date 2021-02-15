# Avoid 'no handlers could be found for logger' warnings if logging not configured for application
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())


__version__ = '0.0.1'
__author__ = 'Matt Kracht'
__email__ = 'mwkracht@gmail.com'
__license__ = 'MIT'
