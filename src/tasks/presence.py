"""Presence update task."""

from typing import TYPE_CHECKING

import discord
import structlog
from discord.ext import commands, tasks

if TYPE_CHECKING:
    from src.bot import DisCalendarBot

logger = structlog.get_logger()


class PresenceState:
    """State machine for presence updates."""

    STATES = ["help", "slash_help", "servers", "url"]

    def __init__(self):
        self.current_index = 0

    def next(self) -> None:
        """Move to next state."""
        self.current_index = (self.current_index + 1) % len(self.STATES)

    @property
    def current(self) -> str:
        """Get current state."""
        return self.STATES[self.current_index]


class PresenceTask(commands.Cog):
    """Cog for updating bot presence."""

    def __init__(self, bot: "DisCalendarBot"):
        self.bot = bot
        self.state = PresenceState()
        self.presence_loop.start()

    async def cog_unload(self) -> None:
        """Called when cog is unloaded."""
        self.presence_loop.cancel()

    @tasks.loop(seconds=10)
    async def presence_loop(self) -> None:
        """Update bot presence periodically."""
        await self._update_presence()
        self.state.next()

    @presence_loop.before_loop
    async def before_presence_loop(self) -> None:
        """Wait for bot to be ready before starting loop."""
        await self.bot.wait_until_ready()

    async def _update_presence(self) -> None:
        """Update presence based on current state."""
        state = self.state.current

        if state == "help":
            activity = discord.Activity(
                type=discord.ActivityType.watching, name="cal help"
            )
        elif state == "slash_help":
            activity = discord.Activity(
                type=discord.ActivityType.watching, name="/help"
            )
        elif state == "servers":
            num_servers = len(self.bot.guilds)
            activity = discord.Activity(
                type=discord.ActivityType.watching, name=f"{num_servers} servers"
            )
        else:  # url
            activity = discord.Activity(
                type=discord.ActivityType.listening, name="discalendar.app"
            )

        await self.bot.change_presence(
            activity=activity, status=discord.Status.online
        )
        logger.debug("Updated presence", state=state)


async def setup(bot: "DisCalendarBot") -> None:
    """Setup function for loading the cog."""
    await bot.add_cog(PresenceTask(bot))
