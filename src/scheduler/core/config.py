from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/djs"
    poll_interval_seconds: int = 5
    worker_poll_interval_seconds: int = 2


settings = Settings()
