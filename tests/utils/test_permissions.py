"""Tests for permission utilities."""

from unittest.mock import MagicMock

import pytest

from src.utils.permissions import has_manage_permissions


class TestHasManagePermissions:
    """Tests for has_manage_permissions function."""

    def test_returns_true_with_administrator_permission(self) -> None:
        """Test that administrator permission returns True."""
        member = MagicMock()
        member.guild_permissions = MagicMock()
        member.guild_permissions.administrator = True
        member.guild_permissions.manage_roles = False
        member.guild_permissions.manage_messages = False
        member.guild_permissions.manage_guild = False

        assert has_manage_permissions(member) is True

    def test_returns_true_with_manage_roles_permission(self) -> None:
        """Test that manage_roles permission returns True."""
        member = MagicMock()
        member.guild_permissions = MagicMock()
        member.guild_permissions.administrator = False
        member.guild_permissions.manage_roles = True
        member.guild_permissions.manage_messages = False
        member.guild_permissions.manage_guild = False

        assert has_manage_permissions(member) is True

    def test_returns_true_with_manage_messages_permission(self) -> None:
        """Test that manage_messages permission returns True."""
        member = MagicMock()
        member.guild_permissions = MagicMock()
        member.guild_permissions.administrator = False
        member.guild_permissions.manage_roles = False
        member.guild_permissions.manage_messages = True
        member.guild_permissions.manage_guild = False

        assert has_manage_permissions(member) is True

    def test_returns_true_with_manage_guild_permission(self) -> None:
        """Test that manage_guild permission returns True."""
        member = MagicMock()
        member.guild_permissions = MagicMock()
        member.guild_permissions.administrator = False
        member.guild_permissions.manage_roles = False
        member.guild_permissions.manage_messages = False
        member.guild_permissions.manage_guild = True

        assert has_manage_permissions(member) is True

    def test_returns_false_without_any_permission(self) -> None:
        """Test that no permissions returns False."""
        member = MagicMock()
        member.guild_permissions = MagicMock()
        member.guild_permissions.administrator = False
        member.guild_permissions.manage_roles = False
        member.guild_permissions.manage_messages = False
        member.guild_permissions.manage_guild = False

        assert has_manage_permissions(member) is False

    def test_returns_true_with_multiple_permissions(self) -> None:
        """Test that having multiple permissions returns True."""
        member = MagicMock()
        member.guild_permissions = MagicMock()
        member.guild_permissions.administrator = True
        member.guild_permissions.manage_roles = True
        member.guild_permissions.manage_messages = True
        member.guild_permissions.manage_guild = True

        assert has_manage_permissions(member) is True
