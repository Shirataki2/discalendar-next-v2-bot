"""Tests for presence task."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.tasks.presence import PresenceState, PresenceTask


class TestPresenceState:
    """Tests for PresenceState."""

    def test_initial_state(self) -> None:
        """Test that initial state is correct."""
        state = PresenceState()
        assert state.current == "help"
        assert state.current_index == 0

    def test_next_cycles_through_states(self) -> None:
        """Test that next cycles through all states."""
        state = PresenceState()
        states = []
        for _ in range(len(state.STATES) + 1):
            states.append(state.current)
            state.next()

        assert states[0] == "help"
        assert states[1] == "slash_help"
        assert states[2] == "servers"
        assert states[3] == "url"
        assert states[4] == "help"  # Cycles back

    def test_current_property(self) -> None:
        """Test that current property returns correct state."""
        state = PresenceState()
        assert state.current == PresenceState.STATES[0]

        state.next()
        assert state.current == PresenceState.STATES[1]


class TestPresenceTask:
    """Tests for PresenceTask."""

    @pytest.mark.asyncio
    async def test_update_presence_help_state(self, mock_bot: MagicMock) -> None:
        """Test that _update_presence sets help activity."""
        cog = PresenceTask(mock_bot)
        cog.state.current_index = 0  # help state

        await cog._update_presence()

        mock_bot.change_presence.assert_called_once()
        call_kwargs = mock_bot.change_presence.call_args[1]
        assert call_kwargs["status"].value == "online"
        activity = call_kwargs["activity"]
        assert activity.type.value == 3  # watching
        assert activity.name == "cal help"

    @pytest.mark.asyncio
    async def test_update_presence_slash_help_state(self, mock_bot: MagicMock) -> None:
        """Test that _update_presence sets slash_help activity."""
        cog = PresenceTask(mock_bot)
        cog.state.current_index = 1  # slash_help state

        await cog._update_presence()

        call_kwargs = mock_bot.change_presence.call_args[1]
        activity = call_kwargs["activity"]
        assert activity.type.value == 3  # watching
        assert activity.name == "/help"

    @pytest.mark.asyncio
    async def test_update_presence_servers_state(self, mock_bot: MagicMock) -> None:
        """Test that _update_presence sets servers activity."""
        mock_bot.guilds = [MagicMock(), MagicMock(), MagicMock()]
        cog = PresenceTask(mock_bot)
        cog.state.current_index = 2  # servers state

        await cog._update_presence()

        call_kwargs = mock_bot.change_presence.call_args[1]
        activity = call_kwargs["activity"]
        assert activity.type.value == 3  # watching
        assert activity.name == "3 servers"

    @pytest.mark.asyncio
    async def test_update_presence_url_state(self, mock_bot: MagicMock) -> None:
        """Test that _update_presence sets url activity."""
        cog = PresenceTask(mock_bot)
        cog.state.current_index = 3  # url state

        await cog._update_presence()

        call_kwargs = mock_bot.change_presence.call_args[1]
        activity = call_kwargs["activity"]
        assert activity.type.value == 2  # listening
        assert activity.name == "discalendar.app"

    @pytest.mark.asyncio
    async def test_presence_loop_updates_and_cycles(self, mock_bot: MagicMock) -> None:
        """Test that presence_loop updates presence and cycles state."""
        cog = PresenceTask(mock_bot)
        initial_index = cog.state.current_index

        # Simulate one loop iteration
        await cog._update_presence()
        cog.state.next()

        assert cog.state.current_index == (initial_index + 1) % len(cog.state.STATES)
        mock_bot.change_presence.assert_called()
