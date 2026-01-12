"""Guild data models."""

from dataclasses import dataclass
from typing import Self


@dataclass
class Guild:
    """Guild model."""

    id: int
    guild_id: str
    name: str
    avatar_url: str | None
    locale: str

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create Guild from dictionary."""
        return cls(
            id=data["id"],
            guild_id=data["guild_id"],
            name=data["name"],
            avatar_url=data.get("avatar_url"),
            locale=data.get("locale", "ja"),
        )


@dataclass
class GuildCreate:
    """Guild creation data."""

    guild_id: str
    name: str
    avatar_url: str | None = None
    locale: str = "ja"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "guild_id": self.guild_id,
            "name": self.name,
            "avatar_url": self.avatar_url,
            "locale": self.locale,
        }


@dataclass
class GuildConfig:
    """Guild configuration model."""

    guild_id: str
    restricted: bool

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create GuildConfig from dictionary."""
        return cls(
            guild_id=data["guild_id"],
            restricted=data.get("restricted", False),
        )
