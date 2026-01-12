"""Tests for guild event handlers."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.events.guild import GuildEvents
from src.models import Guild, GuildCreate


class TestGuildEvents:
    """Tests for GuildEvents."""

    @pytest.mark.asyncio
    async def test_on_guild_join_creates_new_guild(
        self, mock_bot: MagicMock, mock_guild: MagicMock
    ) -> None:
        """Test that on_guild_join creates a new guild when it doesn't exist."""
        mock_bot.guild_service.find_by_guild_id = AsyncMock(return_value=None)
        mock_bot.guild_service.create = AsyncMock(
            return_value=Guild(
                id=1,
                guild_id="987654321",
                name="Test Guild",
                avatar_url="https://example.com/guild_icon.png",
                locale="ja",
            )
        )

        cog = GuildEvents(mock_bot)
        await cog.on_guild_join(mock_guild)

        mock_bot.guild_service.find_by_guild_id.assert_called_once_with("987654321")
        mock_bot.guild_service.create.assert_called_once()
        create_call_args = mock_bot.guild_service.create.call_args[0][0]
        assert isinstance(create_call_args, GuildCreate)
        assert create_call_args.guild_id == "987654321"
        assert create_call_args.name == "Test Guild"
        assert create_call_args.avatar_url == "https://example.com/guild_icon.png"

    @pytest.mark.asyncio
    async def test_on_guild_join_skips_existing_guild(
        self, mock_bot: MagicMock, mock_guild: MagicMock
    ) -> None:
        """Test that on_guild_join skips creation when guild already exists."""
        existing_guild = Guild(
            id=1,
            guild_id="987654321",
            name="Existing Guild",
            avatar_url=None,
            locale="ja",
        )
        mock_bot.guild_service.find_by_guild_id = AsyncMock(return_value=existing_guild)

        cog = GuildEvents(mock_bot)
        await cog.on_guild_join(mock_guild)

        mock_bot.guild_service.find_by_guild_id.assert_called_once_with("987654321")
        mock_bot.guild_service.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_guild_join_without_icon(
        self, mock_bot: MagicMock, mock_guild: MagicMock
    ) -> None:
        """Test that on_guild_join handles guild without icon."""
        mock_guild.icon = None
        mock_bot.guild_service.find_by_guild_id = AsyncMock(return_value=None)
        mock_bot.guild_service.create = AsyncMock(
            return_value=Guild(
                id=1, guild_id="987654321", name="Test Guild", avatar_url=None, locale="ja"
            )
        )

        cog = GuildEvents(mock_bot)
        await cog.on_guild_join(mock_guild)

        create_call_args = mock_bot.guild_service.create.call_args[0][0]
        assert create_call_args.avatar_url is None

    @pytest.mark.asyncio
    async def test_on_guild_remove_deletes_guild(
        self, mock_bot: MagicMock, mock_guild: MagicMock
    ) -> None:
        """Test that on_guild_remove deletes the guild."""
        mock_bot.guild_service.delete = AsyncMock()

        cog = GuildEvents(mock_bot)
        await cog.on_guild_remove(mock_guild)

        mock_bot.guild_service.delete.assert_called_once_with("987654321")

    @pytest.mark.asyncio
    async def test_on_guild_update_updates_name(
        self, mock_bot: MagicMock, mock_guild: MagicMock
    ) -> None:
        """Test that on_guild_update updates guild when name changes."""
        before_guild = MagicMock()
        before_guild.id = 987654321
        before_guild.name = "Old Name"
        before_guild.icon = None

        after_guild = MagicMock()
        after_guild.id = 987654321
        after_guild.name = "New Name"
        after_guild.icon = None

        mock_bot.guild_service.update = AsyncMock(
            return_value=Guild(
                id=1, guild_id="987654321", name="New Name", avatar_url=None, locale="ja"
            )
        )

        cog = GuildEvents(mock_bot)
        await cog.on_guild_update(before_guild, after_guild)

        mock_bot.guild_service.update.assert_called_once()
        update_call_args = mock_bot.guild_service.update.call_args
        assert update_call_args[0][0] == "987654321"
        assert isinstance(update_call_args[0][1], GuildCreate)
        assert update_call_args[0][1].name == "New Name"

    @pytest.mark.asyncio
    async def test_on_guild_update_updates_icon(
        self, mock_bot: MagicMock, mock_guild: MagicMock
    ) -> None:
        """Test that on_guild_update updates guild when icon changes."""
        before_guild = MagicMock()
        before_guild.id = 987654321
        before_guild.name = "Test Guild"
        before_guild.icon = None

        after_guild = MagicMock()
        after_guild.id = 987654321
        after_guild.name = "Test Guild"
        after_guild.icon = MagicMock()
        after_guild.icon.url = "https://example.com/new_icon.png"

        mock_bot.guild_service.update = AsyncMock(
            return_value=Guild(
                id=1,
                guild_id="987654321",
                name="Test Guild",
                avatar_url="https://example.com/new_icon.png",
                locale="ja",
            )
        )

        cog = GuildEvents(mock_bot)
        await cog.on_guild_update(before_guild, after_guild)

        mock_bot.guild_service.update.assert_called_once()
        update_call_args = mock_bot.guild_service.update.call_args[0][1]
        assert update_call_args.avatar_url == "https://example.com/new_icon.png"

    @pytest.mark.asyncio
    async def test_on_guild_update_skips_when_no_changes(
        self, mock_bot: MagicMock, mock_guild: MagicMock
    ) -> None:
        """Test that on_guild_update skips update when nothing changes."""
        before_guild = MagicMock()
        before_guild.id = 987654321
        before_guild.name = "Test Guild"
        before_guild.icon = mock_guild.icon

        after_guild = MagicMock()
        after_guild.id = 987654321
        after_guild.name = "Test Guild"
        after_guild.icon = mock_guild.icon

        cog = GuildEvents(mock_bot)
        await cog.on_guild_update(before_guild, after_guild)

        mock_bot.guild_service.update.assert_not_called()
