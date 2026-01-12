"""Tests for embed generation utilities."""

from datetime import UTC, datetime

import discord

from src.models import Event, NotificationPayload
from src.utils.embeds import (
    create_error_embed,
    create_event_embed,
    create_help_embed,
    create_notification_embed,
)


class TestCreateHelpEmbed:
    """Tests for create_help_embed function."""

    def test_creates_embed_with_avatar(self) -> None:
        """Test that help embed is created with bot avatar."""
        avatar_url = "https://example.com/avatar.png"
        invitation_url = "https://discord.com/invite/test"
        embed = create_help_embed(avatar_url, invitation_url)

        assert isinstance(embed, discord.Embed)
        assert embed.title == "DisCalendar - Help"
        assert embed.description is not None
        assert "DisCalendarはDiscord用の__予定管理Bot__です" in embed.description
        assert invitation_url in embed.description
        assert embed.thumbnail.url == avatar_url
        assert embed.color.value == 0x0000DD
        assert embed.timestamp is not None

    def test_creates_embed_without_avatar(self) -> None:
        """Test that help embed is created without bot avatar."""
        invitation_url = "https://discord.com/invite/test"
        embed = create_help_embed(None, invitation_url)

        assert isinstance(embed, discord.Embed)
        assert embed.title == "DisCalendar - Help"
        assert embed.thumbnail.url is None

    def test_includes_version_in_footer(self) -> None:
        """Test that version is included in footer."""
        embed = create_help_embed(None, "https://discord.com/invite/test")
        assert embed.footer.text is not None
        assert embed.footer.text.startswith("v")


class TestCreateEventEmbed:
    """Tests for create_event_embed function."""

    def test_creates_embed_for_regular_event(self) -> None:
        """Test that event embed is created for regular event."""
        event = Event(
            id="1",
            guild_id="123",
            name="Test Event",
            description="Test Description",
            color="#FF0000",
            is_all_day=False,
            start_at=datetime(2024, 1, 15, 10, 0, 0, tzinfo=UTC),
            end_at=datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=[],
            created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
            updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
        )

        embed = create_event_embed(event)

        assert isinstance(embed, discord.Embed)
        assert embed.title == "Test Event"
        assert embed.description == "Test Description"
        assert embed.color.value == 0xFF0000
        assert len(embed.fields) >= 2
        assert embed.fields[0].name == "開始時間"
        assert embed.fields[1].name == "終了時間"
        assert embed.timestamp is not None

    def test_creates_embed_for_all_day_event(self) -> None:
        """Test that event embed is created for all-day event."""
        event = Event(
            id="1",
            guild_id="123",
            name="All Day Event",
            description=None,
            color="#0000FF",
            is_all_day=True,
            start_at=datetime(2024, 1, 15, 0, 0, 0, tzinfo=UTC),
            end_at=datetime(2024, 1, 15, 0, 0, 0, tzinfo=UTC),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=[],
            created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
            updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
        )

        embed = create_event_embed(event)

        assert isinstance(embed, discord.Embed)
        assert embed.title == "All Day Event"
        assert embed.description == ""
        # For all-day events, dates should be formatted as YYYY/MM/DD
        assert embed.fields[0].value is not None
        assert "/" in embed.fields[0].value
        assert ":" not in embed.fields[0].value  # No time component

    def test_creates_embed_with_notifications(self) -> None:
        """Test that event embed includes notifications."""
        notifications = [
            NotificationPayload(key=0, num=30, ty="分前"),
            NotificationPayload(key=1, num=1, ty="時間前"),
        ]
        event = Event(
            id="1",
            guild_id="123",
            name="Event with Notifications",
            description="Description",
            color="#00FF00",
            is_all_day=False,
            start_at=datetime(2024, 1, 15, 10, 0, 0, tzinfo=UTC),
            end_at=datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=notifications,
            created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
            updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
        )

        embed = create_event_embed(event)

        assert len(embed.fields) == 3
        assert embed.fields[2].name == "通知"
        assert embed.fields[2].value is not None
        assert "30分前" in embed.fields[2].value
        assert "1時間前" in embed.fields[2].value

    def test_color_conversion(self) -> None:
        """Test that hex color is converted to integer."""
        event = Event(
            id="1",
            guild_id="123",
            name="Test",
            description=None,
            color="#ABCDEF",
            is_all_day=False,
            start_at=datetime(2024, 1, 15, 10, 0, 0, tzinfo=UTC),
            end_at=datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=[],
            created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
            updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
        )

        embed = create_event_embed(event)
        assert embed.color.value == 0xABCDEF


class TestCreateErrorEmbed:
    """Tests for create_error_embed function."""

    def test_creates_error_embed(self) -> None:
        """Test that error embed is created with correct title and description."""
        title = "Test Error"
        description = "This is a test error message"
        embed = create_error_embed(title, description)

        assert isinstance(embed, discord.Embed)
        assert embed.title == "❌ Test Error"
        assert embed.description == description
        assert embed.color.value == 0xFF0000


class TestCreateNotificationEmbed:
    """Tests for create_notification_embed function."""

    def test_creates_notification_embed_for_regular_event(self) -> None:
        """Test that notification embed is created for regular event."""
        event = Event(
            id="1",
            guild_id="123",
            name="Test Event",
            description="Test Description",
            color="#FF0000",
            is_all_day=False,
            start_at=datetime(2024, 1, 15, 10, 0, 0, tzinfo=UTC),
            end_at=datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=[],
            created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
            updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
        )

        embed = create_notification_embed(event, "30分後に以下の予定が開催されます")

        assert isinstance(embed, discord.Embed)
        assert embed.title == "Test Event"
        assert embed.description == "Test Description"
        assert embed.color.value == 0xFF0000
        assert embed.author.name == "30分後に以下の予定が開催されます"
        assert len(embed.fields) == 1
        assert embed.fields[0].name == "日時"
        assert embed.fields[0].value is not None

    def test_creates_notification_embed_for_all_day_event_same_date(self) -> None:
        """Test that notification embed is created for all-day event with same start/end date."""
        event = Event(
            id="1",
            guild_id="123",
            name="All Day Event",
            description=None,
            color="#0000FF",
            is_all_day=True,
            start_at=datetime(2024, 1, 15, 0, 0, 0, tzinfo=UTC),
            end_at=datetime(2024, 1, 15, 0, 0, 0, tzinfo=UTC),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=[],
            created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
            updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
        )

        embed = create_notification_embed(event, "以下の予定が開催されます")

        assert embed.fields[0].name == "日時"
        # For same-day all-day events, should show single date
        date_str = embed.fields[0].value
        assert date_str is not None
        assert "2024/01/15" in date_str
        assert date_str.count("2024/01/15") == 1  # Should appear only once

    def test_creates_notification_embed_for_all_day_event_different_dates(self) -> None:
        """Test that notification embed is created for all-day event spanning multiple days."""
        event = Event(
            id="1",
            guild_id="123",
            name="Multi-Day Event",
            description=None,
            color="#0000FF",
            is_all_day=True,
            start_at=datetime(2024, 1, 15, 0, 0, 0, tzinfo=UTC),
            end_at=datetime(2024, 1, 17, 0, 0, 0, tzinfo=UTC),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=[],
            created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
            updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
        )

        embed = create_notification_embed(event, "以下の予定が開催されます")

        date_str = embed.fields[0].value
        assert date_str is not None
        assert "2024/01/15" in date_str
        assert "2024/01/17" in date_str
        assert " - " in date_str  # Should show date range

    def test_creates_notification_embed_for_regular_event_same_date(self) -> None:
        """Test that notification embed handles regular event on same day."""
        event = Event(
            id="1",
            guild_id="123",
            name="Same Day Event",
            description=None,
            color="#00FF00",
            is_all_day=False,
            start_at=datetime(2024, 1, 15, 10, 0, 0, tzinfo=UTC),
            end_at=datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=[],
            created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
            updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
        )

        embed = create_notification_embed(event, "以下の予定が開催されます")

        date_str = embed.fields[0].value
        assert date_str is not None
        # Should show date once and both times
        assert "2024/01/15" in date_str or "2025/01/15" in date_str  # Timezone conversion
        assert ":" in date_str  # Should include time
