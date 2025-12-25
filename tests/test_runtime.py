import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rf_radar.app.runtime import Runtime
from rf_radar.core import config
from rf_radar.infrastructure.queues import create_observation_queue, create_snapshot_queue


def test_runtime_produces_snapshots_and_stops_cleanly():
    observation_queue = create_observation_queue(config)
    snapshot_queue = create_snapshot_queue(config)
    runtime = Runtime(config, observation_queue, snapshot_queue)

    runtime.start()
    snap = snapshot_queue.get(timeout=2.0)
    assert snap is not None
    assert runtime.is_running()

    runtime.stop()
    time.sleep(0.1)
    assert not runtime.is_running()
    if runtime.core_thread:
        assert not runtime.core_thread.is_alive()
