"""Guild event handlers."""

from typing import TYPE_CHECKING

import discord
import structlog
from discord.ext import commands

from src.models import GuildCreate

if TYPE_CHECKING:
    from src.bot import DisCalendarBot

logger = structlog.get_logger()


class GuildEvents(commands.Cog):
    """Cog for handling guild events."""

    def __init__(self, bot: "DisCalendarBot"):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Called when the bot joins a guild."""
        logger.info("Joined guild", guild_id=guild.id, guild_name=guild.name)

        # Check if guild already exists
        existing = await self.bot.guild_service.find_by_guild_id(str(guild.id))
        if existing:
            logger.debug("Guild already exists", guild_id=guild.id)
            return

        # Create guild in database
        guild_data = GuildCreate(
            guild_id=str(guild.id),
            name=guild.name,
            avatar_url=guild.icon.url if guild.icon else None,
            locale="ja",
        )
        await self.bot.guild_service.create(guild_data)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Called when the bot leaves a guild."""
        logger.info("Left guild", guild_id=guild.id, guild_name=guild.name)

        # Delete guild from database
        await self.bot.guild_service.delete(str(guild.id))

    @commands.Cog.listener()
    async def on_guild_update(
        self, before: discord.Guild, after: discord.Guild
    ) -> None:
        """Called when a guild is updated."""
        # Only update if name or icon changed
        name_changed = before.name != after.name
        icon_changed = before.icon != after.icon

        if not (name_changed or icon_changed):
            return

        logger.info(
            "Guild updated",
            guild_id=after.id,
            old_name=before.name,
            new_name=after.name,
        )

        # Update guild in database
        guild_data = GuildCreate(
            guild_id=str(after.id),
            name=after.name,
            avatar_url=after.icon.url if after.icon else None,
            locale="ja",
        )
        await self.bot.guild_service.update(str(after.id), guild_data)


async def setup(bot: "DisCalendarBot") -> None:
    """Setup function for loading the cog."""
    await bot.add_cog(GuildEvents(bot))
