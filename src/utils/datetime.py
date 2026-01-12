"""Datetime utilities."""

from datetime import UTC, datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))


def get_jst_now() -> datetime:
    """Get current time in JST."""
    return datetime.now(UTC).astimezone(JST)


def format_datetime(dt: datetime) -> str:
    """Format datetime as YYYY/MM/DD HH:MM."""
    jst_dt = dt.astimezone(JST)
    return jst_dt.strftime("%Y/%m/%d %H:%M")


def format_date(dt: datetime) -> str:
    """Format datetime as YYYY/MM/DD."""
    jst_dt = dt.astimezone(JST)
    return jst_dt.strftime("%Y/%m/%d")


def validate_date(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0
) -> bool:
    """Validate date components."""
    if not (1970 <= year <= 2099):
        return False
    if not (1 <= month <= 12):
        return False
    if not (1 <= day <= 31):
        return False
    if not (0 <= hour <= 23):
        return False
    if not (0 <= minute <= 59):
        return False

    # Check days in month
    if month in (4, 6, 9, 11) and day == 31:
        return False
    if month == 2:
        if day > 29:
            return False
        # Leap year check
        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        if day == 29 and not is_leap:
            return False

    return True
