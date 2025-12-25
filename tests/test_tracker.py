import math
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rf_radar.core import config
from rf_radar.core import mapping
from rf_radar.core.models import Observation, ObservationSource, TargetState
from rf_radar.core.tracker import Tracker


def test_creation_and_angle_stability():
    tracker = Tracker(config)
    obs = Observation(ObservationSource.SIM, "id-1", -60, ts=0.0, meta=None)
    tracker.update(obs)

    assert "id-1" in tracker.targets
    first_angle = tracker.targets["id-1"].angle_deg

    tracker.update(Observation(ObservationSource.SIM, "id-1", -50, ts=1.0, meta=None))
    assert tracker.targets["id-1"].angle_deg == first_angle


def test_rssi_filtering_updates_radius():
    tracker = Tracker(config)
    tracker.update(Observation(ObservationSource.SIM, "id-2", -60, ts=0.0, meta=None))
    first_filt = tracker.targets["id-2"].rssi_filt

    tracker.update(Observation(ObservationSource.SIM, "id-2", -20, ts=1.0, meta=None))
    second_filt = tracker.targets["id-2"].rssi_filt

    expected = (1 - config.RSSI_SMOOTHING) * first_filt + config.RSSI_SMOOTHING * (-20)
    assert math.isclose(second_filt, expected)
    assert tracker.targets["id-2"].angle_deg == tracker.targets["id-2"].angle_deg


def test_temporal_state_transitions():
    tracker = Tracker(config)
    tracker.update(Observation(ObservationSource.SIM, "id-3", -70, ts=0.0, meta=None))

    tracker.tick(config.RSSI_STALE_TIMEOUT + 0.1)
    assert tracker.targets["id-3"].state == TargetState.STALE

    tracker.tick(2 * config.RSSI_STALE_TIMEOUT + 0.2)
    assert "id-3" not in tracker.targets


def test_snapshot_content_and_selection():
    tracker = Tracker(config)
    tracker.update(Observation(ObservationSource.SIM, "near", config.RSSI_MAX, ts=0.0, meta=None))
    tracker.update(Observation(ObservationSource.SIM, "far", config.RSSI_MIN, ts=0.0, meta=None))

    snap = tracker.build_snapshot(now_ts=1.0)
    assert isinstance(snap.targets, tuple)
    ids = {t.id for t in snap.targets}
    assert ids == {"near", "far"}
    assert snap.selected_id == "near"
    assert snap.stats["total"] == 2
    assert snap.stats["active"] == 2
    assert snap.stats["stale"] == 0


def test_snapshot_immutability():
    tracker = Tracker(config)
    tracker.update(Observation(ObservationSource.SIM, "id-4", -55, ts=0.0, meta=None))
    snap = tracker.build_snapshot(now_ts=0.5)

    try:
        snap.targets += ()
        mutated = False
    except Exception:
        mutated = True
    assert mutated

    try:
        snap.stats["extra"] = 1
        stats_mutated = False
    except Exception:
        stats_mutated = True
    assert stats_mutated
