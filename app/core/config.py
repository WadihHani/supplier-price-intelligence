from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Supplier Price Intelligence API"
    app_version: str = "0.1.0"
    environment: str = "development"

    database_url: str = "sqlite:///./supplier_intelligence.db"
    ai_provider: str = "mock"
    ai_api_key: str | None = None
    ai_model: str = "gpt-4o-mini"
    jwt_secret_key: str | None = None
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
