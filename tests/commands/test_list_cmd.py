"""Tests for list command."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.commands.list_cmd import EventListView, ListCommand
from src.models import Event


@pytest.fixture
def sample_events() -> list[Event]:
    """Create sample events for testing."""
    return [
        Event(
            id="1",
            guild_id="123",
            name="Event 1",
            description="Description 1",
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
        ),
        Event(
            id="2",
            guild_id="123",
            name="Event 2",
            description="Description 2",
            color="#0000FF",
            is_all_day=False,
            start_at=datetime(2024, 1, 16, 14, 0, 0, tzinfo=UTC),
            end_at=datetime(2024, 1, 16, 16, 0, 0, tzinfo=UTC),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=[],
            created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
            updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
        ),
        Event(
            id="3",
            guild_id="123",
            name="Event 3",
            description="Description 3",
            color="#00FF00",
            is_all_day=False,
            start_at=datetime(2024, 1, 17, 9, 0, 0, tzinfo=UTC),
            end_at=datetime(2024, 1, 17, 11, 0, 0, tzinfo=UTC),
            location=None,
            channel_id=None,
            channel_name=None,
            notifications=[],
            created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
            updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
        ),
    ]


class TestListCommand:
    """Tests for ListCommand."""

    @pytest.mark.asyncio
    async def test_list_events_future(
        self, mock_bot: MagicMock, mock_interaction: MagicMock, sample_events: list[Event]
    ) -> None:
        """Test that list command displays future events."""
        mock_bot.event_service.find_by_guild_id = AsyncMock(return_value=sample_events)

        cog = ListCommand(mock_bot)
        await cog.list_events.callback(cog, mock_interaction, range="future")  # type: ignore[misc]

        mock_bot.event_service.find_by_guild_id.assert_called_once_with("987654321", "future")
        mock_interaction.response.send_message.assert_called_once()
        call_kwargs = mock_interaction.response.send_message.call_args[1]
        assert "embed" in call_kwargs
        assert "view" in call_kwargs

    @pytest.mark.asyncio
    async def test_list_events_past(
        self, mock_bot: MagicMock, mock_interaction: MagicMock
    ) -> None:
        """Test that list command displays past events."""
        past_events = [
            Event(
                id="1",
                guild_id="123",
                name="Past Event",
                description=None,
                color="#FF0000",
                is_all_day=False,
                start_at=datetime(2023, 1, 1, 10, 0, 0, tzinfo=UTC),
                end_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC),
                location=None,
                channel_id=None,
                channel_name=None,
                notifications=[],
                created_at=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                updated_at=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            )
        ]
        mock_bot.event_service.find_by_guild_id = AsyncMock(return_value=past_events)

        cog = ListCommand(mock_bot)
        await cog.list_events.callback(cog, mock_interaction, range="past")  # type: ignore[misc]

        mock_bot.event_service.find_by_guild_id.assert_called_once_with("987654321", "past")

    @pytest.mark.asyncio
    async def test_list_events_all(
        self, mock_bot: MagicMock, mock_interaction: MagicMock, sample_events: list[Event]
    ) -> None:
        """Test that list command displays all events."""
        mock_bot.event_service.find_by_guild_id = AsyncMock(return_value=sample_events)

        cog = ListCommand(mock_bot)
        await cog.list_events.callback(cog, mock_interaction, range="all")  # type: ignore[misc]

        mock_bot.event_service.find_by_guild_id.assert_called_once_with("987654321", "all")

    @pytest.mark.asyncio
    async def test_list_events_no_events(
        self, mock_bot: MagicMock, mock_interaction: MagicMock
    ) -> None:
        """Test that list command handles no events."""
        mock_bot.event_service.find_by_guild_id = AsyncMock(return_value=[])

        cog = ListCommand(mock_bot)
        await cog.list_events.callback(cog, mock_interaction)  # type: ignore[misc]

        mock_interaction.response.send_message.assert_called_once_with(
            "現在登録されている予定はありません", ephemeral=True
        )

    @pytest.mark.asyncio
    async def test_list_events_without_guild(
        self, mock_bot: MagicMock, mock_interaction: MagicMock
    ) -> None:
        """Test that list command fails when not in a guild."""
        mock_interaction.guild = None

        cog = ListCommand(mock_bot)
        await cog.list_events.callback(cog, mock_interaction)  # type: ignore[misc]

        mock_interaction.response.send_message.assert_called_once_with(
            "このコマンドはサーバーでのみ実行可能です", ephemeral=True
        )
        mock_bot.event_service.find_by_guild_id.assert_not_called()


class TestEventListView:
    """Tests for EventListView."""

    @pytest.mark.asyncio
    async def test_initializes_correctly(self, sample_events: list[Event]) -> None:
        """Test that EventListView initializes correctly."""
        view = EventListView(sample_events, per_page=2)

        assert view.current_page == 0
        assert view.max_pages == 2
        assert len(view.events) == 3
        assert view.prev_button.disabled is True  # First page, prev disabled
        assert view.next_button.disabled is False  # Not last page, next enabled

    @pytest.mark.asyncio
    async def test_get_embed_first_page(self, sample_events: list[Event]) -> None:
        """Test that get_embed returns correct embed for first page."""
        view = EventListView(sample_events, per_page=2)

        embed = view.get_embed()

        assert embed.title == "予定一覧"
        assert len(embed.fields) == 2  # First 2 events
        assert embed.fields[0].name == "Event 1"
        assert embed.fields[1].name == "Event 2"
        assert embed.footer is not None
        assert embed.footer.text == "ページ 1/2"

    @pytest.mark.asyncio
    async def test_get_embed_second_page(self, sample_events: list[Event]) -> None:
        """Test that get_embed returns correct embed for second page."""
        view = EventListView(sample_events, per_page=2)
        view.current_page = 1

        embed = view.get_embed()

        assert len(embed.fields) == 1  # Last event
        assert embed.fields[0].name == "Event 3"
        assert embed.footer is not None
        assert embed.footer.text == "ページ 2/2"

    @pytest.mark.asyncio
    async def test_button_states_first_page(self, sample_events: list[Event]) -> None:
        """Test button states on first page."""
        view = EventListView(sample_events, per_page=2)

        assert view.prev_button.disabled is True
        assert view.next_button.disabled is False

    @pytest.mark.asyncio
    async def test_button_states_middle_page(self, sample_events: list[Event]) -> None:
        """Test button states on middle page."""
        view = EventListView(sample_events, per_page=1)
        view.current_page = 1
        view._update_buttons()

        assert view.prev_button.disabled is False
        assert view.next_button.disabled is False

    @pytest.mark.asyncio
    async def test_button_states_last_page(self, sample_events: list[Event]) -> None:
        """Test button states on last page."""
        view = EventListView(sample_events, per_page=2)
        view.current_page = 1
        view._update_buttons()

        assert view.prev_button.disabled is False
        assert view.next_button.disabled is True

    @pytest.mark.asyncio
    async def test_prev_button_navigation(self, sample_events: list[Event]) -> None:
        """Test that prev button navigates to previous page."""
        view = EventListView(sample_events, per_page=2)
        view.current_page = 1

        mock_interaction = MagicMock()
        mock_interaction.response.edit_message = AsyncMock()

        await view.prev_button.callback(mock_interaction)  # type: ignore[misc]

        assert view.current_page == 0
        assert view.prev_button.disabled is True
        mock_interaction.response.edit_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_next_button_navigation(self, sample_events: list[Event]) -> None:
        """Test that next button navigates to next page."""
        view = EventListView(sample_events, per_page=2)
        view.current_page = 0

        mock_interaction = MagicMock()
        mock_interaction.response.edit_message = AsyncMock()

        await view.next_button.callback(mock_interaction)  # type: ignore[misc]

        assert view.current_page == 1
        assert view.next_button.disabled is True
        mock_interaction.response.edit_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_embed_includes_notifications(self) -> None:
        """Test that embed includes notification information."""
        events_with_notifications = [
            Event(
                id="1",
                guild_id="123",
                name="Event with Notifications",
                description=None,
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
        ]

        view = EventListView(events_with_notifications)
        embed = view.get_embed()

        assert embed.fields[0].value is not None
        assert "通知" in embed.fields[0].value

