"""Tests for datetime utilities."""

from datetime import UTC, datetime, timedelta, timezone

import pytest

from src.utils.datetime import format_date, format_datetime, get_jst_now, validate_date

JST = timezone(timedelta(hours=9))


class TestGetJstNow:
    """Tests for get_jst_now function."""

    def test_returns_datetime(self) -> None:
        """Test that get_jst_now returns a datetime object."""
        result = get_jst_now()
        assert isinstance(result, datetime)
        assert result.tzinfo is not None

    def test_timezone_is_jst(self) -> None:
        """Test that returned datetime is in JST timezone."""
        result = get_jst_now()
        assert result.tzinfo == JST


class TestFormatDatetime:
    """Tests for format_datetime function."""

    def test_formats_correctly(self) -> None:
        """Test that datetime is formatted as YYYY/MM/DD HH:MM."""
        dt = datetime(2024, 1, 15, 14, 30, 0, tzinfo=UTC)
        result = format_datetime(dt)
        assert result == "2024/01/15 23:30"  # UTC to JST conversion

    def test_preserves_timezone_conversion(self) -> None:
        """Test that timezone conversion is applied."""
        dt = datetime(2024, 12, 31, 15, 0, 0, tzinfo=UTC)
        result = format_datetime(dt)
        # UTC 15:00 = JST 00:00 (next day)
        assert result.startswith("2025/01/01")


class TestFormatDate:
    """Tests for format_date function."""

    def test_formats_correctly(self) -> None:
        """Test that datetime is formatted as YYYY/MM/DD."""
        dt = datetime(2024, 3, 20, 10, 30, 0, tzinfo=UTC)
        result = format_date(dt)
        assert result == "2024/03/20"

    def test_time_component_ignored(self) -> None:
        """Test that time component is ignored."""
        # Use dates that won't cross day boundary when converted to JST
        dt1 = datetime(2024, 5, 10, 0, 0, 0, tzinfo=UTC)
        dt2 = datetime(2024, 5, 10, 14, 59, 59, tzinfo=UTC)  # Before 15:00 UTC (00:00 JST next day)
        result1 = format_date(dt1)
        result2 = format_date(dt2)
        assert result1 == result2 == "2024/05/10"


class TestValidateDate:
    """Tests for validate_date function."""

    def test_valid_date(self) -> None:
        """Test validation of valid dates."""
        assert validate_date(2024, 1, 15, 10, 30) is True
        assert validate_date(2024, 12, 31, 23, 59) is True
        assert validate_date(1970, 1, 1, 0, 0) is True
        assert validate_date(2099, 12, 31, 23, 59) is True

    def test_invalid_year_too_low(self) -> None:
        """Test that years below 1970 are invalid."""
        assert validate_date(1969, 1, 1, 0, 0) is False

    def test_invalid_year_too_high(self) -> None:
        """Test that years above 2099 are invalid."""
        assert validate_date(2100, 1, 1, 0, 0) is False

    def test_invalid_month_too_low(self) -> None:
        """Test that months below 1 are invalid."""
        assert validate_date(2024, 0, 1, 0, 0) is False

    def test_invalid_month_too_high(self) -> None:
        """Test that months above 12 are invalid."""
        assert validate_date(2024, 13, 1, 0, 0) is False

    def test_invalid_day_too_low(self) -> None:
        """Test that days below 1 are invalid."""
        assert validate_date(2024, 1, 0, 0, 0) is False

    def test_invalid_day_too_high(self) -> None:
        """Test that days above 31 are invalid."""
        assert validate_date(2024, 1, 32, 0, 0) is False

    def test_invalid_hour_too_low(self) -> None:
        """Test that hours below 0 are invalid."""
        assert validate_date(2024, 1, 1, -1, 0) is False

    def test_invalid_hour_too_high(self) -> None:
        """Test that hours above 23 are invalid."""
        assert validate_date(2024, 1, 1, 24, 0) is False

    def test_invalid_minute_too_low(self) -> None:
        """Test that minutes below 0 are invalid."""
        assert validate_date(2024, 1, 1, 0, -1) is False

    def test_invalid_minute_too_high(self) -> None:
        """Test that minutes above 59 are invalid."""
        assert validate_date(2024, 1, 1, 0, 60) is False

    def test_invalid_day_in_30_day_month(self) -> None:
        """Test that day 31 is invalid for 30-day months."""
        assert validate_date(2024, 4, 31, 0, 0) is False  # April
        assert validate_date(2024, 6, 31, 0, 0) is False  # June
        assert validate_date(2024, 9, 31, 0, 0) is False  # September
        assert validate_date(2024, 11, 31, 0, 0) is False  # November

    def test_valid_day_in_30_day_month(self) -> None:
        """Test that days up to 30 are valid for 30-day months."""
        assert validate_date(2024, 4, 30, 0, 0) is True
        assert validate_date(2024, 6, 30, 0, 0) is True

    def test_invalid_february_day_30(self) -> None:
        """Test that day 30 is invalid for February."""
        assert validate_date(2024, 2, 30, 0, 0) is False

    def test_invalid_february_day_29_non_leap_year(self) -> None:
        """Test that day 29 is invalid for February in non-leap years."""
        assert validate_date(2023, 2, 29, 0, 0) is False  # 2023 is not a leap year
        assert validate_date(2100, 2, 29, 0, 0) is False  # 2100 is not a leap year

    def test_valid_february_day_29_leap_year(self) -> None:
        """Test that day 29 is valid for February in leap years."""
        assert validate_date(2024, 2, 29, 0, 0) is True  # 2024 is a leap year
        assert validate_date(2000, 2, 29, 0, 0) is True  # 2000 is a leap year

    def test_valid_february_day_28(self) -> None:
        """Test that day 28 is always valid for February."""
        assert validate_date(2023, 2, 28, 0, 0) is True  # Non-leap year
        assert validate_date(2024, 2, 28, 0, 0) is True  # Leap year

    def test_leap_year_divisible_by_4(self) -> None:
        """Test leap year detection for years divisible by 4."""
        assert validate_date(2020, 2, 29, 0, 0) is True  # Divisible by 4

    def test_leap_year_not_divisible_by_100(self) -> None:
        """Test leap year detection for years divisible by 4 but not by 100."""
        assert validate_date(2004, 2, 29, 0, 0) is True  # 2004 % 4 == 0, 2004 % 100 != 0

    def test_leap_year_divisible_by_400(self) -> None:
        """Test leap year detection for years divisible by 400."""
        assert validate_date(2000, 2, 29, 0, 0) is True  # 2000 % 400 == 0
