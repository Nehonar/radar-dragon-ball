"""Entry point for the RF Presence Radar prototype."""
import logging
import time

from rf_radar.app.runtime import Runtime, install_signal_handlers
from rf_radar.core import config
from rf_radar.infrastructure import queues
from rf_radar.infrastructure.logging import setup_logging


def main() -> None:
    """Initialize runtime, run until stopped, then exit cleanly."""
    setup_logging(config)
    logger = logging.getLogger(__name__)

    observation_queue = queues.create_observation_queue(config)
    snapshot_queue = queues.create_snapshot_queue(config)

    runtime = Runtime(config, observation_queue, snapshot_queue)
    install_signal_handlers(runtime)

    logger.info("Starting runtime")
    runtime.start()

    try:
        while runtime.is_running():
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received; stopping runtime.")
        runtime.stop()
    finally:
        runtime.stop()
        logger.info("Runtime stopped cleanly")


if __name__ == "__main__":
    main()
