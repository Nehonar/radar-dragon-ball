import logging
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rf_radar.core import config
from rf_radar.core.models import Observation, ObservationSource
from rf_radar.core.tracker import Tracker


def test_radius_updates_only_after_interval_and_band_change():
    original_interval = config.TARGET_UPDATE_INTERVAL
    config.TARGET_UPDATE_INTERVAL = 1.0
    tracker = Tracker(config)

    tracker.update(Observation(ObservationSource.SIM, "id-band", -85, ts=0.0, meta=None))
    radius_initial = tracker.targets["id-band"].radius_norm

    tracker.update(Observation(ObservationSource.SIM, "id-band", -40, ts=0.2, meta=None))
    assert tracker.targets["id-band"].radius_norm == radius_initial

    tracker.update(Observation(ObservationSource.SIM, "id-band", -40, ts=1.1, meta=None))
    assert tracker.targets["id-band"].radius_norm != radius_initial

    config.TARGET_UPDATE_INTERVAL = original_interval


def test_radius_stays_within_band_even_after_interval():
    original_interval = config.TARGET_UPDATE_INTERVAL
    config.TARGET_UPDATE_INTERVAL = 0.1
    tracker = Tracker(config)

    tracker.update(Observation(ObservationSource.SIM, "id-band2", -85, ts=0.0, meta=None))
    radius_initial = tracker.targets["id-band2"].radius_norm

    tracker.update(Observation(ObservationSource.SIM, "id-band2", -83, ts=0.2, meta=None))
    assert tracker.targets["id-band2"].radius_norm == radius_initial

    config.TARGET_UPDATE_INTERVAL = original_interval


def test_debug_logging_emitted_when_enabled(caplog):
    original_debug = getattr(config, "TARGET_DEBUG_LOG", False)
    original_log_interval = getattr(config, "TARGET_LOG_INTERVAL", 0.0)
    config.TARGET_DEBUG_LOG = True
    config.TARGET_LOG_INTERVAL = 0.0
    tracker = Tracker(config)

    with caplog.at_level(logging.DEBUG, logger="rf_radar.core.tracker"):
        tracker.update(Observation(ObservationSource.SIM, "id-log", -60, ts=0.0, meta=None))
    assert any("TARGET id=id-log" in rec.message for rec in caplog.records)

    config.TARGET_DEBUG_LOG = original_debug
    config.TARGET_LOG_INTERVAL = original_log_interval
