"""Tests for init command."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.commands.init import InitCommand
from src.models import EventSettings


class TestInitCommand:
    """Tests for InitCommand."""

    @pytest.mark.asyncio
    async def test_init_creates_settings_when_not_exists(
        self,
        mock_bot: MagicMock,
        mock_interaction: MagicMock,
        mock_channel: MagicMock,
        mock_member: MagicMock,
    ) -> None:
        """Test that init command creates settings when they don't exist."""
        import discord

        # Set user with admin permission
        mock_interaction.user = mock_member
        mock_member.guild_permissions.administrator = True
        mock_interaction.channel = mock_channel
        mock_bot.event_service.get_settings = AsyncMock(return_value=None)
        mock_bot.event_service.create_settings = AsyncMock(
            return_value=EventSettings(id=1, guild_id="987654321", channel_id="555666777")
        )

        # Patch isinstance to return True for discord.Member check
        with patch("src.commands.init.isinstance") as mock_isinstance:
            mock_isinstance.side_effect = lambda obj, cls: cls == discord.Member or isinstance(
                obj, cls
            )

            cog = InitCommand(mock_bot)
            await cog.init.callback(cog, mock_interaction)  # type: ignore[misc]

            mock_bot.event_service.create_settings.assert_called_once_with("987654321", "555666777")
            mock_interaction.response.send_message.assert_called_once()
            call_args = mock_interaction.response.send_message.call_args[0][0]
            assert "イベント通知を有効にしました" in call_args
        assert "<#555666777>" in call_args

    @pytest.mark.asyncio
    async def test_init_updates_settings_when_exists(
        self,
        mock_bot: MagicMock,
        mock_interaction: MagicMock,
        mock_channel: MagicMock,
        mock_member: MagicMock,
    ) -> None:
        """Test that init command updates settings when they exist."""
        import discord

        # Set user with admin permission
        mock_interaction.user = mock_member
        mock_member.guild_permissions.administrator = True
        mock_interaction.channel = mock_channel
        existing_settings = EventSettings(id=1, guild_id="987654321", channel_id="111222333")
        mock_bot.event_service.get_settings = AsyncMock(return_value=existing_settings)
        mock_bot.event_service.update_settings = AsyncMock(
            return_value=EventSettings(id=1, guild_id="987654321", channel_id="555666777")
        )

        # Patch isinstance to return True for discord.Member check
        with patch("src.commands.init.isinstance") as mock_isinstance:
            mock_isinstance.side_effect = lambda obj, cls: cls == discord.Member or isinstance(
                obj, cls
            )

            cog = InitCommand(mock_bot)
            await cog.init.callback(cog, mock_interaction)  # type: ignore[misc]

            mock_bot.event_service.update_settings.assert_called_once_with("987654321", "555666777")
            mock_interaction.response.send_message.assert_called_once()
            call_args = mock_interaction.response.send_message.call_args[0][0]
            assert "イベント通知先を変更しました" in call_args
        assert "<#111222333>" in call_args
        assert "<#555666777>" in call_args

    @pytest.mark.asyncio
    async def test_init_with_specified_channel(
        self,
        mock_bot: MagicMock,
        mock_interaction: MagicMock,
        mock_channel: MagicMock,
        mock_member: MagicMock,
    ) -> None:
        """Test that init command uses specified channel."""
        import discord

        # Set user with admin permission
        mock_interaction.user = mock_member
        mock_member.guild_permissions.administrator = True

        specified_channel = MagicMock()
        specified_channel.id = 999888777

        mock_bot.event_service.get_settings = AsyncMock(return_value=None)
        mock_bot.event_service.create_settings = AsyncMock(
            return_value=EventSettings(id=1, guild_id="987654321", channel_id="999888777")
        )

        # Patch isinstance to return True for discord.Member check
        with patch("src.commands.init.isinstance") as mock_isinstance:
            mock_isinstance.side_effect = lambda obj, cls: cls == discord.Member or isinstance(
                obj, cls
            )

            cog = InitCommand(mock_bot)
            await cog.init.callback(cog, mock_interaction, channel=specified_channel)  # type: ignore[misc]

            mock_bot.event_service.create_settings.assert_called_once_with("987654321", "999888777")

    @pytest.mark.asyncio
    async def test_init_without_guild(
        self, mock_bot: MagicMock, mock_interaction: MagicMock
    ) -> None:
        """Test that init command fails when not in a guild."""
        mock_interaction.guild = None

        cog = InitCommand(mock_bot)
        await cog.init.callback(cog, mock_interaction)  # type: ignore[misc]

        mock_interaction.response.send_message.assert_called_once_with(
            "このコマンドはサーバー内で実行してください", ephemeral=True
        )
        mock_bot.event_service.create_settings.assert_not_called()
        mock_bot.event_service.update_settings.assert_not_called()

    @pytest.mark.asyncio
    async def test_init_without_permissions(
        self, mock_bot: MagicMock, mock_interaction: MagicMock, mock_member: MagicMock
    ) -> None:
        """Test that init command fails when user lacks permissions."""
        import discord

        mock_interaction.user = mock_member
        mock_member.guild_permissions.administrator = False
        mock_member.guild_permissions.manage_roles = False
        mock_member.guild_permissions.manage_messages = False
        mock_member.guild_permissions.manage_guild = False

        # Patch isinstance to return True for discord.Member check
        with patch("src.commands.init.isinstance") as mock_isinstance:
            mock_isinstance.side_effect = lambda obj, cls: cls == discord.Member or isinstance(
                obj, cls
            )

            cog = InitCommand(mock_bot)
            await cog.init.callback(cog, mock_interaction)  # type: ignore[misc]

            mock_interaction.response.send_message.assert_called_once()
            call_args = mock_interaction.response.send_message.call_args[0][0]
            assert "権限が必要です" in call_args or "このコマンドを実行するためには" in call_args
            assert mock_interaction.response.send_message.call_args[1]["ephemeral"] is True
            mock_bot.event_service.create_settings.assert_not_called()

    @pytest.mark.asyncio
    async def test_init_with_permissions(
        self,
        mock_bot: MagicMock,
        mock_interaction: MagicMock,
        mock_member: MagicMock,
        mock_channel: MagicMock,
    ) -> None:
        """Test that init command succeeds when user has permissions."""
        mock_interaction.user = mock_member
        mock_interaction.channel = mock_channel
        mock_member.guild_permissions.administrator = True

        mock_bot.event_service.get_settings = AsyncMock(return_value=None)
        mock_bot.event_service.create_settings = AsyncMock(
            return_value=EventSettings(id=1, guild_id="987654321", channel_id="555666777")
        )

        cog = InitCommand(mock_bot)
        await cog.init.callback(cog, mock_interaction)  # type: ignore[misc]

        mock_bot.event_service.create_settings.assert_called_once()

    @pytest.mark.asyncio
    async def test_init_without_channel(
        self, mock_bot: MagicMock, mock_interaction: MagicMock, mock_member: MagicMock
    ) -> None:
        """Test that init command fails when channel is None."""
        import discord

        # Set user with admin permission
        mock_interaction.user = mock_member
        mock_member.guild_permissions.administrator = True
        mock_interaction.channel = None

        # Patch isinstance to return True for discord.Member check
        with patch("src.commands.init.isinstance") as mock_isinstance:
            mock_isinstance.side_effect = lambda obj, cls: cls == discord.Member or isinstance(
                obj, cls
            )

            cog = InitCommand(mock_bot)
            await cog.init.callback(cog, mock_interaction)  # type: ignore[misc]

            mock_interaction.response.send_message.assert_called_once_with(
                "チャンネルを指定してください", ephemeral=True
            )
            mock_bot.event_service.create_settings.assert_not_called()
