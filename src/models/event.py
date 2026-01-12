"""Event data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self


@dataclass
class NotificationPayload:
    """Notification payload model."""

    key: int
    num: int
    ty: str  # "分前", "時間前", "日前"

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create NotificationPayload from dictionary."""
        return cls(
            key=data["key"],
            num=data["num"],
            ty=data.get("type", "分前"),
        )

    def to_minutes(self) -> int:
        """Convert to minutes."""
        if self.ty == "時間前":
            return self.num * 60
        elif self.ty == "日前":
            return self.num * 60 * 24
        elif self.ty == "週間前":
            return self.num * 60 * 24 * 7
        return self.num  # 分前

    def __str__(self) -> str:
        return f"{self.num}{self.ty}"


@dataclass
class Event:
    """Event model."""

    id: str
    guild_id: str
    name: str
    description: str | None
    color: str
    is_all_day: bool
    start_at: datetime
    end_at: datetime
    location: str | None
    channel_id: str | None
    channel_name: str | None
    notifications: list[NotificationPayload]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create Event from dictionary."""
        notifications = []
        if data.get("notifications"):
            for n in data["notifications"]:
                if isinstance(n, dict):
                    notifications.append(NotificationPayload.from_dict(n))

        return cls(
            id=data["id"],
            guild_id=data["guild_id"],
            name=data["name"],
            description=data.get("description"),
            color=data.get("color", "#3B82F6"),
            is_all_day=data.get("is_all_day", False),
            start_at=datetime.fromisoformat(data["start_at"].replace("Z", "+00:00")),
            end_at=datetime.fromisoformat(data["end_at"].replace("Z", "+00:00")),
            location=data.get("location"),
            channel_id=data.get("channel_id"),
            channel_name=data.get("channel_name"),
            notifications=notifications,
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
        )


@dataclass
class EventCreate:
    """Event creation data."""

    guild_id: str
    name: str
    start_at: datetime
    end_at: datetime
    description: str | None = None
    color: str = "#3B82F6"
    is_all_day: bool = False
    location: str | None = None
    channel_id: str | None = None
    channel_name: str | None = None
    notifications: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "guild_id": self.guild_id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "is_all_day": self.is_all_day,
            "start_at": self.start_at.isoformat(),
            "end_at": self.end_at.isoformat(),
            "location": self.location,
            "channel_id": self.channel_id,
            "channel_name": self.channel_name,
            "notifications": self.notifications,
        }


@dataclass
class EventSettings:
    """Event settings model."""

    id: int
    guild_id: str
    channel_id: str

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create EventSettings from dictionary."""
        return cls(
            id=data["id"],
            guild_id=data["guild_id"],
            channel_id=data["channel_id"],
        )
