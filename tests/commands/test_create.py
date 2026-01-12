"""Tests for create command."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.commands.create import CreateCommand
from src.models import Event, GuildConfig


class TestCreateCommand:
    """Tests for CreateCommand."""

    @pytest.mark.asyncio
    async def test_create_event_success(
        self, mock_bot: MagicMock, mock_interaction: MagicMock, mock_member: MagicMock
    ) -> None:
        """Test that create command creates event successfully."""
        mock_interaction.user = mock_member
        mock_bot.guild_service.get_config = AsyncMock(return_value=None)
        mock_bot.event_service.create = AsyncMock(
            return_value=Event(
                id="1",
                guild_id="987654321",
                name="Test Event",
                description="Test Description",
                color="#3e44f7",
                is_all_day=False,
                start_at=datetime(2024, 12, 31, 10, 0, 0, tzinfo=UTC),
                end_at=datetime(2024, 12, 31, 12, 0, 0, tzinfo=UTC),
                location=None,
                channel_id=None,
                channel_name=None,
                notifications=[],
                created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
                updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
            )
        )

        with patch("src.commands.create.create_event_embed") as mock_create_embed:
            mock_embed = MagicMock()
            mock_create_embed.return_value = mock_embed

            cog = CreateCommand(mock_bot)
            await cog.create.callback(  # type: ignore[misc]
                cog,
                mock_interaction,
                name="Test Event",
                start_year=2024,
                start_month=12,
                start_day=31,
                start_hour=10,
                start_minute=0,
                end_year=2024,
                end_month=12,
                end_day=31,
                end_hour=12,
                end_minute=0,
                description="Test Description",
            )

            mock_bot.event_service.create.assert_called_once()
            mock_interaction.response.send_message.assert_called_once_with(
                "正常に予定を作成しました", embed=mock_embed
            )

    @pytest.mark.asyncio
    async def test_create_event_without_guild(
        self, mock_bot: MagicMock, mock_interaction: MagicMock
    ) -> None:
        """Test that create command fails when not in a guild."""
        mock_interaction.guild = None

        cog = CreateCommand(mock_bot)
        await cog.create.callback(  # type: ignore[misc]
            cog,
            mock_interaction,
            name="Test Event",
            start_year=2024,
            start_month=12,
            start_day=31,
            start_hour=10,
            start_minute=0,
            end_year=2024,
            end_month=12,
            end_day=31,
            end_hour=12,
            end_minute=0,
        )

        mock_interaction.response.send_message.assert_called_once_with(
            "このコマンドはサーバーでのみ実行可能です", ephemeral=True
        )
        mock_bot.event_service.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_event_restricted_mode_without_permission(
        self, mock_bot: MagicMock, mock_interaction: MagicMock, mock_member: MagicMock
    ) -> None:
        """Test that create command fails in restricted mode without permission."""
        import discord

        mock_interaction.user = mock_member
        mock_member.guild_permissions.administrator = False
        mock_member.guild_permissions.manage_roles = False
        mock_member.guild_permissions.manage_messages = False
        mock_member.guild_permissions.manage_guild = False

        mock_bot.guild_service.get_config = AsyncMock(
            return_value=GuildConfig(guild_id="987654321", restricted=True)
        )

        # Patch isinstance to return True for discord.Member check
        with patch("src.commands.create.isinstance") as mock_isinstance:
            mock_isinstance.side_effect = lambda obj, cls: cls == discord.Member or isinstance(
                obj, cls
            )

            cog = CreateCommand(mock_bot)
            await cog.create.callback(  # type: ignore[misc]
                cog,
                mock_interaction,
                name="Test Event",
                start_year=2024,
                start_month=12,
                start_day=31,
                start_hour=10,
                start_minute=0,
                end_year=2024,
                end_month=12,
                end_day=31,
                end_hour=12,
                end_minute=0,
            )

            mock_interaction.response.send_message.assert_called_once()
            call_args = mock_interaction.response.send_message.call_args[0][0]
            assert "権限が必要です" in call_args or "このコマンドを実行するためには" in call_args
            assert mock_interaction.response.send_message.call_args[1]["ephemeral"] is True
            mock_bot.event_service.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_event_restricted_mode_with_permission(
        self, mock_bot: MagicMock, mock_interaction: MagicMock, mock_member: MagicMock
    ) -> None:
        """Test that create command succeeds in restricted mode with permission."""
        mock_interaction.user = mock_member
        mock_member.guild_permissions.administrator = True

        mock_bot.guild_service.get_config = AsyncMock(
            return_value=GuildConfig(guild_id="987654321", restricted=True)
        )
        mock_bot.event_service.create = AsyncMock(
            return_value=Event(
                id="1",
                guild_id="987654321",
                name="Test Event",
                description=None,
                color="#3e44f7",
                is_all_day=False,
                start_at=datetime(2024, 12, 31, 10, 0, 0, tzinfo=UTC),
                end_at=datetime(2024, 12, 31, 12, 0, 0, tzinfo=UTC),
                location=None,
                channel_id=None,
                channel_name=None,
                notifications=[],
                created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
                updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
            )
        )

        with patch("src.commands.create.create_event_embed") as mock_create_embed:
            mock_embed = MagicMock()
            mock_create_embed.return_value = mock_embed

            cog = CreateCommand(mock_bot)
            await cog.create.callback(  # type: ignore[misc]
                cog,
                mock_interaction,
                name="Test Event",
                start_year=2024,
                start_month=12,
                start_day=31,
                start_hour=10,
                start_minute=0,
                end_year=2024,
                end_month=12,
                end_day=31,
                end_hour=12,
                end_minute=0,
            )

            mock_bot.event_service.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_event_invalid_start_date(
        self, mock_bot: MagicMock, mock_interaction: MagicMock, mock_member: MagicMock
    ) -> None:
        """Test that create command fails with invalid start date."""
        mock_interaction.user = mock_member
        mock_bot.guild_service.get_config = AsyncMock(return_value=None)

        cog = CreateCommand(mock_bot)
        await cog.create.callback(  # type: ignore[misc]
            cog,
            mock_interaction,
            name="Test Event",
            start_year=2024,
            start_month=13,  # Invalid month
            start_day=1,
            start_hour=10,
            start_minute=0,
            end_year=2024,
            end_month=12,
            end_day=31,
            end_hour=12,
            end_minute=0,
        )

        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args[0][0]
        assert "無効な開始日時です" in call_args
        mock_bot.event_service.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_event_invalid_end_date(
        self, mock_bot: MagicMock, mock_interaction: MagicMock, mock_member: MagicMock
    ) -> None:
        """Test that create command fails with invalid end date."""
        mock_interaction.user = mock_member
        mock_bot.guild_service.get_config = AsyncMock(return_value=None)

        cog = CreateCommand(mock_bot)
        await cog.create.callback(  # type: ignore[misc]
            cog,
            mock_interaction,
            name="Test Event",
            start_year=2024,
            start_month=12,
            start_day=31,
            start_hour=10,
            start_minute=0,
            end_year=2024,
            end_month=2,
            end_day=30,  # Invalid day for February
            end_hour=12,
            end_minute=0,
        )

        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args[0][0]
        assert "無効な終了日時です" in call_args
        mock_bot.event_service.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_event_start_after_end(
        self, mock_bot: MagicMock, mock_interaction: MagicMock, mock_member: MagicMock
    ) -> None:
        """Test that create command fails when start time is after end time."""
        mock_interaction.user = mock_member
        mock_bot.guild_service.get_config = AsyncMock(return_value=None)

        cog = CreateCommand(mock_bot)
        await cog.create.callback(  # type: ignore[misc]
            cog,
            mock_interaction,
            name="Test Event",
            start_year=2024,
            start_month=12,
            start_day=31,
            start_hour=14,
            start_minute=0,
            end_year=2024,
            end_month=12,
            end_day=31,
            end_hour=12,
            end_minute=0,
        )

        mock_interaction.response.send_message.assert_called_once_with(
            "開始時間が終了時間より後になっています", ephemeral=True
        )
        mock_bot.event_service.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_event_with_color(
        self, mock_bot: MagicMock, mock_interaction: MagicMock, mock_member: MagicMock
    ) -> None:
        """Test that create command handles color correctly."""
        mock_interaction.user = mock_member
        mock_bot.guild_service.get_config = AsyncMock(return_value=None)
        mock_bot.event_service.create = AsyncMock(
            return_value=Event(
                id="1",
                guild_id="987654321",
                name="Test Event",
                description=None,
                color="#fd4028",
                is_all_day=False,
                start_at=datetime(2024, 12, 31, 10, 0, 0, tzinfo=UTC),
                end_at=datetime(2024, 12, 31, 12, 0, 0, tzinfo=UTC),
                location=None,
                channel_id=None,
                channel_name=None,
                notifications=[],
                created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
                updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
            )
        )

        with patch("src.commands.create.create_event_embed"):
            cog = CreateCommand(mock_bot)
            await cog.create.callback(  # type: ignore[misc]
                cog,
                mock_interaction,
                name="Test Event",
                start_year=2024,
                start_month=12,
                start_day=31,
                start_hour=10,
                start_minute=0,
                end_year=2024,
                end_month=12,
                end_day=31,
                end_hour=12,
                end_minute=0,
                color="red",
            )

            call_args = mock_bot.event_service.create.call_args[0][0]
            assert call_args.color == "#fd4028"

    @pytest.mark.asyncio
    async def test_create_event_with_notifications(
        self, mock_bot: MagicMock, mock_interaction: MagicMock, mock_member: MagicMock
    ) -> None:
        """Test that create command parses notifications correctly."""
        mock_interaction.user = mock_member
        mock_bot.guild_service.get_config = AsyncMock(return_value=None)
        mock_bot.event_service.create = AsyncMock(
            return_value=Event(
                id="1",
                guild_id="987654321",
                name="Test Event",
                description=None,
                color="#3e44f7",
                is_all_day=False,
                start_at=datetime(2024, 12, 31, 10, 0, 0, tzinfo=UTC),
                end_at=datetime(2024, 12, 31, 12, 0, 0, tzinfo=UTC),
                location=None,
                channel_id=None,
                channel_name=None,
                notifications=[],
                created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
                updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
            )
        )

        with patch("src.commands.create.create_event_embed"):
            cog = CreateCommand(mock_bot)
            await cog.create.callback(  # type: ignore[misc]
                cog,
                mock_interaction,
                name="Test Event",
                start_year=2024,
                start_month=12,
                start_day=31,
                start_hour=10,
                start_minute=0,
                end_year=2024,
                end_month=12,
                end_day=31,
                end_hour=12,
                end_minute=0,
                notify_1="30m",
                notify_2="1h",
            )

            call_args = mock_bot.event_service.create.call_args[0][0]
            assert len(call_args.notifications) == 2
            assert call_args.notifications[0]["key"] == 0
            assert call_args.notifications[0]["num"] == 30
            assert call_args.notifications[0]["type"] == "分前"
            assert call_args.notifications[1]["key"] == 1
            assert call_args.notifications[1]["num"] == 1
            assert call_args.notifications[1]["type"] == "時間前"

    @pytest.mark.asyncio
    async def test_create_event_all_day(
        self, mock_bot: MagicMock, mock_interaction: MagicMock, mock_member: MagicMock
    ) -> None:
        """Test that create command handles all-day events."""
        mock_interaction.user = mock_member
        mock_bot.guild_service.get_config = AsyncMock(return_value=None)
        mock_bot.event_service.create = AsyncMock(
            return_value=Event(
                id="1",
                guild_id="987654321",
                name="All Day Event",
                description=None,
                color="#3e44f7",
                is_all_day=True,
                start_at=datetime(2024, 12, 31, 0, 0, 0, tzinfo=UTC),
                end_at=datetime(2024, 12, 31, 0, 0, 0, tzinfo=UTC),
                location=None,
                channel_id=None,
                channel_name=None,
                notifications=[],
                created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
                updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
            )
        )

        with patch("src.commands.create.create_event_embed"):
            cog = CreateCommand(mock_bot)
            await cog.create.callback(  # type: ignore[misc]
                cog,
                mock_interaction,
                name="All Day Event",
                start_year=2024,
                start_month=12,
                start_day=31,
                start_hour=0,
                start_minute=0,
                end_year=2024,
                end_month=12,
                end_day=31,
                end_hour=0,
                end_minute=0,
                is_all_day=True,
            )

            call_args = mock_bot.event_service.create.call_args[0][0]
            assert call_args.is_all_day is True
