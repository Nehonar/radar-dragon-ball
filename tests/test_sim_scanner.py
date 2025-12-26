import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rf_radar.core import config
from rf_radar.core.models import ObservationSource
from rf_radar.core.tracker import Tracker
from rf_radar.infrastructure.queues import create_observation_queue
from rf_radar.scanners.sim_scanner import SimScanner


def _first_obs(scanner: SimScanner, step: int):
    return list(scanner._build_observations(step))[0]


def test_reproducible_sequence_with_seed():
    s1 = SimScanner(create_observation_queue(config), config, scenario="B", seed=123, tick_rate=10)
    s2 = SimScanner(create_observation_queue(config), config, scenario="B", seed=123, tick_rate=10)

    seq1 = [_first_obs(s1, i) for i in range(5)]
    seq2 = [_first_obs(s2, i) for i in range(5)]

    assert [(o.id, o.rssi, o.ts) for o in seq1] == [(o.id, o.rssi, o.ts) for o in seq2]


def test_scenarios_emit_valid_observations():
    for scenario in ("A", "B", "C"):
        scanner = SimScanner(create_observation_queue(config), config, scenario=scenario, seed=1, tick_rate=10)
        obs = _first_obs(scanner, 0)
        assert obs.source == ObservationSource.SIM
        assert config.RSSI_MIN <= obs.rssi <= config.RSSI_MAX
        assert obs.meta["scenario"] == scenario


def test_tracker_integration_with_sim_scanner():
    original_interval = getattr(config, "TARGET_UPDATE_INTERVAL", 0.5)
    config.TARGET_UPDATE_INTERVAL = 0.0
    observation_queue = create_observation_queue(config)
    tracker = Tracker(config)
    scanner = SimScanner(observation_queue, config, scenario="C", seed=7, tick_rate=30, start_ts=0.0)

    scanner.start()
    observations = []
    for _ in range(6):
        obs = observation_queue.get(timeout=1.0)
        observations.append(obs)
    scanner.stop()

    radius_first = None
    radius_last = None
    for obs in observations:
        tracker.update(obs)
        tracker.tick(obs.ts)
        radius_last = tracker.targets["sim-move"].radius_norm
        if radius_first is None:
            radius_first = radius_last

    tracker_first = radius_first
    tracker_last = radius_last
    assert tracker_first > tracker_last

    snap = tracker.build_snapshot(now_ts=observations[-1].ts)
    assert isinstance(snap.targets, tuple)
    ids = {t.id for t in snap.targets}
    assert "sim-move" in ids
    assert snap.selected_id == "sim-move"
    config.TARGET_UPDATE_INTERVAL = original_interval
