from pydantic import  AnyHttpUrl
from pydantic_settings import BaseSettings

class ConfigBase(BaseSettings):
    api_user: str
    api_key: str
    subscription_key: str
    target_environment: str = "sandbox"
    callback_host: AnyHttpUrl

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

config = ConfigBase() # type: ignore
