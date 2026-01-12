"""Guild service for database operations."""

from typing import Any, cast

import structlog
from supabase import Client

from src.models import Guild, GuildConfig, GuildCreate

logger = structlog.get_logger()


class GuildService:
    """Service for guild database operations."""

    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def find_by_guild_id(self, guild_id: str) -> Guild | None:
        """Find a guild by Discord guild ID."""
        response = self.supabase.table("guilds").select("*").eq("guild_id", guild_id).execute()
        if response.data:
            return Guild.from_dict(cast(dict[str, Any], response.data[0]))
        return None

    async def create(self, data: GuildCreate) -> Guild:
        """Create a new guild."""
        response = self.supabase.table("guilds").insert(data.to_dict()).execute()
        logger.info("Created guild", guild_id=data.guild_id, name=data.name)
        return Guild.from_dict(cast(dict[str, Any], response.data[0]))

    async def update(self, guild_id: str, data: GuildCreate) -> Guild:
        """Update a guild."""
        update_data = {
            "name": data.name,
            "avatar_url": data.avatar_url,
            "locale": data.locale,
        }
        response = (
            self.supabase.table("guilds").update(update_data).eq("guild_id", guild_id).execute()
        )
        logger.info("Updated guild", guild_id=guild_id, name=data.name)
        return Guild.from_dict(cast(dict[str, Any], response.data[0]))

    async def delete(self, guild_id: str) -> None:
        """Delete a guild."""
        self.supabase.table("guilds").delete().eq("guild_id", guild_id).execute()
        logger.info("Deleted guild", guild_id=guild_id)

    async def get_config(self, guild_id: str) -> GuildConfig | None:
        """Get guild configuration."""
        response = (
            self.supabase.table("guild_config").select("*").eq("guild_id", guild_id).execute()
        )
        if response.data:
            return GuildConfig.from_dict(cast(dict[str, Any], response.data[0]))
        return None

    async def upsert_config(self, guild_id: str, restricted: bool) -> GuildConfig:
        """Create or update guild configuration."""
        response = (
            self.supabase.table("guild_config")
            .upsert({"guild_id": guild_id, "restricted": restricted})
            .execute()
        )
        return GuildConfig.from_dict(cast(dict[str, Any], response.data[0]))
