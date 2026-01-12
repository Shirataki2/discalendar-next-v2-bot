"""Embed generation utilities."""

from datetime import datetime

import discord

from src import __version__
from src.models import Event
from src.utils.datetime import format_date, format_datetime


def create_help_embed(bot_avatar_url: str | None, invitation_url: str) -> discord.Embed:
    """Create help embed."""
    description = f"""DisCalendarはDiscord用の__予定管理Bot__です

ほとんどの操作は**Web上で行えることが特徴です！**

[**こちら**](https://discalendar.app)からログインして
サーバーのカレンダーを閲覧することができます

__**🌟初期化🌟**__
　この操作を行わなくても予定の追加はできますが
追加した予定の開始時間になった際にチャンネルに
投稿するようにするには初期化処理が必要です！

　このBotからメッセージを受信したいチャンネルで
```
/init
```
　と入力してください

　受信チャンネルを変更したい際には再度別のチャンネルで
このコマンドを実行して下さい

__**🌟コマンド機能🌟**__
　Discord上でも予定の表示と作成が行えます！
　詳しくは`/create`, `/list`と打ってみてください！

__**🌟サポートサーバー🌟**__
　機能要望やバグなどがあった場合には
[サポートサーバー](https://discord.gg/MyaZRuze23)へ参加し，ご連絡をお願いします！

__**🌟他のサーバーにも導入する場合🌟**__
　[こちら]({invitation_url})より導入をお願いします！"""

    embed = discord.Embed(
        title="DisCalendar - Help",
        description=description,
        color=0x0000DD,
        timestamp=datetime.utcnow(),
    )
    embed.set_footer(text=f"v{__version__}")
    if bot_avatar_url:
        embed.set_thumbnail(url=bot_avatar_url)

    return embed


def create_event_embed(event: Event) -> discord.Embed:
    """Create event embed."""
    color_int = int(event.color.lstrip("#"), 16)
    embed = discord.Embed(
        title=event.name,
        description=event.description or "",
        color=color_int,
    )

    if event.is_all_day:
        start_str = format_date(event.start_at)
        end_str = format_date(event.end_at)
    else:
        start_str = format_datetime(event.start_at)
        end_str = format_datetime(event.end_at)

    embed.add_field(name="開始時間", value=start_str, inline=True)
    embed.add_field(name="終了時間", value=end_str, inline=True)

    if event.notifications:
        notif_str = ", ".join(str(n) for n in event.notifications)
        embed.add_field(name="通知", value=notif_str, inline=True)

    embed.timestamp = datetime.utcnow()

    return embed


def create_error_embed(title: str, description: str) -> discord.Embed:
    """Create error embed."""
    return discord.Embed(
        title=f"❌ {title}",
        description=description,
        color=0xFF0000,
    )


def create_notification_embed(event: Event, notification_label: str) -> discord.Embed:
    """Create notification embed for event alerts."""
    color_int = int(event.color.lstrip("#"), 16)

    embed = discord.Embed(
        title=event.name,
        description=event.description or "",
        color=color_int,
    )
    embed.set_author(name=notification_label)

    if event.is_all_day:
        start_str = format_date(event.start_at)
        end_str = format_date(event.end_at)
        if start_str == end_str:
            date_str = start_str
        else:
            date_str = f"{start_str} - {end_str}"
    else:
        start_date = event.start_at.date()
        end_date = event.end_at.date()
        if start_date == end_date:
            date_str = f"{format_datetime(event.start_at)} - {event.end_at.strftime('%H:%M')}"
        else:
            date_str = f"{format_datetime(event.start_at)} - {format_datetime(event.end_at)}"

    embed.add_field(name="日時", value=date_str, inline=False)

    return embed
