import simplejson as Json
from typing import (
    Any, TypedDict, Sequence, Optional,
    Mapping
)
    
from cinetpay._schema import (
    Channels, Languages, Currencies
)
from cinetpay._utils import (
    Logger
)
    
    
####
##      CREDENTIALS MODEL
#####
class Credential(TypedDict):
    ''' Account Credentials Model. '''
    
    apikey : str                        # CINEPAY ACCOUNT APIKEY
    site_id : str                        # ACCOUNT SITE ID
  
  
####
##      CONFIGS BASE REPRESENTATION CLASS
#####
class Config(TypedDict,total=True):
    """ The base class for all configs. """
    
    host : Optional[str] = None,                # HOST
    credentials : Credential                    # AUTH MODEL
    channels : Optional[str] = Channels.ALL     # AVAILABLE PAYMENT CHANNELS
    language : Optional[str] = Languages.FR     # GATEWAY LANGUAGE
    currency : Optional[str] = Currencies.XOF   # TRANSACTION CURRENCY
    lock_phone_number : bool = False            # IF IT'S SET TO TRUE, CLIENT PHONE NUMBER WILL BE AUTOMATICALLY USED TOO FILL CHECKOUT PAGE.
    raise_on_error : bool                       # IF SET TO TRUE, RAISE IF EXCEPTION OCCURES 
    
    
####
##      CUSTOMER MODEL
#####
class Customer(object):
    ''' Transaction Customer representation model. '''
    
    # MINIMAL REQUIRED FIELDS BASED ON TRANSACTION CHANNEL
    _required_fields = [
        'customer_id', 'customer_name', 'customer_surname',
        'customer_phone_number'
    ]
    # CHOICES FIELDS
    _choices_fields = {
        'customer_country':{
            'schema': Channels
        }
    }
    
    # APP USED CHANNEL
    channel: str = None
    
    def __init__(
        self,customer_id, customer_name, customer_surname,
        customer_phone_number, *, 
        customer_email = '', 
        customer_address = '',
        customer_city = '',
        customer_country = '',
        customer_zip_code = '',
        customer_state = ''
    ):
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.customer_surname = customer_surname
        self.customer_phone_number = customer_phone_number
        self.customer_email = customer_email
        self.customer_address = customer_address
        self.customer_city = customer_city
        self.customer_country = customer_country
        self.customer_zip_code = customer_zip_code
        self.customer_state = customer_state
    
    def get_channel(self):
        ''' Return Configurations channel. '''
        return self.channel
    
    def get_required_fields(self,)->Sequence[str]:
        ''' return required fields for validation based on used channel. '''
        
        # ADD CREDIT CARD CHANNEL SPECIFIC FIELDS
        if self.get_channel() == Channels.CREDIT_CARD:
            self._required_fields.extend(
                [
                    'customer_email','customer_address', 
                    'customer_city', 'customer_country',
                    'customer_state', 'customer_zip_code'
                ]
            )
        
        return self._required_fields
    
    def check(self):
        ''' Validate Transaction customer data. '''
        
        for fields in self.get_required_fields():
            if not getattr(self, fields):
                return False, f'Customer {fields} is required.'
            
        return True,''
                    
    def to_representation(self):
        ''' Returns a Json representation of Customer object. '''
        
        d = {}
        for fields in self.get_required_fields():
            d[fields] = getattr(self, fields)
        return d
    


####
##      TRANSACTION ORDER CLASS
#####
class Order(object):
    ''' Represents Transaction Order.

        - `id` : str
        The order id.
        - `amount` : int
        Amount of the transaction 
        - `currency` : str
        Currency of the transaction
        - `notify_url` : str
        Callback URL where the provider will send notifications about the transaction.
        - `return_url` : str
        Return URL after a successful payment
       - `description` : str
        The requesting transaction order's short description
        - `customer` : dict[str,any]
        Transaction Order Client or contact.
    '''
    
    def __init__(
        self,
        id:str,
        amount,
        customer: Customer,
        currency = None,
        notify_url = None,
        return_url = None,
        description = 'This is a transaction.',
    ):
        self.id = id
        self.amount = amount
        self.currency = currency
        self.customer = customer
        self.notify_url = notify_url
        self.return_url = return_url
        self.description = description
        
    def check_urls(self):
        ''' Check that either notify url or return url is is given. '''
        
        if self.notify_url is None and self.return_url is None:
            return False, (
                'Either notify_url or return_url must be given '
                'for any Transaction order.'
                )
        return True,''
        
    def to_representation(self):
        ''' Return a dict representation of a transaction. '''
        
        d = {
            'transaction_id': self.id,
            'amount': self.amount,
            'currency': self.currency,
            'notify_url': self.notify_url,
            'return_url': self.return_url,
            'description': self.description,
        }
        d |= self.customer.to_representation()
        
        return d
        
        
####
##      REQUEST RESPONSE
#####
class Response:
    ''' Request response Manager. '''
    
    def __init__(
        self,
        response = None,
        context = {}
    ):
        self.response = response
        self.context = context
        
        # INITIALIZE LOGGER
        self.logger = Logger('Response Manager')
        
    @property
    def json(self):
        ''' Return response json content. '''
        return self.response.json()
    
    @property
    def client(self):
        ''' Get the request Client instance. '''
        return self.context.get('client')
    
    @property
    def request(self):
        ''' Get the related request object. '''
        return self.response.request
    
    @property
    def status_code(self):
        ''' Get HTTP Status Code of the response. '''
        return self.response.status_code
    
    @property
    def base_url(self):
        ''' Return context Base URL. '''
        return self.context['base_url']
    
    @property
    def has_error(self):
        ''' Check if it's an error response. '''
        return False
    
    def __str__(self) -> str:
        return f'<{self.__class__.__name__} [{self.status_code}]>'
    
    
####
##      PAGGINATED RESPONSE MANAGER
#####
class PagginatedResponse(Response):
    ''' Used to manage pagginated responses. '''
    
    # OBJECTS COUNT
    count : int = 0
    # NEXT PAGE URL
    next_url : str = ''
    # PREVIOUS PAGE URL
    previous_url : str = ''
    # RESULTS 
    results: Sequence[Mapping[str,Any]] = []
    
    def __init__(self, response=None, context={}):
        super().__init__(response, context)
        
        self.process_data()
        
        # LOGGING SUCCESS
        self.logger.info(
            f'{self.request.method} {self.request.url} {self.response.status_code}'
        )
        
    def __str__(self):
        return f'<{self.__class__.__name__} [{self.status_code}]>'
        
    def process_data(self):
        ''' Build attributes. '''
        
        data = self.json
        self.count = data['count']
        self.next_url = data['next'] or None
        self.previous_url = data['previous'] or None
        self.results = data['results']
        
    @property
    def has_next(self):
        return self.next_url is not None
    
    @property
    def has_prev(self):
        return self.previous_url is not None
        
    @property
    def next_page(self):
        ''' Send request to get next page objects '''
        # RAISE VALUE ERROR IF NEXT URL IS NONE
        if not self.next_url: raise
        
        # GET ENDPOINT FROM URL
        _,__,endpoint = self.next_url.partition(
            self.base_url
        )
        # SEND REQUEST
        return self.send_request(endpoint = endpoint)
    
    @property
    def previous_page(self):
        ''' Send request to get previous page objects '''
        # RAISE VALUE ERROR IF NEXT URL IS NONE
        if not self.previous_url: raise
        
        # GET ENDPOINT FROM URL
        _,__,endpoint = self.previous_url.partition(
            self.base_url
        )
        # SEND REQUEST
        return self.send_request(endpoint = endpoint)
        
    def send_request(self,endpoint):
        ''' Send request using context client. '''
        return self.client._request(
            "GET", True, end_point = endpoint 
        )
      
      
####
##      ERROR RESPONSE
#####
class ErrorResponse(Response):
    ''' Error Response Manager. '''
    
    # MESSAGE ATTR KEYS
    keys = [
        'detail','message','non_field_errors'
    ]
    
    # ROOR CODES
    ERROR_CODES = {
        '608':{
            'description': 'Minimum required field',
            'cause':(
                "Un paramètre obligatoire n'a pas été fourni ou "
                "une erreur sur la nomenclature du paramètre. "
                "Le format de la requête n'est pas JSON. La valeur du paramètre n'est pas valide"
            ),
            'hint': (
                "Vérifier le tableau des paramètres ou le format d'envoi"
            )
        },
        '609':{
            'description': 'AUTH_NOT_FOUND',
            'cause': "apikey fourni n'est pas correcte",
            'hint': (
                "Récupérer l'apikey correcte dans votre back-office(menu integration)"
            )
        },
        '613':{
            'description': 'ERROR_SITE_ID_NOTVALID',
            'cause': "site_id fourni n'est pas correcte",
            'hint': (
                "Récupérer l'apikey correcte dans votre back-office(menu integration)"
            )
        },
        '624':{
            'description': 'An error occurred while processing the request',
            'cause': (
                "1- l'apikey saisi est incorrect \n"
                "2- La valeur de lock_phone_number est à true mais "
                "la valeur du customer_phone_number est incorrect"
            ),
            'hint': (
                "1- Récupérer l'apikey correcte dans votre back-office(menu integration) \n"
                "2- La variable doit être false"
            )
        },
        '403':{
            'description': 'Forbidden',
            'cause':(
                "Cela se produit lorsque le content-type utilisé est différent du format json"
            ),
            'hint':''
        },
        '429':{
            'description': 'TOO_MANY_REQUEST',
            'cause':(
                "Le système a détecté que l'activité que vous menez sur l'api est suspecte"
            ),
            'hint':'Conformez-vous aux instructions données pour initier correctement votre paiement'
        },
        '1010':{
            'description':"Erreur code :1010 signifie qu'il y a une restriction suite à la requête émise par votre serveur.",
            'cause': (
                "L'erreur survient parce que votre application n'a pas envoyé d' user-agent à l'api CinetPay"
            )
        }
    }
    
    def __init__(self, response=None, context={}):
        super().__init__(response, context)

        # LOG ERROR
        self.logger.error(
            self.get_message()
        )
        # LOG ERROR DESCRIPTION
        self.logger.critical(
            self.description
        )
        # LOG ERROR CAUSES
        self.logger.critical(
            self.cause
        )
        # LOG ERROR HINT
        self.logger.warning(
            self.hint
        )
        # DISPLAY ERRORS DOC
        self.display_doc()
        
    @property
    def has_error(self):
        ''' Check if it's an error response. '''
        return True
    
    @property
    def error(self):
        ''' Get the error doc and hint based on code. '''
        return self.ERROR_CODES.get(self.json.get('code'),{})
    
    @property
    def description(self):
        ''' Get the error description. '''
        return self.error.get('description')
        
    @property
    def cause(self):
        ''' Get the error cause. '''
        return self.error.get('cause')
        
    @property
    def hint(self)->str:
        ''' Get the error hint. '''
        return self.error.get('hint')
        
    def get_message(self) -> str:
        ''' Get message from response. '''
        
        # GET MESSAGE FROM RESPONSE JSON
        try:
            # for key in self.keys:
            #     if key in self.json:
            #         return self.json.get(
            #             key, self.response.text
            #         )
            return f'{self.json}'
                    
        except Exception as e:
            # RETURN RESPONSE TEXT OTHERWISE
            return self.response.text
        
    def display_doc(self):
        ''' Display error doc. '''
        self.logger.info(
            '\nFor more information check: ' +\
            "https://docs.cinetpay.com/api/1.0-fr/checkout/initialisation#problemes-frequents"
        )
            
    
####
##      RESPONSE ERROR
#####        
class ResponseError(Exception):
  """
  Common class for response errors.
  """

  def __init__(self, error: str, status_code: int = -1):
    try:
      # TRY TO PARSE CONTENT AS JSON AND EXTRACT 'error'
      # FALLBACK TO RAW content if JSON parsing fails
      error = Json.loads(error).get('detail', error)
    except Json.JSONDecodeError:
      ...

    super().__init__(error)
    self.error = error
    'Reason for the error.'

    self.status_code = status_code
    'HTTP status code of the response.'