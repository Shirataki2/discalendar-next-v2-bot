"""Invite command."""

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from src.config import get_config

if TYPE_CHECKING:
    from src.bot import DisCalendarBot


class InviteCommand(commands.Cog):
    """Invite command cog."""

    def __init__(self, bot: "DisCalendarBot"):
        self.bot = bot

    @app_commands.command(name="invite", description="このBotの招待URLを表示します")
    async def invite(self, interaction: discord.Interaction) -> None:
        """Display bot invitation URL."""
        await interaction.response.send_message(get_config().invitation_url)


async def setup(bot: "DisCalendarBot") -> None:
    """Setup function for loading the cog."""
    await bot.add_cog(InviteCommand(bot))
