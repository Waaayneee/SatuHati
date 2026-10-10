from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database (Supabase session pooler, driver prefix postgresql+psycopg://)
    database_url: str = ""
    test_database_url: str = ""
    # Optional schema for tests when the test database shares the dev project
    test_database_schema: str = ""

    # Supabase Auth verification
    supabase_url: str = ""
    supabase_jwt_mode: Literal["jwks", "secret"] = "jwks"
    supabase_jwt_secret: str = ""

    # Claude API
    anthropic_api_key: str = ""
    anthropic_model: str = ""
    # Optional: effort level ("low" | "medium" | "high" ...). Blank uses the model default.
    anthropic_effort: str = ""
    # Optional: server-side refusal fallback mode ("default"). Blank turns it off.
    anthropic_fallbacks: str = ""

    # Agent identity
    agent_service_token: str = ""

    # Approval settings
    approval_ttl_hours: int = 48
    agent_max_iterations: int = 8

    # Seed users
    seed_hod_email: str = ""
    seed_committee_emails: str = ""

    # CORS
    frontend_origin: str = "http://localhost:3000"

    @property
    def supabase_issuer(self) -> str:
        return f"{self.supabase_url.rstrip('/')}/auth/v1"

    @property
    def supabase_jwks_url(self) -> str:
        return f"{self.supabase_issuer}/.well-known/jwks.json"

    @property
    def seed_committee_email_list(self) -> list[str]:
        return [e.strip().lower() for e in self.seed_committee_emails.split(",") if e.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
