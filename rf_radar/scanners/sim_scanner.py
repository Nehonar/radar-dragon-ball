"""Deterministic simulator scanner emitting observations for testing and development."""

import logging
import threading
import time
from queue import Full, Queue
from random import Random
from typing import Callable, Dict, Iterable

from rf_radar.core.models import Observation, ObservationSource

logger = logging.getLogger(__name__)


class SimScanner:
    """Deterministic simulator that emits observations on a background thread."""

    def __init__(
        self,
        observation_queue: Queue,
        config,
        scenario: str = "A",
        seed: int = 42,
        tick_rate: float = None,
        start_ts: float = 0.0,
    ) -> None:
        self.observation_queue = observation_queue
        self.config = config
        self.seed = seed
        self.random = Random(seed)
        self.scenario = scenario.upper()
        self.tick_rate = tick_rate or float(config.CORE_TICK_RATE)
        self.tick_interval = 1.0 / self.tick_rate
        self.start_ts = start_ts

        self.running = False
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._dropped = 0

        self._scenario_emitters: Dict[str, Callable[[int], Iterable[Observation]]] = {
            "A": self._emit_scenario_a,
            "B": self._emit_scenario_b,
            "C": self._emit_scenario_c,
        }

    def start(self) -> None:
        """Start the simulator thread."""
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Signal the simulator to stop and wait for the thread to finish."""
        if not self.running:
            return
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self.running = False
        self._stop_event.clear()

    def _run(self) -> None:
        """Thread loop emitting observations at a fixed tick rate."""
        step = 0
        while not self._stop_event.is_set():
            for obs in self._build_observations(step):
                try:
                    self.observation_queue.put_nowait(obs)
                except Full:
                    self._dropped += 1
                    if self._dropped % 10 == 1:
                        logger.warning("SimScanner dropped observations: %s", self._dropped)
            step += 1
            time.sleep(self.tick_interval)

    def _build_observations(self, step: int):
        emitter = self._scenario_emitters.get(self.scenario, self._emit_scenario_a)
        return emitter(step)

    def _base_observation(self, obs_id: str, rssi: int, ts: float):
        return Observation(
            source=ObservationSource.SIM,
            id=obs_id,
            rssi=int(rssi),
            ts=ts,
            meta={"scenario": self.scenario},
        )

    def _emit_scenario_a(self, step: int):
        ts = self.start_ts + step * self.tick_interval
        yield self._base_observation("sim-stable", rssi=-60, ts=ts)

    def _emit_scenario_b(self, step: int):
        ids = ("sim-a", "sim-b", "sim-c")
        idx = step % len(ids)
        ts = self.start_ts + step * self.tick_interval
        yield self._base_observation(ids[idx], rssi=-65, ts=ts)

    def _emit_scenario_c(self, step: int):
        ts = self.start_ts + step * self.tick_interval
        cycle = 20
        position = step % cycle
        half = cycle // 2
        if position <= half:
            frac = position / half
            rssi = self.config.RSSI_MIN + frac * (self.config.RSSI_MAX - self.config.RSSI_MIN)
        else:
            frac = (position - half) / half
            rssi = self.config.RSSI_MAX - frac * (self.config.RSSI_MAX - self.config.RSSI_MIN)
        yield self._base_observation("sim-move", rssi=rssi, ts=ts)
