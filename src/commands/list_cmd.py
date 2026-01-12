"""List command for displaying events."""

from typing import TYPE_CHECKING, Literal

import discord
from discord import app_commands
from discord.ext import commands

from src.models import Event
from src.utils.datetime import format_datetime

if TYPE_CHECKING:
    from src.bot import DisCalendarBot


class EventListView(discord.ui.View):
    """Paginated view for event list."""

    def __init__(self, events: list[Event], per_page: int = 4):
        super().__init__(timeout=180)
        self.events = events
        self.per_page = per_page
        self.current_page = 0
        self.max_pages = (len(events) - 1) // per_page + 1

        self._update_buttons()

    def _update_buttons(self) -> None:
        """Update button states."""
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= self.max_pages - 1

    def get_embed(self) -> discord.Embed:
        """Get embed for current page."""
        embed = discord.Embed(title="予定一覧", color=0x0000FF)

        start = self.current_page * self.per_page
        end = start + self.per_page
        page_events = self.events[start:end]

        for event in page_events:
            notifications_str = ""
            if event.notifications:
                notifications_str = ", ".join(str(n) for n in event.notifications)

            value = (
                f"`開始時刻`: {format_datetime(event.start_at)}\n"
                f"`終了時刻`: {format_datetime(event.end_at)}\n"
                f"`　通知　`: {notifications_str or 'なし'}"
            )
            embed.add_field(name=event.name, value=value, inline=False)

        embed.set_footer(text=f"ページ {self.current_page + 1}/{self.max_pages}")
        return embed

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """Previous page button."""
        self.current_page -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """Next page button."""
        self.current_page += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)


class ListCommand(commands.Cog):
    """List command cog."""

    def __init__(self, bot: "DisCalendarBot"):
        self.bot = bot

    @app_commands.command(name="list", description="予定の一覧を表示します")
    @app_commands.describe(range="表示する予定の範囲")
    @app_commands.choices(
        range=[
            app_commands.Choice(name="過去", value="past"),
            app_commands.Choice(name="未来", value="future"),
            app_commands.Choice(name="全て", value="all"),
        ]
    )
    async def list_events(
        self,
        interaction: discord.Interaction,
        range: Literal["past", "future", "all"] = "future",
    ) -> None:
        """List events for this guild."""
        if not interaction.guild:
            await interaction.response.send_message(
                "このコマンドはサーバーでのみ実行可能です", ephemeral=True
            )
            return

        # 処理前応答（3秒以内に必須）
        await interaction.response.defer()

        guild_id = str(interaction.guild.id)
        events = await self.bot.event_service.find_by_guild_id(guild_id, range)

        if not events:
            await interaction.followup.send("現在登録されている予定はありません", ephemeral=True)
            return

        view = EventListView(events)
        await interaction.followup.send(embed=view.get_embed(), view=view)


async def setup(bot: "DisCalendarBot") -> None:
    """Setup function for loading the cog."""
    await bot.add_cog(ListCommand(bot))
