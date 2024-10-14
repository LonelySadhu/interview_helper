from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    api_key: str = ...
    assistant_id: str = ...
    model_config = SettingsConfigDict(env_prefix='')


settings = Settings()

