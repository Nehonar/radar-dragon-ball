"""Runtime orchestrator coordinating scanner and core loop."""

import logging
import signal
import threading
import time
from queue import Empty, Full, Queue
from typing import Optional

from rf_radar.core.tracker import Tracker
from rf_radar.scanners.sim_scanner import SimScanner

logger = logging.getLogger(__name__)


class Runtime:
    """Runtime coordinates scanner and core processing in background threads."""

    def __init__(self, config, observation_queue: Queue, snapshot_queue: Queue) -> None:
        self.config = config
        self.observation_queue = observation_queue
        self.snapshot_queue = snapshot_queue
        self.tracker: Optional[Tracker] = None
        self.scanner: Optional[SimScanner] = None
        self.stop_event = threading.Event()
        self.core_thread: Optional[threading.Thread] = None
        self.core_interval = 1.0 / float(self.config.CORE_TICK_RATE)

    def start(self) -> None:
        """Initialize components and start processing threads."""
        if self.core_thread and self.core_thread.is_alive():
            return

        self.tracker = Tracker(self.config)
        self.scanner = SimScanner(self.observation_queue, self.config, scenario="C", seed=1)
        self.scanner.start()

        self.core_thread = threading.Thread(target=self._core_loop, name="RuntimeCore", daemon=True)
        self.core_thread.start()

    def stop(self) -> None:
        """Signal shutdown and wait for threads to finish."""
        self.stop_event.set()
        if self.scanner:
            self.scanner.stop()
        if self.core_thread:
            self.core_thread.join(timeout=2.0)
        self._drain_queues()

    def is_running(self) -> bool:
        """Return True if runtime is active."""
        return bool(self.core_thread and self.core_thread.is_alive())

    def _core_loop(self) -> None:
        """Core processing loop running in a background thread."""
        while not self.stop_event.is_set():
            iteration_start = time.time()
            obs = None
            try:
                obs = self.observation_queue.get(timeout=self.core_interval)
            except Empty:
                pass

            now_ts = obs.ts if obs else time.time()
            if self.tracker:
                if obs:
                    self.tracker.update(obs)
                self.tracker.tick(now_ts)
                snap = self.tracker.build_snapshot(now_ts)
                self._publish_snapshot(snap)

            elapsed = time.time() - iteration_start
            remaining = self.core_interval - elapsed
            if remaining > 0:
                time.sleep(remaining)

    def _publish_snapshot(self, snap) -> None:
        try:
            self.snapshot_queue.put_nowait(snap)
        except Full:
            try:
                self.snapshot_queue.get_nowait()
            except Empty:
                pass
            try:
                self.snapshot_queue.put_nowait(snap)
            except Full:
                logger.debug("Snapshot queue still full; dropping snapshot.")

    def _drain_queues(self) -> None:
        try:
            while True:
                self.observation_queue.get_nowait()
        except Empty:
            pass
        try:
            while True:
                self.snapshot_queue.get_nowait()
        except Empty:
            pass


def install_signal_handlers(runtime: Runtime) -> None:
    """Register signal handlers to stop the runtime gracefully."""

    def handler(signum, frame):
        logger.info("Signal received (%s); initiating shutdown.", signum)
        runtime.stop()

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
