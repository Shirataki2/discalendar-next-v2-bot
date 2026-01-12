"""Init command for setting notification channel."""

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from src.utils.permissions import has_manage_permissions

if TYPE_CHECKING:
    from src.bot import DisCalendarBot


class InitCommand(commands.Cog):
    """Init command cog."""

    def __init__(self, bot: "DisCalendarBot"):
        self.bot = bot

    @app_commands.command(name="init", description="このBotの通知の送信先を設定します")
    @app_commands.describe(
        channel="通知先のチャンネル(指定しない場合はこのコマンドを送信したチャンネルになります)"
    )
    async def init(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel | None = None,
    ) -> None:
        """Set notification channel."""
        if not interaction.guild:
            await interaction.response.send_message(
                "このコマンドはサーバー内で実行してください", ephemeral=True
            )
            return

        # Check permissions
        if isinstance(interaction.user, discord.Member):
            if not has_manage_permissions(interaction.user):
                await interaction.response.send_message(
                    "このコマンドを実行するためには「管理者」「サーバー管理」"
                    "「ロールの管理」「メッセージの管理」のいずれかの権限が必要です",
                    ephemeral=True,
                )
                return

        # Use current channel if not specified
        target_channel = channel or interaction.channel
        if not target_channel:
            await interaction.response.send_message(
                "チャンネルを指定してください", ephemeral=True
            )
            return

        guild_id = str(interaction.guild.id)
        channel_id = str(target_channel.id)

        # Check existing settings
        existing = await self.bot.event_service.get_settings(guild_id)

        if existing:
            old_channel_id = existing.channel_id
            await self.bot.event_service.update_settings(guild_id, channel_id)
            await interaction.response.send_message(
                f"イベント通知先を変更しました\n"
                f"通知先: <#{old_channel_id}> → <#{channel_id}>"
            )
        else:
            await self.bot.event_service.create_settings(guild_id, channel_id)
            await interaction.response.send_message(
                f"イベント通知を有効にしました\n通知先: <#{channel_id}>"
            )


async def setup(bot: "DisCalendarBot") -> None:
    """Setup function for loading the cog."""
    await bot.add_cog(InitCommand(bot))
