"""Discord Bot class definition."""

import discord
import structlog
from discord.ext import commands
from supabase import Client, create_client

from src.config import get_config
from src.services import EventService, GuildService

logger = structlog.get_logger()


class DisCalendarBot(commands.Bot):
    """DisCalendar Discord Bot."""

    def __init__(self) -> None:
        config = get_config()

        intents = discord.Intents.default()
        intents.guilds = True
        intents.guild_messages = True

        super().__init__(
            command_prefix="cal ",
            intents=intents,
            application_id=int(config.application_id),
        )

        # Supabase client
        self.supabase: Client = create_client(
            config.supabase_url,
            config.supabase_key,
        )

        # Services
        self.guild_service: GuildService = GuildService(self.supabase)
        self.event_service: EventService = EventService(self.supabase)

    async def setup_hook(self) -> None:
        """Called when the bot is starting up."""
        logger.info("Setting up bot...")

        # Load extensions (cogs)
        await self.load_extension("src.commands.help")
        await self.load_extension("src.commands.invite")
        await self.load_extension("src.commands.list_cmd")
        await self.load_extension("src.commands.create")
        await self.load_extension("src.commands.init")
        await self.load_extension("src.events.guild")
        await self.load_extension("src.tasks.presence")
        await self.load_extension("src.tasks.notify")

        logger.info("Loaded all extensions")

        # Sync slash commands
        await self.tree.sync()
        logger.info("Synced slash commands")

    async def on_ready(self) -> None:
        """Called when the bot is fully ready."""
        if self.user:
            logger.info("Bot is ready", user=str(self.user), user_id=self.user.id)
        else:
            logger.info("Bot is ready")

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        """Called when an error occurs."""
        logger.exception(
            "Error in event handler",
            event_method=event_method,
            args=args,
            kwargs=kwargs,
        )
