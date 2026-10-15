from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "CommunityLab API"
    api_schema_version: str = "v1"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://communitylab:communitylab@db:5432/communitylab"
    cors_origins: list[str] = ["http://localhost:8501", "http://127.0.0.1:8501"]
    storage_backend: str = "local"
    storage_bucket: str = "communitylab-local"
    local_storage_path: str = "/tmp/communitylab-storage"
    oci_namespace: str | None = None
    oci_region: str | None = None
    oci_use_instance_principal: bool = True
    analysis_provider: Literal["mock", "gemini"] = "mock"
    analysis_fallback_provider: Literal["mock", "gemini"] | None = None
    analysis_max_attempts: int = Field(default=2, ge=1, le=5)
    analysis_prompt_version: str = "analysis-gemini-v1"
    faq_recurrence_threshold: int = Field(default=2, ge=2, le=20)
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-3.1-flash-lite"

    @field_validator("database_url", mode="before")
    @classmethod
    def use_psycopg_v3(cls, value: str) -> str:
        """Render and Neon expose generic PostgreSQL URLs; the app uses psycopg 3."""
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
