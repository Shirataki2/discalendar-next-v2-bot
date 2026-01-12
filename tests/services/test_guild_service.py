"""Tests for GuildService."""

from unittest.mock import MagicMock

import pytest

from src.models import Guild, GuildConfig, GuildCreate
from src.services import GuildService


class TestGuildServiceFindByGuildId:
    """Tests for GuildService.find_by_guild_id method."""

    @pytest.mark.asyncio
    async def test_returns_guild_when_exists(self) -> None:
        """Test that find_by_guild_id returns guild when it exists."""
        mock_supabase = MagicMock()
        service = GuildService(mock_supabase)

        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": 1,
                "guild_id": "123",
                "name": "Test Guild",
                "avatar_url": "https://example.com/avatar.png",
                "locale": "ja",
            }
        ]

        mock_query = MagicMock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        guild = await service.find_by_guild_id("123")

        assert guild is not None
        assert guild.guild_id == "123"
        assert guild.name == "Test Guild"

    @pytest.mark.asyncio
    async def test_returns_none_when_not_exists(self) -> None:
        """Test that find_by_guild_id returns None when guild doesn't exist."""
        mock_supabase = MagicMock()
        service = GuildService(mock_supabase)

        mock_response = MagicMock()
        mock_response.data = []

        mock_query = MagicMock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        guild = await service.find_by_guild_id("123")

        assert guild is None


class TestGuildServiceCreate:
    """Tests for GuildService.create method."""

    @pytest.mark.asyncio
    async def test_creates_guild_successfully(self) -> None:
        """Test that create creates a guild successfully."""
        mock_supabase = MagicMock()
        service = GuildService(mock_supabase)

        guild_data = GuildCreate(
            guild_id="123",
            name="New Guild",
            avatar_url="https://example.com/avatar.png",
            locale="ja",
        )

        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": 1,
                "guild_id": "123",
                "name": "New Guild",
                "avatar_url": "https://example.com/avatar.png",
                "locale": "ja",
            }
        ]

        mock_query = MagicMock()
        mock_query.insert.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        guild = await service.create(guild_data)

        assert guild.guild_id == "123"
        assert guild.name == "New Guild"
        mock_query.insert.assert_called_once_with(guild_data.to_dict())


class TestGuildServiceUpdate:
    """Tests for GuildService.update method."""

    @pytest.mark.asyncio
    async def test_updates_guild_successfully(self) -> None:
        """Test that update updates a guild successfully."""
        mock_supabase = MagicMock()
        service = GuildService(mock_supabase)

        guild_data = GuildCreate(
            guild_id="123",
            name="Updated Guild",
            avatar_url="https://example.com/new_avatar.png",
            locale="en",
        )

        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": 1,
                "guild_id": "123",
                "name": "Updated Guild",
                "avatar_url": "https://example.com/new_avatar.png",
                "locale": "en",
            }
        ]

        mock_query = MagicMock()
        mock_query.update.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        guild = await service.update("123", guild_data)

        assert guild.name == "Updated Guild"
        mock_query.update.assert_called_once()
        update_call_args = mock_query.update.call_args[0][0]
        assert update_call_args["name"] == "Updated Guild"
        assert update_call_args["avatar_url"] == "https://example.com/new_avatar.png"
        assert update_call_args["locale"] == "en"
        mock_query.eq.assert_called_once_with("guild_id", "123")


class TestGuildServiceDelete:
    """Tests for GuildService.delete method."""

    @pytest.mark.asyncio
    async def test_deletes_guild_successfully(self) -> None:
        """Test that delete deletes a guild successfully."""
        mock_supabase = MagicMock()
        service = GuildService(mock_supabase)

        mock_query = MagicMock()
        mock_query.delete.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = MagicMock()
        mock_supabase.table.return_value = mock_query

        await service.delete("123")

        mock_query.delete.assert_called_once()
        mock_query.eq.assert_called_once_with("guild_id", "123")


class TestGuildServiceGetConfig:
    """Tests for GuildService.get_config method."""

    @pytest.mark.asyncio
    async def test_returns_config_when_exists(self) -> None:
        """Test that get_config returns config when it exists."""
        mock_supabase = MagicMock()
        service = GuildService(mock_supabase)

        mock_response = MagicMock()
        mock_response.data = [{"guild_id": "123", "restricted": True}]

        mock_query = MagicMock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        config = await service.get_config("123")

        assert config is not None
        assert config.guild_id == "123"
        assert config.restricted is True

    @pytest.mark.asyncio
    async def test_returns_none_when_not_exists(self) -> None:
        """Test that get_config returns None when config doesn't exist."""
        mock_supabase = MagicMock()
        service = GuildService(mock_supabase)

        mock_response = MagicMock()
        mock_response.data = []

        mock_query = MagicMock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        config = await service.get_config("123")

        assert config is None


class TestGuildServiceUpsertConfig:
    """Tests for GuildService.upsert_config method."""

    @pytest.mark.asyncio
    async def test_creates_config_when_not_exists(self) -> None:
        """Test that upsert_config creates config when it doesn't exist."""
        mock_supabase = MagicMock()
        service = GuildService(mock_supabase)

        mock_response = MagicMock()
        mock_response.data = [{"guild_id": "123", "restricted": False}]

        mock_query = MagicMock()
        mock_query.upsert.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        config = await service.upsert_config("123", False)

        assert config.guild_id == "123"
        assert config.restricted is False
        mock_query.upsert.assert_called_once_with({"guild_id": "123", "restricted": False})

    @pytest.mark.asyncio
    async def test_updates_config_when_exists(self) -> None:
        """Test that upsert_config updates config when it exists."""
        mock_supabase = MagicMock()
        service = GuildService(mock_supabase)

        mock_response = MagicMock()
        mock_response.data = [{"guild_id": "123", "restricted": True}]

        mock_query = MagicMock()
        mock_query.upsert.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_query

        config = await service.upsert_config("123", True)

        assert config.guild_id == "123"
        assert config.restricted is True
        mock_query.upsert.assert_called_once_with({"guild_id": "123", "restricted": True})
