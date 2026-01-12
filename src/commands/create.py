"""Create command for adding new events."""

from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Literal

import discord
from discord import app_commands
from discord.ext import commands

from src.models import EventCreate
from src.utils.datetime import validate_date
from src.utils.embeds import create_event_embed
from src.utils.permissions import has_manage_permissions

if TYPE_CHECKING:
    from src.bot import DisCalendarBot


class Color(Enum):
    """Event color choices."""

    WHITE = ("白", 0xFFFFFF)
    BLACK = ("黒", 0x000000)
    RED = ("赤", 0xFD4028)
    BLUE = ("青", 0x3E44F7)
    GREEN = ("緑", 0x33F54B)
    YELLOW = ("黄", 0xEAFF33)
    PURPLE = ("紫", 0xA31CE0)
    GRAY = ("灰", 0x808080)
    BROWN = ("茶", 0xA54F4F)
    AQUA = ("水色", 0x44F3F3)

    def to_hex(self) -> str:
        """Convert to hex color code."""
        return f"#{self.value[1]:06x}"


class Notification(Enum):
    """Notification timing choices."""

    FIVE_MINUTES = ("5分前", 5, "分前")
    TEN_MINUTES = ("10分前", 10, "分前")
    FIFTEEN_MINUTES = ("15分前", 15, "分前")
    THIRTY_MINUTES = ("30分前", 30, "分前")
    ONE_HOUR = ("1時間前", 1, "時間前")
    TWO_HOURS = ("2時間前", 2, "時間前")
    THREE_HOURS = ("3時間前", 3, "時間前")
    SIX_HOURS = ("6時間前", 6, "時間前")
    TWELVE_HOURS = ("12時間前", 12, "時間前")
    ONE_DAY = ("1日前", 1, "日前")
    TWO_DAYS = ("2日前", 2, "日前")
    THREE_DAYS = ("3日前", 3, "日前")
    SEVEN_DAYS = ("7日前", 7, "日前")

    def to_payload(self, key: int) -> dict:
        """Convert to notification payload."""
        return {
            "key": key,
            "num": self.value[1],
            "type": self.value[2],
        }


class CreateCommand(commands.Cog):
    """Create command cog."""

    def __init__(self, bot: "DisCalendarBot"):
        self.bot = bot

    @app_commands.command(name="create", description="予定を新たに作成します")
    @app_commands.describe(
        name="予定の名称",
        description="予定の説明",
        start_year="予定開始時間(年)",
        start_month="予定開始時間(月)",
        start_day="予定開始時間(日)",
        start_hour="予定開始時間(時)",
        start_minute="予定開始時間(分)",
        end_year="予定終了時間(年)",
        end_month="予定終了時間(月)",
        end_day="予定終了時間(日)",
        end_hour="予定終了時間(時)",
        end_minute="予定終了時間(分)",
        is_all_day="終日行う予定か",
        color="予定の配色",
        notify_1="予定の事前通知",
        notify_2="予定の事前通知",
        notify_3="予定の事前通知",
        notify_4="予定の事前通知",
    )
    @app_commands.choices(
        color=[
            app_commands.Choice(name="白", value="white"),
            app_commands.Choice(name="黒", value="black"),
            app_commands.Choice(name="赤", value="red"),
            app_commands.Choice(name="青", value="blue"),
            app_commands.Choice(name="緑", value="green"),
            app_commands.Choice(name="黄", value="yellow"),
            app_commands.Choice(name="紫", value="purple"),
            app_commands.Choice(name="灰", value="gray"),
            app_commands.Choice(name="茶", value="brown"),
            app_commands.Choice(name="水色", value="aqua"),
        ],
        notify_1=[
            app_commands.Choice(name="5分前", value="5m"),
            app_commands.Choice(name="10分前", value="10m"),
            app_commands.Choice(name="15分前", value="15m"),
            app_commands.Choice(name="30分前", value="30m"),
            app_commands.Choice(name="1時間前", value="1h"),
            app_commands.Choice(name="2時間前", value="2h"),
            app_commands.Choice(name="3時間前", value="3h"),
            app_commands.Choice(name="6時間前", value="6h"),
            app_commands.Choice(name="12時間前", value="12h"),
            app_commands.Choice(name="1日前", value="1d"),
            app_commands.Choice(name="2日前", value="2d"),
            app_commands.Choice(name="3日前", value="3d"),
            app_commands.Choice(name="7日前", value="7d"),
        ],
        notify_2=[
            app_commands.Choice(name="5分前", value="5m"),
            app_commands.Choice(name="10分前", value="10m"),
            app_commands.Choice(name="15分前", value="15m"),
            app_commands.Choice(name="30分前", value="30m"),
            app_commands.Choice(name="1時間前", value="1h"),
            app_commands.Choice(name="2時間前", value="2h"),
            app_commands.Choice(name="3時間前", value="3h"),
            app_commands.Choice(name="6時間前", value="6h"),
            app_commands.Choice(name="12時間前", value="12h"),
            app_commands.Choice(name="1日前", value="1d"),
            app_commands.Choice(name="2日前", value="2d"),
            app_commands.Choice(name="3日前", value="3d"),
            app_commands.Choice(name="7日前", value="7d"),
        ],
        notify_3=[
            app_commands.Choice(name="5分前", value="5m"),
            app_commands.Choice(name="10分前", value="10m"),
            app_commands.Choice(name="15分前", value="15m"),
            app_commands.Choice(name="30分前", value="30m"),
            app_commands.Choice(name="1時間前", value="1h"),
            app_commands.Choice(name="2時間前", value="2h"),
            app_commands.Choice(name="3時間前", value="3h"),
            app_commands.Choice(name="6時間前", value="6h"),
            app_commands.Choice(name="12時間前", value="12h"),
            app_commands.Choice(name="1日前", value="1d"),
            app_commands.Choice(name="2日前", value="2d"),
            app_commands.Choice(name="3日前", value="3d"),
            app_commands.Choice(name="7日前", value="7d"),
        ],
        notify_4=[
            app_commands.Choice(name="5分前", value="5m"),
            app_commands.Choice(name="10分前", value="10m"),
            app_commands.Choice(name="15分前", value="15m"),
            app_commands.Choice(name="30分前", value="30m"),
            app_commands.Choice(name="1時間前", value="1h"),
            app_commands.Choice(name="2時間前", value="2h"),
            app_commands.Choice(name="3時間前", value="3h"),
            app_commands.Choice(name="6時間前", value="6h"),
            app_commands.Choice(name="12時間前", value="12h"),
            app_commands.Choice(name="1日前", value="1d"),
            app_commands.Choice(name="2日前", value="2d"),
            app_commands.Choice(name="3日前", value="3d"),
            app_commands.Choice(name="7日前", value="7d"),
        ],
    )
    async def create(
        self,
        interaction: discord.Interaction,
        name: str,
        start_year: int,
        start_month: int,
        start_day: int,
        start_hour: int,
        start_minute: int,
        end_year: int,
        end_month: int,
        end_day: int,
        end_hour: int,
        end_minute: int,
        description: str | None = None,
        is_all_day: bool = False,
        color: Literal[
            "white", "black", "red", "blue", "green", "yellow", "purple", "gray", "brown", "aqua"
        ] = "blue",
        notify_1: str | None = None,
        notify_2: str | None = None,
        notify_3: str | None = None,
        notify_4: str | None = None,
    ) -> None:
        """Create a new event."""
        if not interaction.guild:
            await interaction.response.send_message(
                "このコマンドはサーバーでのみ実行可能です", ephemeral=True
            )
            return

        guild_id = str(interaction.guild.id)

        # Check restrictions
        guild_config = await self.bot.guild_service.get_config(guild_id)
        if guild_config and guild_config.restricted:
            if isinstance(interaction.user, discord.Member):
                if not has_manage_permissions(interaction.user):
                    await interaction.response.send_message(
                        "このコマンドを実行するためには「管理者」「サーバー管理」"
                        "「ロールの管理」「メッセージの管理」のいずれかの権限が必要です",
                        ephemeral=True,
                    )
                    return

        # Validate dates
        if not validate_date(start_year, start_month, start_day, start_hour, start_minute):
            await interaction.response.send_message(
                f"無効な開始日時です: {start_year}/{start_month}/{start_day} "
                f"{start_hour}:{start_minute}",
                ephemeral=True,
            )
            return

        if not validate_date(end_year, end_month, end_day, end_hour, end_minute):
            await interaction.response.send_message(
                f"無効な終了日時です: {end_year}/{end_month}/{end_day} "
                f"{end_hour}:{end_minute}",
                ephemeral=True,
            )
            return

        # Create datetime objects
        try:
            start_at = datetime(
                start_year,
                start_month,
                start_day,
                start_hour,
                start_minute,
                tzinfo=UTC,
            )
            end_at = datetime(
                end_year, end_month, end_day, end_hour, end_minute, tzinfo=UTC
            )
        except ValueError as e:
            await interaction.response.send_message(f"日時の形式が無効です: {e}", ephemeral=True)
            return

        if start_at > end_at:
            await interaction.response.send_message(
                "開始時間が終了時間より後になっています", ephemeral=True
            )
            return

        # Parse color
        color_map = {
            "white": "#ffffff",
            "black": "#000000",
            "red": "#fd4028",
            "blue": "#3e44f7",
            "green": "#33f54b",
            "yellow": "#eaff33",
            "purple": "#a31ce0",
            "gray": "#808080",
            "brown": "#a54f4f",
            "aqua": "#44f3f3",
        }
        color_hex = color_map.get(color, "#3e44f7")

        # Parse notifications
        notifications = []
        notify_map = {
            "5m": (5, "分前"),
            "10m": (10, "分前"),
            "15m": (15, "分前"),
            "30m": (30, "分前"),
            "1h": (1, "時間前"),
            "2h": (2, "時間前"),
            "3h": (3, "時間前"),
            "6h": (6, "時間前"),
            "12h": (12, "時間前"),
            "1d": (1, "日前"),
            "2d": (2, "日前"),
            "3d": (3, "日前"),
            "7d": (7, "日前"),
        }

        for i, notify in enumerate([notify_1, notify_2, notify_3, notify_4]):
            if notify and notify in notify_map:
                num, ty = notify_map[notify]
                notifications.append({"key": i, "num": num, "type": ty})

        # Create event
        event_data = EventCreate(
            guild_id=guild_id,
            name=name,
            description=description,
            start_at=start_at,
            end_at=end_at,
            is_all_day=is_all_day,
            color=color_hex,
            notifications=notifications,
        )

        event = await self.bot.event_service.create(event_data)

        # Send response
        embed = create_event_embed(event)
        await interaction.response.send_message("正常に予定を作成しました", embed=embed)


async def setup(bot: "DisCalendarBot") -> None:
    """Setup function for loading the cog."""
    await bot.add_cog(CreateCommand(bot))
