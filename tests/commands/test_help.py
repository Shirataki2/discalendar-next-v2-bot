"""Tests for help command."""

from unittest.mock import MagicMock, patch

import pytest

from src.commands.help import HelpCommand


class TestHelpCommand:
    """Tests for HelpCommand."""

    @pytest.mark.asyncio
    async def test_help_with_avatar(
        self, mock_bot: MagicMock, mock_interaction: MagicMock
    ) -> None:
        """Test that help command creates embed with bot avatar."""
        mock_bot.user.avatar.url = "https://example.com/avatar.png"

        with patch("src.commands.help.get_config") as mock_get_config, patch(
            "src.commands.help.create_help_embed"
        ) as mock_create_help_embed:
            mock_config = MagicMock()
            mock_config.invitation_url = "https://discord.com/invite/test"
            mock_get_config.return_value = mock_config

            mock_embed = MagicMock()
            mock_create_help_embed.return_value = mock_embed

            cog = HelpCommand(mock_bot)
            await cog.help.callback(cog, mock_interaction)  # type: ignore[misc]

            mock_create_help_embed.assert_called_once_with(
                "https://example.com/avatar.png", "https://discord.com/invite/test"
            )
            mock_interaction.response.send_message.assert_called_once_with(
                embed=mock_embed, ephemeral=True
            )

    @pytest.mark.asyncio
    async def test_help_without_avatar(
        self, mock_bot: MagicMock, mock_interaction: MagicMock
    ) -> None:
        """Test that help command creates embed without bot avatar."""
        mock_bot.user.avatar = None

        with patch("src.commands.help.get_config") as mock_get_config, patch(
            "src.commands.help.create_help_embed"
        ) as mock_create_help_embed:
            mock_config = MagicMock()
            mock_config.invitation_url = "https://discord.com/invite/test"
            mock_get_config.return_value = mock_config

            mock_embed = MagicMock()
            mock_create_help_embed.return_value = mock_embed

            cog = HelpCommand(mock_bot)
            await cog.help.callback(cog, mock_interaction)  # type: ignore[misc]

            mock_create_help_embed.assert_called_once_with(None, "https://discord.com/invite/test")
            mock_interaction.response.send_message.assert_called_once_with(
                embed=mock_embed, ephemeral=True
            )
