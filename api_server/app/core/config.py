"""Runtime configuration loaded from env vars + .env file."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    """Top-level application settings."""

    model_config = SettingsConfigDict(
        env_file=ROOT_ENV_FILE,
        env_file_encoding="utf-8",
        env_prefix="CRYPTOLAB_",
        case_sensitive=False,
        extra="ignore",
    )

    # ----- runtime -----
    environment: Literal["dev", "staging", "prod"] = "dev"
    docs_enabled: bool = True

    # ----- security -----
    jwt_secret: str = Field(
        ...,
        description="HS256 signing key for JWT access tokens.",
        min_length=32,
    )
    jwt_algorithm: Literal["HS256"] = "HS256"
    jwt_access_ttl_seconds: int = 1800
    password_pbkdf2_iterations: int = 100_000

    # KEK (Key Encryption Key) for the at-rest key store. Hex-encoded 32 bytes.
    master_key_hex: str = Field(
        default="00" * 32,
        description="AES-256 KEK used to wrap user key material before DB write.",
    )

    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"]
    )

    # ----- data plane -----
    database_url: str = "sqlite:///./cryptolab.db"
    redis_url: str = "memory://"

    # ----- rate limiting -----
    rate_limit_window_seconds: int = 60
    rate_limit_per_minute: int = 60
    login_rate_limit_per_minute: int = 5

    # ----- audit -----
    audit_sample_rate: float = 1.0  # 1.0 = log every request


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton accessor — call from anywhere instead of constructing directly."""
    return Settings()
