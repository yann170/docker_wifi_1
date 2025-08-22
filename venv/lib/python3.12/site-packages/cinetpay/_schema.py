from enum import Enum
from pydantic import BaseModel, Field # type: ignore

__all__ = [
    'Channels',
    'Currencies',
    'Languages',
    'CustomerCountryCodes'
]


####
##      BASE SCHEMA CLASS
#####
class BaselSchema(BaseModel):
    ''' Base class for All Schemas. '''
    
    def get_name(self):
        ''' Return specific mapped attribute name. '''
        return 'Schema'
    
    def validate(self,channel):
        ''' Checks if a given channel name is valid. '''
        
        keys = self.model_dump().values()
        if not channel in keys:
            return False, (
                f'Invalid {self.get_name()} value :`{channel}`',
                f'choices are {keys}.'
            )
        return True ,''


####
##      TRANSACTION CHANNELS CHOICES
#####
class ChannelSchema(BaselSchema):
    ''' Supported Transaction Channels. '''
    
    ALL: str = Field(
       default = 'ALL',
       description = 'Uses all supported Transaction Channels'
    )
    ''' Uses all supported Transaction Channels '''
   
    MOBILE_MONEY: str = Field(
        default = 'MOBILE_MONEY',
        description = 'Uses Only supported mobile moneys.'
    )
    ''' Uses Only supported mobile moneys. '''
    
    CREDIT_CARD: str = Field(
        default = 'CREDIT_CARD',
        description = 'Uses Only supported credit cards.'
    )
    ''' Uses Only supported credit cards. '''
    
    WALLET: str = Field(
        default = 'WALLET',
        description = 'Uses Only supported wallets.'
    )
    ''' Uses Only supported wallets '''
    
    def get_name(self):
        return 'Channel'
   

####
##      TRANSACTION CURRENCY CHOICES
#####
class CurrencySchema(BaselSchema):
    ''' Supported Transaction Currencies. '''
    
    XOF: str = Field(
        default = 'XOF',
        description = 'West African (WAEMU) CFA franc.'
    )
    ''' 
    The West African CFA franc (XOF) is the currency shared by eight 
    independent West African states, which constitute the West African 
    Economic and Monetary Union (WAEMU or UEMOA). 
    '''
    
    XAF: str = Field(
        default = 'XAF',
        description = 'Central African CFA franc.'
    )
    '''
    The Central African CFA franc (XAF) is the currency shared by six
    independent Central African states: Cameroon, the Central African Republic, 
    Chad, the Republic of the Congo, Equatorial Guinea, and Gabon.
    '''
    
    CDF: str = Field(
        default = 'CDF',
        description = 'Congolese franc.'
    )
    '''
    The Congolese franc (code FC) is the currency of the Democratic Republic of the Congo (DRC).
    '''
    
    GNF: str = Field(
        default = 'GNF',
        description = 'Guinean franc.'
    )
    '''
    The Guinean franc (GNF) is the currency of Guinea, a country in West Africa.
    '''
    
    USD: str = Field(
        default = 'USD',
        description = 'United States dollar.'
    )
    '''
    The United States dollar (symbol: $; code: USD) is the official currency of the 
    United States and its territories per the Coinage Act of 1792.
    '''
    
    def get_name(self):
        return 'Currency'
    
    
####
##      TRANSACTION GATEWAY LANGUAGE CHOICES
#####
class LanguageSchema(BaselSchema):
    ''' Supported Transaction GateWay Languages. '''
    
    FR: str = Field(
        default = 'fr',
        description = 'French.'
    )
    ''' French language. '''
    
    EN: str = Field(
        default = 'en',
        description = 'English.'
    )
    ''' English language. '''
    
    def get_name(self):
        return 'Language'
    
    
####
##      TRANSACTION CUSTOMER COUNTRY CHOICES FOR CREDIT CARD CHANNEL
#####
class CustomerCountryCodeSchema(BaselSchema):
    ''' Supported Transaction Customer country Code choices. '''
    
    CI: str = Field(
        default = 'CI',
        description = 'Côte d\'Ivoire.'
    )
    ''' Ivory Coast. '''
    
    BF: str = Field(
        default = 'BF',
        description = 'Burkina Faso.'
    )
    ''' Burkina Faso. '''
    
    US: str = Field(
        default = 'US',
        description = 'United States.'
    )
    ''' United States. '''
    
    CA: str = Field(
        default = 'CA',
        description = 'Canada.'
    )
    ''' Canada. '''
    
    FR: str = Field(
        default = 'FR',
        description = 'France.'
    )
    ''' France. '''
    
    def get_name(self):
        return 'Country Code'
    
     
Channels = ChannelSchema()
Currencies = CurrencySchema()
Languages = LanguageSchema()
CustomerCountryCodes = CustomerCountryCodeSchema()