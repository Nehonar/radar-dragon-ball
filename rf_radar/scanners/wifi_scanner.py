"""WiFi scanner using iw to emit observations."""

import logging
import threading
import time
from queue import Full, Queue
import subprocess
import re

from rf_radar.core.models import Observation, ObservationSource

logger = logging.getLogger(__name__)


class WifiScanner:
    def __init__(self, observation_queue: Queue, config) -> None:
        self.observation_queue = observation_queue
        self.config = config
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None

    def start(self) -> None:
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._run, name="WifiScanner", daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=2.0)

    def _run(self) -> None:
        while not self.stop_event.is_set():
            started = time.time()
            try:
                observations = self._scan()
                logger.debug("WIFI scan: %s devices", len(observations))
                for obs in observations:
                    try:
                        self.observation_queue.put_nowait(obs)
                    except Full:
                        logger.warning("WIFI observation queue full; dropping observation.")
            except Exception as exc:
                logger.error("WIFI scan error: %s", exc)
            elapsed = time.time() - started
            wait_time = max(0.0, self.config.WIFI_SCAN_INTERVAL - elapsed)
            if wait_time > 0:
                self.stop_event.wait(wait_time)

    def _scan(self):
        cmd = ["iw", "dev", self.config.WIFI_INTERFACE, "scan"]
        try:
            output = subprocess.check_output(cmd, timeout=self.config.WIFI_SCAN_TIMEOUT, text=True, stderr=subprocess.STDOUT)
        except Exception as exc:
            logger.error("WIFI scan command failed: %s", exc)
            return []

        observations = []
        bssid = None
        rssi = None
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("BSS "):
                if bssid is not None and rssi is not None:
                    observations.append(self._make_observation(bssid, rssi))
                bssid = line.split(" ")[1].split("(")[0]
                rssi = None
            elif line.startswith("signal:"):
                match = re.search(r"signal:\s*(-?\d+)", line)
                if match:
                    rssi = int(match.group(1))
        if bssid is not None and rssi is not None:
            observations.append(self._make_observation(bssid, rssi))
        return observations

    def _make_observation(self, bssid: str, rssi: int) -> Observation:
        ts = time.time()
        return Observation(
            source=ObservationSource.WIFI,
            id=bssid,
            rssi=rssi,
            ts=ts,
            meta={"scanner": "wifi"},
        )
