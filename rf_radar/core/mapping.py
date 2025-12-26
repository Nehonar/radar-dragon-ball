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


def radius_from_rssi_band(rssi: int, config) -> Tuple[float, int]:
    """Map RSSI into a quantized radius and return its band index."""
    rssi_clamped = max(config.RSSI_MIN, min(config.RSSI_MAX, rssi))
    bands = config.RSSI_BANDS
    radii = config.RADII_NORMALIZED

    for idx, ((low, high), radius) in enumerate(zip(bands, radii)):
        if low <= rssi_clamped <= high:
            return radius, idx

    if rssi_clamped < bands[0][0]:
        return radii[0], 0
    return radii[-1], len(radii) - 1


def radius_from_rssi(rssi: int, config) -> float:
    """Map RSSI into a quantized radius based on configured bands."""
    radius, _ = radius_from_rssi_band(rssi, config)
    return radius


def polar_to_cartesian(angle: float, radius: float) -> Tuple[float, float]:
    """Convert polar coordinates (radians, normalized radius) to 2D cartesian (x, y)."""
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    return (x, y)
