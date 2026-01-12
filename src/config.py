"""Configuration and environment variables."""

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    """Application configuration."""

    # Discord
    bot_token: str
    application_id: str
    invitation_url: str

    # Supabase
    supabase_url: str
    supabase_key: str

    # Optional
    log_level: str = "INFO"
    sentry_dsn: str | None = None

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            bot_token=os.environ["BOT_TOKEN"],
            application_id=os.environ["APPLICATION_ID"],
            invitation_url=os.environ.get(
                "INVITATION_URL",
                "https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID",
            ),
            supabase_url=os.environ["SUPABASE_URL"],
            supabase_key=os.environ["SUPABASE_SERVICE_KEY"],
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            sentry_dsn=os.environ.get("SENTRY_DSN"),
        )


@lru_cache
def get_config() -> Config:
    """Get configuration singleton."""
    return Config.from_env()
