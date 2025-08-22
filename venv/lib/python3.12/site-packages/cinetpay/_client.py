import httpx
import platform
import simplejson as Json
from importlib import metadata

try:
    __version__ = metadata.version('cinetpay')
except metadata.PackageNotFoundError:
    __version__ = '0.0.0'
    
from cinetpay._utils import (
    UrlUtils, Logger, DEFAULT_API_HOST,
    API_ENDPOINTS
)
from cinetpay._services import get_service
from cinetpay._types import (
    Config, Order, Response,
    PagginatedResponse, ResponseError,
    ErrorResponse
)
    
## VARIABLES
USER_AGENT = (
    f'CinetPay-python/{__version__} ({platform.machine()}'
    f'{platform.system().lower()}) Python/{platform.python_version()}'
    )

  
####
##      BASE CLIENT
#####
class BaseClient:
    """
        Creates a httpx client. Default parameters are the same as those defined in httpx
        except for the following:
        - `follow_redirects`: True
        - `timeout`: None
        - `configs`: AuthConfig
        `kwargs` are passed to the httpx client.
    """
    
    def __init__(
        self,
        configs : Config,
        **kwargs,
    ) -> None:
        
        # INITIALIZE CONFIGS
        self.config = Config(**configs)
        self.token = None
        self._client = self.get_client(**kwargs)
        self.logger = Logger('Client')
        
        # CHECK CONFIGS
        self.check_config()
        
    def check_config(self):
        ''' Validate config. '''
        
        from cinetpay._schema import (
            Channels, Languages, Currencies
        )
        
        # REQUIRED FIELDS
        required_fields = [
            'credentials','currency','language',
            'channels','lock_phone_number',
            'raise_on_error'
        ]
        
        # ENSURE REQUIRED FIELDS ARE SET.
        for field in required_fields:
            if not field in self.config.keys():
                raise AttributeError(
                    f'Improperly Configured: Config is missing '
                    f'required field: {field}'
                )
                
        # VALIDATE ALL REQUIRED SCHEMAS
        checks = [
            Channels.validate(self.config['channels']),
            Languages.validate(self.config['language']),
            Currencies.validate(self.config['currency'])
        ]
        for check in checks:
            if not check[0]:
                raise AttributeError(check[1])
        
    def set_token(self,token):
        ''' Update token. '''
        
        self.token = token
    
    def get_client(self,auth = False,**kwargs):
        ''' Return a new httpx client. '''
        # CREATE CLIENT NOW
        return httpx.Client(
            base_url = self.get_url(),
            headers = self._get_headers(
                authorization = auth
            ),
            **kwargs,
        )
        
    def get_url(self):
        ''' Return a base Url to use foe requests. '''
        return UrlUtils().parse_host(
            self.config.get('host') or DEFAULT_API_HOST
        )
    
    def _get_headers(self,authorization=False):
        ''' Return request Headers. '''

        # FILL REQUEST HEADERS
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': USER_AGENT
        }
        if authorization:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers
    
    def _get_response_context(self):
        ''' Return serponse context dic. '''
        return {
            'client': self,
            'base_url': DEFAULT_API_HOST
        }
    
    def _request(
        self, method: str, auth: bool, 
        end_point: str = '', detail = False, **kwargs
    ) -> httpx.Response:
        ''' Send request and return an Httpx Response. '''
        
        # SEND REQUEST TO PROVIDER.
        with self.get_client(auth) as req:
            response = req.request(
                method, self.get_url() + end_point, **kwargs
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                self.logger.error(f'{e}')

            return self.process_response(
                response, detail = detail
            )
    
    def process_response(self,response ,detail = False):
        ''' Return appropriate response based on response. '''
        
        # GET CONTEXT
        context = self._get_response_context()
        
        # CHECK FOR SUCCESS
        if response.status_code in (200,201):
            
            return PagginatedResponse(
                response,context
            )if not detail else Response(
                response,context
            )
        
        # THEN RAISE RESPONSE ERROR IF NEEDED
        if self.config['raise_on_error']:
            raise ResponseError(
                response.text,response.status_code
            ) from None
        # RETURN ERROR RESPONSE ELSE
        else:
            return ErrorResponse(
                response, context
            )
        
####
##      CLIENT
#####
class Client(BaseClient):
    ''' CinetPay client 😎. '''
    
    def list_transactions(self):
        ''' Return App Transactions. '''
        
        self.logger.warning(
            'This method is not recommandes for now.'
        )
        
        # SEND REQUEST TO API
        return self._request(
            "GET", auth = False, 
            end_point = API_ENDPOINTS['list'],
        )
      
    def initialize_transaction(self,transaction:Order):
        ''' Initialize a new payment transaction. '''
        
        # GET VALIDATOR SERVICE FIRST
        service = get_service(
            transaction.__class__.__name__.upper()
        )
        
        # VALIDATE TRANSACTION ORDER
        t = service(
            transaction,
            context = self._get_response_context()
        ).prepare_transaction()
        
        # SEND REQUEST TO API 🍻
        return self._request(
            "POST", auth = False,detail = True,
            end_point = API_ENDPOINTS['initialize'],
            json = t
        )
        
    def get_transaction(self,*,token: str = None, _id: str = None):
        ''' Get details 📰 for a specific transaction by a given id or token. '''
        
        # ENSURE BOTH token AND _id ARE NOT NONE 🙃
        if token is None and _id is None:
            if self.config['raise_on_error']:
                raise ValueError(
                    'You must provide either a token or an id.'
                )
            self.logger.error(
                'get_transaction: You must provide either a token or an id 🥲.'
            )
            
        # THEN BUILD OUR REQUEST DATA
        data = self.config['credentials']       # THIS PROVIDES API_KEY AND SITE_ID
        
        # TRYING TO USE TOKEN
        if token :
            data |= {'token': token,}
        # OR USE ID ELSE
        if _id:
            data |= {'transaction_id': _id,}
        
        # SEND REQUEST TO API
        return self._request(
            "POST", auth = True, detail = True,
            end_point = f'/{API_ENDPOINTS["check"]}',
            json = data
        )