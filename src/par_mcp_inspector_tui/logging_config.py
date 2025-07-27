"""Logging configuration for the application."""

from __future__ import annotations

import logging
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler


def setup_logging(debug: bool = False, log_file: Path | None = None) -> None:
    """Set up logging configuration.

    Args:
        debug: Enable debug level logging
        log_file: Optional file path to write logs to
    """
    # Set logging level
    level = logging.DEBUG if debug else logging.INFO

    # Create handlers
    handlers: list[logging.Handler] = []

    # Rich console handler for pretty terminal output
    console_handler = RichHandler(
        rich_tracebacks=True,
        show_time=debug,
        show_path=debug,
        console=Console(stderr=True),
    )
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    handlers.append(console_handler)

    # Optional file handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True,  # Override any existing configuration
    )

    # Set specific logger levels
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    if debug:
        logger = logging.getLogger(__name__)
        logger.debug("Debug logging enabled")
        if log_file:
            logger.debug(f"Logging to file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
