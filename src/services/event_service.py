"""Event service for database operations."""

from datetime import datetime
from typing import Any, cast

import structlog
from supabase import Client

from src.models import Event, EventCreate, EventSettings

logger = structlog.get_logger()


class EventService:
    """Service for event database operations."""

    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def find_by_guild_id(
        self, guild_id: str, range_type: str = "future"
    ) -> list[Event]:
        """Find events by guild ID with optional range filter."""
        now = datetime.utcnow().isoformat()

        query = self.supabase.table("events").select("*").eq("guild_id", guild_id)

        if range_type == "past":
            query = query.lt("start_at", now)
        elif range_type == "future":
            query = query.gte("start_at", now)
        # "all" - no additional filter

        query = query.order("start_at")
        response = query.execute()

        return [Event.from_dict(cast(dict[str, Any], e)) for e in response.data]

    async def find_all_future_events(self, from_time: datetime) -> list[Event]:
        """Find all future events across all guilds."""
        response = (
            self.supabase.table("events")
            .select("*")
            .gte("start_at", from_time.isoformat())
            .order("start_at")
            .execute()
        )
        return [Event.from_dict(cast(dict[str, Any], e)) for e in response.data]

    async def create(self, data: EventCreate) -> Event:
        """Create a new event."""
        response = self.supabase.table("events").insert(data.to_dict()).execute()
        logger.info("Created event", guild_id=data.guild_id, name=data.name)
        return Event.from_dict(cast(dict[str, Any], response.data[0]))

    async def get_settings(self, guild_id: str) -> EventSettings | None:
        """Get event settings for a guild."""
        response = (
            self.supabase.table("event_settings")
            .select("*")
            .eq("guild_id", guild_id)
            .execute()
        )
        if response.data:
            return EventSettings.from_dict(cast(dict[str, Any], response.data[0]))
        return None

    async def create_settings(self, guild_id: str, channel_id: str) -> EventSettings:
        """Create event settings for a guild."""
        response = (
            self.supabase.table("event_settings")
            .insert({"guild_id": guild_id, "channel_id": channel_id})
            .execute()
        )
        logger.info("Created event settings", guild_id=guild_id, channel_id=channel_id)
        return EventSettings.from_dict(cast(dict[str, Any], response.data[0]))

    async def update_settings(self, guild_id: str, channel_id: str) -> EventSettings:
        """Update event settings for a guild."""
        response = (
            self.supabase.table("event_settings")
            .update({"channel_id": channel_id})
            .eq("guild_id", guild_id)
            .execute()
        )
        logger.info("Updated event settings", guild_id=guild_id, channel_id=channel_id)
        return EventSettings.from_dict(cast(dict[str, Any], response.data[0]))
