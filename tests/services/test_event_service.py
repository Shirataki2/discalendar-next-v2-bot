"""Tests for EventService."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from src.models import Event, EventCreate, EventSettings, NotificationPayload
from src.services import EventService


class TestEventServiceFindByGuildId:
    """Tests for EventService.find_by_guild_id method."""

    @pytest.mark.asyncio
    async def test_returns_events_for_future_range(self) -> None:
        """Test that find_by_guild_id returns future events with range_type='future'."""
        mock_supabase = MagicMock()
        service = EventService(mock_supabase)

        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "1",
                "guild_id": "123",
                "name": "Future Event",
                "description": None,
                "color": "#FF0000",
                "is_all_day": False,
                "start_at": "2024-12-31T10:00:00Z",
                "end_at": "2024-12-31T12:00:00Z",
                "location": None,
                "channel_id": None,
                "channel_name": None,
                "notifications": [],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        ]

        mock_query = MagicMock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.gte.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        events = await service.find_by_guild_id("123", "future")

        assert len(events) == 1
        assert events[0].name == "Future Event"
        mock_query.gte.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_events_for_past_range(self) -> None:
        """Test that find_by_guild_id returns past events with range_type='past'."""
        mock_supabase = MagicMock()
        service = EventService(mock_supabase)

        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "2",
                "guild_id": "123",
                "name": "Past Event",
                "description": None,
                "color": "#0000FF",
                "is_all_day": False,
                "start_at": "2023-01-01T10:00:00Z",
                "end_at": "2023-01-01T12:00:00Z",
                "location": None,
                "channel_id": None,
                "channel_name": None,
                "notifications": [],
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
            }
        ]

        mock_query = MagicMock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.lt.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        events = await service.find_by_guild_id("123", "past")

        assert len(events) == 1
        assert events[0].name == "Past Event"
        mock_query.lt.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_all_events_for_all_range(self) -> None:
        """Test that find_by_guild_id returns all events with range_type='all'."""
        mock_supabase = MagicMock()
        service = EventService(mock_supabase)

        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "1",
                "guild_id": "123",
                "name": "Event 1",
                "description": None,
                "color": "#FF0000",
                "is_all_day": False,
                "start_at": "2024-12-31T10:00:00Z",
                "end_at": "2024-12-31T12:00:00Z",
                "location": None,
                "channel_id": None,
                "channel_name": None,
                "notifications": [],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": "2",
                "guild_id": "123",
                "name": "Event 2",
                "description": None,
                "color": "#0000FF",
                "is_all_day": False,
                "start_at": "2023-01-01T10:00:00Z",
                "end_at": "2023-01-01T12:00:00Z",
                "location": None,
                "channel_id": None,
                "channel_name": None,
                "notifications": [],
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
            },
        ]

        mock_query = MagicMock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        events = await service.find_by_guild_id("123", "all")

        assert len(events) == 2
        # Should not call gte or lt for "all"
        assert not hasattr(mock_query, "gte") or not mock_query.gte.called
        assert not hasattr(mock_query, "lt") or not mock_query.lt.called

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_events(self) -> None:
        """Test that find_by_guild_id returns empty list when no events found."""
        mock_supabase = MagicMock()
        service = EventService(mock_supabase)

        mock_response = MagicMock()
        mock_response.data = []

        mock_query = MagicMock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.gte.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        events = await service.find_by_guild_id("123", "future")

        assert events == []


class TestEventServiceFindAllFutureEvents:
    """Tests for EventService.find_all_future_events method."""

    @pytest.mark.asyncio
    async def test_returns_future_events_across_all_guilds(self) -> None:
        """Test that find_all_future_events returns future events from all guilds."""
        mock_supabase = MagicMock()
        service = EventService(mock_supabase)

        from_time = datetime(2024, 6, 1, 0, 0, 0, tzinfo=UTC)

        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "1",
                "guild_id": "123",
                "name": "Event 1",
                "description": None,
                "color": "#FF0000",
                "is_all_day": False,
                "start_at": "2024-07-01T10:00:00Z",
                "end_at": "2024-07-01T12:00:00Z",
                "location": None,
                "channel_id": None,
                "channel_name": None,
                "notifications": [],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": "2",
                "guild_id": "456",
                "name": "Event 2",
                "description": None,
                "color": "#0000FF",
                "is_all_day": False,
                "start_at": "2024-08-01T10:00:00Z",
                "end_at": "2024-08-01T12:00:00Z",
                "location": None,
                "channel_id": None,
                "channel_name": None,
                "notifications": [],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        ]

        mock_query = MagicMock()
        mock_query.select.return_value = mock_query
        mock_query.gte.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        events = await service.find_all_future_events(from_time)

        assert len(events) == 2
        mock_query.gte.assert_called_once_with("start_at", from_time.isoformat())


class TestEventServiceCreate:
    """Tests for EventService.create method."""

    @pytest.mark.asyncio
    async def test_creates_event_successfully(self) -> None:
        """Test that create creates an event successfully."""
        mock_supabase = MagicMock()
        service = EventService(mock_supabase)

        event_data = EventCreate(
            guild_id="123",
            name="New Event",
            description="Test Description",
            start_at=datetime(2024, 12, 31, 10, 0, 0, tzinfo=UTC),
            end_at=datetime(2024, 12, 31, 12, 0, 0, tzinfo=UTC),
            color="#FF0000",
            is_all_day=False,
            notifications=[{"key": 0, "num": 30, "type": "分前"}],
        )

        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "1",
                "guild_id": "123",
                "name": "New Event",
                "description": "Test Description",
                "color": "#FF0000",
                "is_all_day": False,
                "start_at": "2024-12-31T10:00:00Z",
                "end_at": "2024-12-31T12:00:00Z",
                "location": None,
                "channel_id": None,
                "channel_name": None,
                "notifications": [{"key": 0, "num": 30, "type": "分前"}],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        ]

        mock_query = MagicMock()
        mock_query.insert.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        event = await service.create(event_data)

        assert event.name == "New Event"
        assert event.guild_id == "123"
        mock_query.insert.assert_called_once_with(event_data.to_dict())


class TestEventServiceGetSettings:
    """Tests for EventService.get_settings method."""

    @pytest.mark.asyncio
    async def test_returns_settings_when_exists(self) -> None:
        """Test that get_settings returns settings when they exist."""
        mock_supabase = MagicMock()
        service = EventService(mock_supabase)

        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "guild_id": "123", "channel_id": "456"}]

        mock_query = MagicMock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        settings = await service.get_settings("123")

        assert settings is not None
        assert settings.guild_id == "123"
        assert settings.channel_id == "456"

    @pytest.mark.asyncio
    async def test_returns_none_when_not_exists(self) -> None:
        """Test that get_settings returns None when settings don't exist."""
        mock_supabase = MagicMock()
        service = EventService(mock_supabase)

        mock_response = MagicMock()
        mock_response.data = []

        mock_query = MagicMock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        settings = await service.get_settings("123")

        assert settings is None


class TestEventServiceCreateSettings:
    """Tests for EventService.create_settings method."""

    @pytest.mark.asyncio
    async def test_creates_settings_successfully(self) -> None:
        """Test that create_settings creates settings successfully."""
        mock_supabase = MagicMock()
        service = EventService(mock_supabase)

        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "guild_id": "123", "channel_id": "789"}]

        mock_query = MagicMock()
        mock_query.insert.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        settings = await service.create_settings("123", "789")

        assert settings.guild_id == "123"
        assert settings.channel_id == "789"
        mock_query.insert.assert_called_once_with({"guild_id": "123", "channel_id": "789"})


class TestEventServiceUpdateSettings:
    """Tests for EventService.update_settings method."""

    @pytest.mark.asyncio
    async def test_updates_settings_successfully(self) -> None:
        """Test that update_settings updates settings successfully."""
        mock_supabase = MagicMock()
        service = EventService(mock_supabase)

        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "guild_id": "123", "channel_id": "999"}]

        mock_query = MagicMock()
        mock_query.update.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        settings = await service.update_settings("123", "999")

        assert settings.guild_id == "123"
        assert settings.channel_id == "999"
        mock_query.update.assert_called_once_with({"channel_id": "999"})
        mock_query.eq.assert_called_once_with("guild_id", "123")
