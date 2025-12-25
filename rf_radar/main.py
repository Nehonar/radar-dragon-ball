"""Entry point for the RF Presence Radar prototype (Hito 0)."""
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """Boot the application with a single startup log."""
    logger.info("RF Presence Radar - BOOT")


if __name__ == "__main__":
    main()
