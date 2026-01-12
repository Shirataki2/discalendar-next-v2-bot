"""Tests for invite command."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.commands.invite import InviteCommand


class TestInviteCommand:
    """Tests for InviteCommand."""

    @pytest.mark.asyncio
    async def test_invite_displays_url(self, mock_bot: MagicMock, mock_interaction: MagicMock) -> None:
        """Test that invite command displays invitation URL."""
        with patch("src.commands.invite.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.invitation_url = "https://discord.com/invite/test123"
            mock_get_config.return_value = mock_config

            cog = InviteCommand(mock_bot)
            await cog.invite.callback(cog, mock_interaction)  # type: ignore[misc]

            mock_interaction.response.send_message.assert_called_once_with("https://discord.com/invite/test123")
