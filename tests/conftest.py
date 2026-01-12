"""Common fixtures for tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from supabase import Client

from src.bot import DisCalendarBot
from src.services import EventService, GuildService


@pytest.fixture
def mock_supabase_client() -> MagicMock:
    """Create a mock Supabase client."""
    return MagicMock(spec=Client)


@pytest.fixture
def mock_event_service(mock_supabase_client: MagicMock) -> MagicMock:
    """Create a mock EventService."""
    return MagicMock(spec=EventService, supabase=mock_supabase_client)


@pytest.fixture
def mock_guild_service(mock_supabase_client: MagicMock) -> MagicMock:
    """Create a mock GuildService."""
    return MagicMock(spec=GuildService, supabase=mock_supabase_client)


@pytest.fixture
def mock_bot(
    mock_supabase_client: MagicMock,
    mock_event_service: MagicMock,
    mock_guild_service: MagicMock,
) -> MagicMock:
    """Create a mock DisCalendarBot."""
    bot = MagicMock(spec=DisCalendarBot)
    bot.supabase = mock_supabase_client
    bot.event_service = mock_event_service
    bot.guild_service = mock_guild_service
    bot.user = MagicMock()
    bot.user.id = 123456789
    bot.user.avatar = MagicMock()
    bot.user.avatar.url = "https://example.com/avatar.png"
    bot.guilds = []
    bot.get_channel = AsyncMock()
    bot.wait_until_ready = AsyncMock()
    bot.change_presence = AsyncMock()
    return bot


@pytest.fixture
def mock_guild() -> MagicMock:
    """Create a mock discord.Guild."""
    guild = MagicMock()
    guild.id = 987654321
    guild.name = "Test Guild"
    guild.icon = MagicMock()
    guild.icon.url = "https://example.com/guild_icon.png"
    return guild


@pytest.fixture
def mock_member(mock_guild: MagicMock) -> MagicMock:
    """Create a mock discord.Member."""
    import discord

    member = MagicMock(spec=discord.Member)
    member.id = 111222333
    member.name = "TestUser"
    member.guild = mock_guild
    member.guild_permissions = MagicMock()
    member.guild_permissions.administrator = False
    member.guild_permissions.manage_roles = False
    member.guild_permissions.manage_messages = False
    member.guild_permissions.manage_guild = False
    return member


@pytest.fixture
def mock_channel() -> MagicMock:
    """Create a mock discord.TextChannel."""
    channel = MagicMock()
    channel.id = 555666777
    channel.name = "test-channel"
    channel.send = AsyncMock()
    channel.guild = MagicMock()
    channel.guild.id = 987654321
    return channel


@pytest.fixture
def mock_interaction(mock_guild: MagicMock, mock_member: MagicMock, mock_channel: MagicMock) -> MagicMock:
    """Create a mock discord.Interaction."""
    interaction = MagicMock()
    interaction.id = 444555666
    interaction.guild = mock_guild
    interaction.user = mock_member
    interaction.channel = mock_channel
    interaction.response = MagicMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.edit_message = AsyncMock()
    return interaction
