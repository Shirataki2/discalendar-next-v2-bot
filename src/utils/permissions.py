"""Permission utilities."""

import discord


def has_manage_permissions(member: discord.Member) -> bool:
    """Check if member has management permissions."""
    perms = member.guild_permissions
    return (
        perms.administrator
        or perms.manage_roles
        or perms.manage_messages
        or perms.manage_guild
    )
