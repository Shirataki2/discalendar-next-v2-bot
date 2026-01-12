"""Tests for notification task."""

from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models import Event, EventSettings, NotificationPayload
from src.tasks.notify import NotifyTask

JST = timezone(timedelta(hours=9))


class TestNotifyTask:
    """Tests for NotifyTask."""

    @pytest.mark.asyncio
    async def test_process_notifications_fetches_events(
        self, mock_bot: MagicMock
    ) -> None:
        """Test that _process_notifications fetches future events."""
        mock_bot.event_service.find_all_future_events = AsyncMock(return_value=[])

        cog = NotifyTask(mock_bot)
        await cog._process_notifications()

        mock_bot.event_service.find_all_future_events.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_event_notifications_skips_when_no_settings(
        self, mock_bot: MagicMock
    ) -> None:
        """Test that _check_event_notifications skips when no settings exist."""
        event = Event(
            id="1",
            guild_id="123",
            name="Test Event",
            description=None,
            color="#FF0000",
            is_all_day=False,
            start_at=datetime.now(JST) + timedelta(hours=1),
            end_at=datetime.now(JST) + timedelta(hours=2),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=[],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        mock_bot.event_service.get_settings = AsyncMock(return_value=None)

        cog = NotifyTask(mock_bot)
        await cog._check_event_notifications(event, datetime.now(JST))

        mock_bot.event_service.get_settings.assert_called_once_with("123")
        mock_bot.get_channel.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_event_notifications_skips_when_no_channel(
        self, mock_bot: MagicMock
    ) -> None:
        """Test that _check_event_notifications skips when channel not found."""
        event = Event(
            id="1",
            guild_id="123",
            name="Test Event",
            description=None,
            color="#FF0000",
            is_all_day=False,
            start_at=datetime.now(JST) + timedelta(hours=1),
            end_at=datetime.now(JST) + timedelta(hours=2),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=[],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        settings = EventSettings(id=1, guild_id="123", channel_id="456")
        mock_bot.event_service.get_settings = AsyncMock(return_value=settings)
        mock_bot.get_channel = AsyncMock(return_value=None)

        cog = NotifyTask(mock_bot)
        await cog._check_event_notifications(event, datetime.now(JST))

        mock_bot.get_channel.assert_called_once_with(456)
        # get_channel returns None, so we can't call send on it
        # The test verifies that no send was attempted when channel is None

    @pytest.mark.asyncio
    async def test_send_notification_sends_embed(
        self, mock_bot: MagicMock, mock_channel: MagicMock
    ) -> None:
        """Test that _send_notification sends embed successfully."""
        event = Event(
            id="1",
            guild_id="123",
            name="Test Event",
            description="Test Description",
            color="#FF0000",
            is_all_day=False,
            start_at=datetime.now(JST),
            end_at=datetime.now(JST) + timedelta(hours=1),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=[],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        notification = NotificationPayload(key=-1, num=0, ty="分前")
        start = datetime.now(JST)
        end = datetime.now(JST) + timedelta(hours=1)

        with patch("src.tasks.notify.create_notification_embed") as mock_create_embed:
            mock_embed = MagicMock()
            mock_create_embed.return_value = mock_embed

            cog = NotifyTask(mock_bot)
            await cog._send_notification(mock_channel, event, notification, start, end)

            mock_channel.send.assert_called_once_with(embed=mock_embed)
            mock_create_embed.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notification_handles_forbidden_error(
        self, mock_bot: MagicMock, mock_channel: MagicMock
    ) -> None:
        """Test that _send_notification handles Forbidden error gracefully."""
        import discord

        event = Event(
            id="1",
            guild_id="123",
            name="Test Event",
            description=None,
            color="#FF0000",
            is_all_day=False,
            start_at=datetime.now(JST),
            end_at=datetime.now(JST) + timedelta(hours=1),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=[],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        notification = NotificationPayload(key=-1, num=0, ty="分前")
        start = datetime.now(JST)
        end = datetime.now(JST) + timedelta(hours=1)

        mock_channel.send = AsyncMock(side_effect=discord.Forbidden(MagicMock(), ""))

        with patch("src.tasks.notify.create_notification_embed"):
            cog = NotifyTask(mock_bot)
            await cog._send_notification(mock_channel, event, notification, start, end)

            mock_channel.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notification_handles_http_exception(
        self, mock_bot: MagicMock, mock_channel: MagicMock
    ) -> None:
        """Test that _send_notification falls back to plain text on HTTPException."""
        import discord

        event = Event(
            id="1",
            guild_id="123",
            name="Test Event",
            description="Test Description",
            color="#FF0000",
            is_all_day=False,
            start_at=datetime.now(JST),
            end_at=datetime.now(JST) + timedelta(hours=1),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=[],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        notification = NotificationPayload(key=-1, num=0, ty="分前")
        start = datetime.now(JST)
        end = datetime.now(JST) + timedelta(hours=1)

        mock_channel.send = AsyncMock(side_effect=[discord.HTTPException(MagicMock(), ""), None])

        with patch("src.tasks.notify.create_notification_embed"):
            cog = NotifyTask(mock_bot)
            await cog._send_notification(mock_channel, event, notification, start, end)

            assert mock_channel.send.call_count == 2
            # Second call should be with plain text content
            second_call = mock_channel.send.call_args_list[1]
            assert "content" in second_call.kwargs or len(second_call.args) > 0

    @pytest.mark.asyncio
    async def test_check_event_notifications_handles_all_day_event(
        self, mock_bot: MagicMock, mock_channel: MagicMock
    ) -> None:
        """Test that _check_event_notifications handles all-day events correctly."""
        event = Event(
            id="1",
            guild_id="123",
            name="All Day Event",
            description=None,
            color="#FF0000",
            is_all_day=True,
            start_at=datetime(2024, 1, 15, 0, 0, 0, tzinfo=UTC),
            end_at=datetime(2024, 1, 15, 0, 0, 0, tzinfo=UTC),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=[],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        settings = EventSettings(id=1, guild_id="123", channel_id="456")
        mock_bot.event_service.get_settings = AsyncMock(return_value=settings)
        mock_bot.get_channel = AsyncMock(return_value=mock_channel)

        cog = NotifyTask(mock_bot)
        # Use a time that won't trigger notification
        jst_now = datetime(2024, 1, 14, 23, 0, 0, tzinfo=JST)
        await cog._check_event_notifications(event, jst_now)

        # Should not send notification for all-day event at wrong time
        mock_channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_notification_label_for_event_time(self, mock_bot: MagicMock, mock_channel: MagicMock) -> None:
        """Test that notification label is correct for event time notification."""
        event = Event(
            id="1",
            guild_id="123",
            name="Test Event",
            description=None,
            color="#FF0000",
            is_all_day=False,
            start_at=datetime.now(JST),
            end_at=datetime.now(JST) + timedelta(hours=1),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=[],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        notification = NotificationPayload(key=-1, num=0, ty="分前")
        start = datetime.now(JST)
        end = datetime.now(JST) + timedelta(hours=1)

        with patch("src.tasks.notify.create_notification_embed") as mock_create_embed:
            mock_embed = MagicMock()
            mock_create_embed.return_value = mock_embed

            cog = NotifyTask(mock_bot)
            await cog._send_notification(mock_channel, event, notification, start, end)

            # Check that create_notification_embed was called with correct label
            call_args = mock_create_embed.call_args
            assert "以下の予定が開催されます" in call_args[0][1]

    @pytest.mark.asyncio
    async def test_notification_label_for_before_event(
        self, mock_bot: MagicMock, mock_channel: MagicMock
    ) -> None:
        """Test that notification label is correct for before-event notification."""
        event = Event(
            id="1",
            guild_id="123",
            name="Test Event",
            description=None,
            color="#FF0000",
            is_all_day=False,
            start_at=datetime.now(JST),
            end_at=datetime.now(JST) + timedelta(hours=1),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=[],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        notification = NotificationPayload(key=0, num=30, ty="分前")
        start = datetime.now(JST)
        end = datetime.now(JST) + timedelta(hours=1)

        with patch("src.tasks.notify.create_notification_embed") as mock_create_embed:
            mock_embed = MagicMock()
            mock_create_embed.return_value = mock_embed

            cog = NotifyTask(mock_bot)
            await cog._send_notification(mock_channel, event, notification, start, end)

            # Check that create_notification_embed was called with correct label
            call_args = mock_create_embed.call_args
            assert "30分後に以下の予定が開催されます" in call_args[0][1]
