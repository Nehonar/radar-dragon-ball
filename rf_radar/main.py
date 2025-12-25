"""Entry point for the RF Presence Radar prototype (Hito 1)."""
import logging

from rf_radar.core import config
from rf_radar.infrastructure.logging import setup_logging
from rf_radar.infrastructure import queues


def main() -> None:
    """Initialize infrastructure and exit cleanly."""
    setup_logging(config)
    logger = logging.getLogger(__name__)

    observation_queue = queues.create_observation_queue(config)
    snapshot_queue = queues.create_snapshot_queue(config)

    # Avoid unused variable warnings in future checks.
    _ = (observation_queue, snapshot_queue)

    logger.info("Infrastructure initialized")


if __name__ == "__main__":
    main()
