"""Help command."""

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from src.config import get_config
from src.utils.embeds import create_help_embed

if TYPE_CHECKING:
    from src.bot import DisCalendarBot


class HelpCommand(commands.Cog):
    """Help command cog."""

    def __init__(self, bot: "DisCalendarBot"):
        self.bot = bot

    @app_commands.command(name="help", description="このBotの使い方を表示します")
    async def help(self, interaction: discord.Interaction) -> None:
        """Display help information."""
        bot_avatar = None
        if self.bot.user and self.bot.user.avatar:
            bot_avatar = self.bot.user.avatar.url

        embed = create_help_embed(bot_avatar, get_config().invitation_url)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: "DisCalendarBot") -> None:
    """Setup function for loading the cog."""
    await bot.add_cog(HelpCommand(bot))
