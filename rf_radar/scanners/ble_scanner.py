"""BLE scanner using bleak to emit observations."""

import asyncio
import logging
import threading
import time
from queue import Full, Queue

from rf_radar.core.models import Observation, ObservationSource

logger = logging.getLogger(__name__)


class BleScanner:
    def __init__(self, observation_queue: Queue, config) -> None:
        self.observation_queue = observation_queue
        self.config = config
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None

    def start(self) -> None:
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._run, name="BleScanner", daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=2.0)

    def _run(self) -> None:
        while not self.stop_event.is_set():
            started = time.time()
            try:
                observations = asyncio.run(self._scan_once())
                logger.debug("BLE scan: %s devices", len(observations))
                for obs in observations:
                    try:
                        self.observation_queue.put_nowait(obs)
                    except Full:
                        logger.warning("BLE observation queue full; dropping observation.")
            except Exception as exc:
                logger.error("BLE scan error: %s", exc)
            elapsed = time.time() - started
            wait_time = max(0.0, self.config.BLE_SCAN_INTERVAL - elapsed)
            if wait_time > 0:
                self.stop_event.wait(wait_time)

    async def _scan_once(self):
        from bleak import BleakScanner

        devices = await BleakScanner.discover(timeout=self.config.BLE_SCAN_TIMEOUT)
        observations = []
        ts = time.time()
        for dev in devices:
            rssi = getattr(dev, "rssi", None)
            if rssi is None:
                rssi = dev.metadata.get("rssi") if hasattr(dev, "metadata") else None
            if rssi is None:
                continue
            observations.append(
                Observation(
                    source=ObservationSource.BLE,
                    id=str(dev.address),
                    rssi=int(rssi),
                    ts=ts,
                    meta={"name": dev.name or "", "scanner": "ble"},
                )
            )
        return observations
