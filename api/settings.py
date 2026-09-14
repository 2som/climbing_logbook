from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    auth_secret_key: str
    access_token_expire_minutes: int = Field(min=1)

    model_config = SettingsConfigDict(env_file=".env")
