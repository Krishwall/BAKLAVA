from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "dev"
    database_url: str
    redis_url: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()