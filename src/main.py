"""Entry point for DisCalendar Discord Bot."""

import asyncio
import logging
import sys

import structlog

from src.bot import DisCalendarBot
from src.config import get_config


def configure_logging(log_level: str) -> None:
    """Configure structlog and standard library logging."""
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )

    # Set log level for discord.py and other libraries
    logging.getLogger("discord").setLevel(logging.INFO)
    logging.getLogger("discord.http").setLevel(logging.WARNING)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Configure logging before creating logger
config = get_config()
configure_logging(config.log_level)
logger = structlog.get_logger()


async def main() -> None:
    """Main entry point."""
    logger.info("Starting DisCalendar Bot...")

    try:
        config = get_config()
        bot = DisCalendarBot()
        async with bot:
            await bot.start(config.bot_token)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception("Fatal error", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
