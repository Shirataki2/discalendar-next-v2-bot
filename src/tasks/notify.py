"""Notification task for sending event reminders."""

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import discord
import structlog
from discord.ext import commands, tasks

from src.models import Event, NotificationPayload
from src.utils.embeds import create_notification_embed

if TYPE_CHECKING:
    from src.bot import DisCalendarBot

logger = structlog.get_logger()

# JST timezone
JST = timezone(timedelta(hours=9))


class NotifyTask(commands.Cog):
    """Cog for sending event notifications."""

    def __init__(self, bot: "DisCalendarBot"):
        self.bot = bot
        self.notify_loop.start()

    async def cog_unload(self) -> None:
        """Called when cog is unloaded."""
        self.notify_loop.cancel()

    @tasks.loop(seconds=60)
    async def notify_loop(self) -> None:
        """Check and send event notifications."""
        await self._process_notifications()

    @notify_loop.before_loop
    async def before_notify_loop(self) -> None:
        """Wait for bot to be ready before starting loop."""
        await self.bot.wait_until_ready()

    async def _process_notifications(self) -> None:
        """Process all pending notifications."""
        # Get current time in JST (zero out seconds)
        jst_now = datetime.now(JST).replace(second=0, microsecond=0)

        # Fetch all future events
        events = await self.bot.event_service.find_all_future_events(jst_now)
        logger.debug("Fetched events for notification", count=len(events))

        for event in events:
            await self._check_event_notifications(event, jst_now)

    async def _check_event_notifications(
        self, event: Event, jst_now: datetime
    ) -> None:
        """Check and send notifications for a single event."""
        # Get notification settings
        settings = await self.bot.event_service.get_settings(event.guild_id)
        if not settings:
            return

        # Get channel
        channel = self.bot.get_channel(int(settings.channel_id))
        if not channel or not isinstance(channel, discord.TextChannel):
            return

        # Build notification list (including "at event time" notification)
        notifications = list(event.notifications)
        notifications.append(NotificationPayload(key=-1, num=0, ty="分前"))
        notifications.sort(key=lambda n: n.key)

        # Determine start time (for all-day events, use midnight)
        if event.is_all_day:
            start = event.start_at.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=JST
            )
            end = event.end_at.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=JST
            )
        else:
            start = event.start_at.astimezone(JST)
            end = event.end_at.astimezone(JST)

        for notification in notifications:
            # Calculate notification time
            offset_minutes = notification.to_minutes()
            notify_time = start - timedelta(minutes=offset_minutes)

            # Check if this is within the current minute
            time_diff = jst_now - notify_time
            if timedelta(0) <= time_diff < timedelta(minutes=1):
                await self._send_notification(
                    channel, event, notification, start, end
                )

    async def _send_notification(
        self,
        channel: discord.TextChannel,
        event: Event,
        notification: NotificationPayload,
        start: datetime,
        end: datetime,
    ) -> None:
        """Send a notification message."""
        # Build notification label
        if notification.key == -1:
            label = "以下の予定が開催されます"
        else:
            time_label = notification.ty.replace("前", "後")
            label = f"{notification.num}{time_label}に以下の予定が開催されます"

        embed = create_notification_embed(event, label)

        try:
            await channel.send(embed=embed)
            logger.info(
                "Sent notification",
                event_name=event.name,
                guild_id=event.guild_id,
                notification=str(notification),
            )
        except discord.Forbidden:
            logger.warning(
                "Cannot send notification - no permission",
                channel_id=channel.id,
                guild_id=event.guild_id,
            )
        except discord.HTTPException as e:
            # Fallback to plain text if embed fails
            logger.warning("Embed failed, trying plain text", error=str(e))
            try:
                content = (
                    f"**🔔** {label}\n\n"
                    f"**{event.name}**\n"
                    f"{event.description or ''}\n\n"
                    f"**日時**: {start.strftime('%Y/%m/%d %H:%M')} - "
                    f"{end.strftime('%H:%M') if start.date() == end.date() else end.strftime('%Y/%m/%d %H:%M')}"
                )
                await channel.send(content)
            except Exception as e2:
                logger.error("Failed to send notification", error=str(e2))


async def setup(bot: "DisCalendarBot") -> None:
    """Setup function for loading the cog."""
    await bot.add_cog(NotifyTask(bot))
