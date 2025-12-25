"""Logging setup for the RF Presence Radar."""

import logging
import sys


def setup_logging(config) -> None:
    """Configure global logging using the provided config module."""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format="%(levelname)s - %(message)s",
        stream=sys.stdout,
    )
