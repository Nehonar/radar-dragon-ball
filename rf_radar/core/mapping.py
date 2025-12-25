"""Pure mapping utilities for angle and position calculations."""

import hashlib
import math
from typing import Tuple


def angle_from_id(id: str) -> float:
    """Deterministically map an identifier to an angle in radians within [0, 2π)."""
    digest = hashlib.sha256(id.encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], byteorder="big", signed=False)
    fraction = (value % (1 << 64)) / float(1 << 64)
    return fraction * (2 * math.pi)


def radius_from_rssi(rssi: int, config) -> float:
    """Normalize RSSI into a radial distance in [0.0, 1.0]; higher RSSI yields smaller radius."""
    rssi_clamped = max(config.RSSI_MIN, min(config.RSSI_MAX, rssi))
    span = config.RSSI_MAX - config.RSSI_MIN
    if span == 0:
        return 1.0
    normalized = (config.RSSI_MAX - rssi_clamped) / span
    return max(0.0, min(1.0, normalized))


def polar_to_cartesian(angle: float, radius: float) -> Tuple[float, float]:
    """Convert polar coordinates (radians, normalized radius) to 2D cartesian (x, y)."""
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    return (x, y)
