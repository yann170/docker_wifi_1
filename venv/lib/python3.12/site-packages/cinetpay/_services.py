from cinetpay._types import (
    Order, Config
)
from cinetpay._utils import (
    Logger
)

import simplejson as Json

####
##      SERVICES FACTORY
#####
class Factory:
    ''' Factory 🏭 of all Registred services. '''
    
    # REGISTRY
    registry = {}
    # LOGGER
    logger = Logger('Services Factory')
    
    @classmethod
    def register(cls, name):
        ''' Decorator to add connector to registry. '''
        def decorator(manager_class):
            # SERVICE MANAGER MUST BE BASE SERVICE INSTANCE
            if issubclass(manager_class, BaseService):
                # ADD SERVICE TO REGISTRY
                cls.registry[name] = manager_class
                # LOGGING
                cls.logger.info(
                    f'{name} service registered.'
                )
                return manager_class
            # RAISE EXCEPTION ELSE
            else:
                # LOGGING
                cls.logger.warning(
                    f'Cannot register service {name}.'
                    f'Invalid service type, looking for "BaseService" '
                    f'got "{manager_class.__name__}" abborting...'
                )
                # raise TypeError(
                #     f'Invalid service type, looking for "BaseService" '
                #     f'got {manager_class.__name__}'
                # )
        return decorator
            
    @classmethod  
    def get(cls,name):
        ''' return a registred manager by name. '''

        manager = cls.registry.get(name,None)
        if manager:
            return manager
        
        # DISPLAY HELP
        cls.help(name)
        
    @classmethod
    def help(cls,obj):
        ''' Raises an exeption... '''

        raise AttributeError(
            'Invalid Service name, '
            f'Factory has no registered service with name "{obj}".'
            f'choices are {cls.get_choices()}'
        )
    
    @classmethod
    def get_choices(cls):
        ''' Return a list of registered services names '''

        return list(cls.registry.keys())


####
##      BASE SERVICE
#####
class BaseService:
    ''' Base service for all Payments Aggregators service. '''
        
    # ORDER REQUIRED FIELDS
    order_required_fields = {}
    
    def __init__(self,transaction:Order,context = {}) -> None:
        ''' Initialize service. '''
        
        self.transaction = transaction
        self.context = context
        
    def get_order_required_fields(self)->list:
        ''' return a equired fields to validate an order. '''
        return self.order_required_fields
    
    def validate_order(self, order: dict,required_fields = None,name = 'order'):
        ''' Validate the order against required fields. '''

        # GET REQUIRED FIELDS
        required_fields = required_fields or self.get_order_required_fields()

        def check(fields: list, parent: dict, name = name):
            ''' Check for fields. '''
            
            for field in fields:
                if field not in parent:
                    return False, f"Missing key '{field}' in '{name}' object."
            return True, ''

        def check_levels(obj, level_fields, name = name):
            ''' Recursive function to go through nested objects. '''
            
            for field, subfields in level_fields.items():
                
                if field not in obj:
                    return False, f"Missing key '{field}' in '{name}' object."
                
                if isinstance(subfields, dict):
                    # RECURSIVELY CHECK NESTED FIELDS
                    # check_levels(obj[field], subfields, f"{name}.{field}")
                    required_fields = self.get_order_required_fields()['second_level_fields'].get(field)
                    res, message = self.validate_order(
                        obj.get(field),required_fields,name=f'{name}.{field}'
                    )
                    if not res:
                        return res, message
            return True, ''

        # CHECK FIRST LEVEL OF ORDER
        res, message = check(required_fields['first_level_fields'], order)
        if not res:
            return res, message

        if 'second_level_fields' in required_fields:
            res, message = check_levels(order, required_fields['second_level_fields'])

        return res, message
    
    def prepare_transaction(self) -> dict:
        ''' Prepare 🧪 Transaction object 📦 for initialisation request. '''
        
        # CAN DO CUSTOM LOGIC HERE BASED ON SERVICE HERE 🤓
        
        # GET CONFIG FROM CONTEXT
        config = self.context.get('client').config
        
        # VALIDATE ORDER URLS
        has_url,__ = self.transaction.check_urls()
        if not has_url:
            if config['raise_on_error']:
                raise Exception(__)
            self.context.get('client').logger.warning(__)
        
        # VALIDATE CUSTOMER
        is_customer_okay,_ = self.transaction.customer.check()
        if not is_customer_okay:
            if config['raise_on_error']:
                raise Exception(_)
            self.context.get('client').logger.warning(_)
        
        # UPDATE TRANSACTION 
        rep = self.transaction.to_representation() 
        currency = rep.pop('currency')
        currency = currency if currency else config['currency']
        rep |= dict(
            **config['credentials'],
            channels = config['channels'],
            lang = config['language'],
            currency = currency,
            lock_phone_number = config['lock_phone_number'],
        )
        
        valid,msg =  self.validate_order(
            rep
        )
        
        print(rep)
        
        if not valid:
            # THEN RAISE EXCEPTION IF NEEDED 🤨
            if config['raise_on_error']:
                raise AttributeError(msg)
            else:
                self.context['client'].logger.warning(msg)
                
        return rep
    
    
####
##      CINETPAY SERVICE
#####
@Factory.register(name = 'ORDER')
class ORDER(BaseService):
    ''' CinetPay Order validator service. '''
    
    # ORDER REQUIRED FIELDS
    order_required_fields = {
        'first_level_fields': [
            'currency','transaction_id',
            'description','customer_name',
            'customer_surname','apikey',
            'amount','site_id'
        ]
    }
    

##      GET SERVICE FUNCTION
def get_service(service:str) -> BaseService:
    ''' Return service from a given name. '''
    
    return Factory.get(service)