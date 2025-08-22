import urllib
from typing import Optional
import urllib.parse
import logging
from colorlog import ColoredFormatter

####
##      CONSTANTS
#####
DEFAULT_API_HOST = 'https://api-checkout.cinetpay.com'
API_ENDPOINTS = {
    'check': '/v2/payment/check',
    'initialize':'/v2/payment',
    'list': '/v2/payment',
    'retrieve':'/v2/payment',
}

####
##      LOGGER
#####
class Logger:
    ''' Logger. '''
    
    def __init__(
        self, name, level = logging.INFO, 
        format = '%(log_color)s[%(levelname)s] %(asctime)s : %(name)s - %(message)s'
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        formatter = ColoredFormatter(
            format,
            datefmt = '%Y-%m-%d %H:%M:%S',
            log_colors = {
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'bold_red,bg_white',
            },
            reset = True,
            style = '%'
        )

        # ADD A CONSOLE HANDLER
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

####
##      URL PARSER
#####
class UrlUtils:
    ''' Url Parser class. '''
    
    def get_scheme_port(self,scheme) -> int:
        ''' Return a post based on given scheme. '''
        
        return {
            'http': 80,
            'https': 443
        }.get(scheme,443)
    
    def parse_host(self,host: Optional[str]) -> str:
        """
        >>> _parse_host(None)
        'http://127.0.0.1:9000'
        >>> _parse_host('')
        'http://127.0.0.1:11434'
        >>> _parse_host('1.2.3.4')
        'http://1.2.3.4:11434'
        >>> _parse_host(':56789')
        'http://127.0.0.1:56789'
        >>> _parse_host('1.2.3.4:56789')
        'http://1.2.3.4:56789'
        >>> _parse_host('http://1.2.3.4')
        'http://1.2.3.4:80'
        >>> _parse_host('https://1.2.3.4')
        'https://1.2.3.4:443'
        >>> _parse_host('https://1.2.3.4:56789')
        'https://1.2.3.4:56789'
        >>> _parse_host('example.com')
        'http://example.com:11434'
        >>> _parse_host('example.com:56789')
        'http://example.com:56789'
        >>> _parse_host('http://example.com')
        'http://example.com:80'
        >>> _parse_host('https://example.com')
        'https://example.com:443'
        >>> _parse_host('https://example.com:56789')
        'https://example.com:56789'
        >>> _parse_host('example.com/')
        'http://example.com:11434'
        >>> _parse_host('example.com:56789/')
        'http://example.com:56789'
        """

        host = host or ''
        scheme, _, hostport = host.partition('://')
        if not hostport:
            scheme, hostport = 'http', host
        
        port = self.get_scheme_port(scheme)

        split = urllib.parse.urlsplit('://'.join([scheme, hostport]))
        host = split.hostname or '127.0.0.1'
        port = split.port or port
        
        return f'{scheme}://{host}:{port}'