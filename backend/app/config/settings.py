from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration, sourced from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "SAST Platform"
    environment: Literal["development", "test", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = Field(default="postgresql+asyncpg://sast:sast@localhost:5432/sast")

    # Security
    secret_key: str = Field(default="change-me-in-production-please")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 60 * 24 * 7

    # CORS
    cors_allow_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    # Rate limiting
    rate_limit_default: str = "100/minute"

    # Uploads / scans
    max_upload_size_mb: int = 50
    upload_dir: str = "uploads"
    reports_dir: str = "reports_output"
    allowed_upload_extensions: list[str] = Field(
        default_factory=lambda: [
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".php",
            ".go",
            ".rs",
            ".cs",
            ".cpp",
            ".c",
            ".zip",
        ]
    )

    # Logging
    log_level: str = "INFO"
    log_json: bool = True

    # AI (optional - see app/scanner/ai/analyzer.py). When unset, the app
    # falls back to NullAIAnalyzer and AI-dependent endpoints return 501.
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-5"


@lru_cache
def get_settings() -> Settings:
    return Settings()
