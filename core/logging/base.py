import logging
from functools import lru_cache

from django.conf import settings
from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Logging handler that routes standard Python logs to Loguru.

    - Maps standard logging levels to Loguru levels.
    - Maintains correct call stack depth for accurate log source reporting.
    - Preserves original log context and exception info.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to Loguru, preserving context and stack depth.

        Args:
            record: The log record to emit.
        """
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


@lru_cache(maxsize=1)
def setup_logging() -> None:
    """
    Configure Loguru as the main logging backend.

    - Redirects all standard logging to Loguru.
    - Sets log level and clears handlers for all loggers.
    - Configures file logging with rotation and retention.
    """
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(settings.LOGGING_LEVEL)

    for file in logging.root.manager.loggerDict.keys():
        logging.getLogger(file).handlers = []
        logging.getLogger(file).propagate = True

    logger.configure(
        handlers=[
            # File output
            {
                "sink": settings.LOG_FILE,
                "rotation": "10 MB",
                "retention": "10 days",
                "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <5} | {file}:{line} - {message}",  # noqa
            },
        ]
    )


setup_logging()
