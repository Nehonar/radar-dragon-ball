"""Factories for application queues."""

from queue import Queue


def create_observation_queue(config) -> Queue:
    """Create the observation queue with configured max size."""
    return Queue(maxsize=config.OBS_QUEUE_MAXSIZE)


def create_snapshot_queue(config) -> Queue:
    """Create the snapshot queue with fixed size of 1 via configuration."""
    return Queue(maxsize=config.SNAPSHOT_QUEUE_MAXSIZE)
