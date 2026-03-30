from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://wildscan:wildscan@localhost:5432/wildscan"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    bright_data_api_token: str = ""
    cors_origins: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
