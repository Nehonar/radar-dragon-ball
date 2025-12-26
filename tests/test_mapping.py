import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rf_radar.core import config
from rf_radar.core import mapping


def test_angle_is_deterministic():
    angle = mapping.angle_from_id("device-123")
    assert mapping.angle_from_id("device-123") == angle


def test_angles_are_generally_distinct_for_different_ids():
    angle_a = mapping.angle_from_id("alpha")
    angle_b = mapping.angle_from_id("beta")
    assert angle_a != angle_b


def test_radius_constant_within_band():
    r1 = mapping.radius_from_rssi(-85, config)
    r2 = mapping.radius_from_rssi(-82, config)
    assert r1 == r2


def test_radius_changes_when_band_changes():
    r1 = mapping.radius_from_rssi(-85, config)  # band 1
    r2 = mapping.radius_from_rssi(-70, config)  # band 2
    assert r1 != r2
    assert r2 < r1


def test_radius_from_rssi_extremes():
    high = mapping.radius_from_rssi(config.RSSI_MAX + 10, config)
    low = mapping.radius_from_rssi(config.RSSI_MIN - 10, config)
    assert high == config.RADII_NORMALIZED[-1]
    assert low == config.RADII_NORMALIZED[0]


def test_polar_to_cartesian_preserves_radius():
    angle = 1.234
    radius = 0.7
    x, y = mapping.polar_to_cartesian(angle, radius)
    assert math.isclose(math.hypot(x, y), radius, rel_tol=1e-9, abs_tol=1e-9)
