from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "CommunityLab API"
    api_schema_version: str = "v1"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://communitylab:communitylab@db:5432/communitylab"
    cors_origins: list[str] = ["http://localhost:8501", "http://127.0.0.1:8501"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
