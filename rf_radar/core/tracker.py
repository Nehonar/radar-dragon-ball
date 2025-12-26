"""Core tracker for aggregating observations into targets and snapshots."""

import logging
import math
from dataclasses import replace
from typing import Dict, Iterable, Tuple

from rf_radar.core import classifier, mapping, snapshot
from rf_radar.core.models import Observation, Target, TargetKind, TargetState

logger = logging.getLogger(__name__)


class Tracker:
    """Stateful tracker managing targets derived from observations."""

    def __init__(self, config) -> None:
        self.config = config
        self.targets: Dict[str, Target] = {}
        self._target_bands: Dict[str, int] = {}
        self._last_radius_update_ts: Dict[str, float] = {}
        self._last_log_ts: Dict[str, float] = {}

    def update(self, observation: Observation) -> None:
        """Ingest a new observation and update or create the corresponding target."""
        target = self.targets.get(observation.id)

        if target is None:
            angle_rad = mapping.angle_from_id(observation.id)
            angle_deg = math.degrees(angle_rad)
            rssi_filt = observation.rssi
            radius_norm, band_idx = mapping.radius_from_rssi_band(rssi_filt, self.config)
            target = Target(
                id=observation.id,
                source_mask={observation.source},
                rssi_raw_last=observation.rssi,
                rssi_filt=rssi_filt,
                angle_deg=angle_deg,
                radius_norm=radius_norm,
                last_seen_ts=observation.ts,
                state=TargetState.ACTIVE,
                kind=TargetKind.UNKNOWN,
            )
            target.kind = classifier.classify(target)
            self.targets[observation.id] = target
            self._target_bands[observation.id] = band_idx
            self._last_radius_update_ts[observation.id] = observation.ts
            self._maybe_log_debug(
                observation.id,
                observation.source.value,
                observation.rssi,
                rssi_filt,
                band_idx,
                radius_norm,
                radius_norm,
                0.0,
                observation.ts,
            )
            return

        prev_radius = target.radius_norm
        alpha = self.config.RSSI_SMOOTHING
        target.rssi_raw_last = observation.rssi
        target.rssi_filt = (1 - alpha) * target.rssi_filt + alpha * observation.rssi
        radius_norm, band_idx = mapping.radius_from_rssi_band(target.rssi_filt, self.config)
        target.last_seen_ts = observation.ts
        target.state = TargetState.ACTIVE
        target.source_mask.add(observation.source)
        target.kind = classifier.classify(target)

        last_band = self._target_bands.get(observation.id, band_idx)
        last_update = self._last_radius_update_ts.get(observation.id, float("-inf"))
        elapsed = observation.ts - last_update
        should_update_radius = (
            band_idx != last_band and elapsed >= self.config.TARGET_UPDATE_INTERVAL
        )

        if should_update_radius:
            target.radius_norm = radius_norm
            self._target_bands[observation.id] = band_idx
            self._last_radius_update_ts[observation.id] = observation.ts

        delta_radius = target.radius_norm - prev_radius
        self._maybe_log_debug(
            observation.id,
            observation.source.value,
            observation.rssi,
            target.rssi_filt,
            self._target_bands.get(observation.id, band_idx),
            target.radius_norm,
            prev_radius,
            delta_radius,
            observation.ts,
        )

    def tick(self, now_ts: float) -> None:
        """Advance time-dependent state of targets."""
        to_delete = []
        stale_timeout = self.config.RSSI_STALE_TIMEOUT
        for target_id, target in self.targets.items():
            age = now_ts - target.last_seen_ts
            if age > 2 * stale_timeout:
                target.state = TargetState.GONE
                to_delete.append(target_id)
            elif age > stale_timeout:
                target.state = TargetState.STALE
        for target_id in to_delete:
            del self.targets[target_id]
            self._target_bands.pop(target_id, None)
            self._last_radius_update_ts.pop(target_id, None)
            self._last_log_ts.pop(target_id, None)

    def build_snapshot(self, now_ts: float) -> snapshot.Snapshot:
        """Create an immutable snapshot of the current targets."""
        active_targets: Iterable[Target] = (
            tgt for tgt in self.targets.values() if tgt.state != TargetState.GONE
        )
        cloned_targets: Tuple[Target, ...] = tuple(replace(tgt) for tgt in active_targets)

        selected_id = None
        if cloned_targets:
            closest = min(cloned_targets, key=lambda t: t.radius_norm)
            selected_id = closest.id

        stats = {
            "total": len(cloned_targets),
            "active": sum(1 for t in cloned_targets if t.state == TargetState.ACTIVE),
            "stale": sum(1 for t in cloned_targets if t.state == TargetState.STALE),
        }

        return snapshot.Snapshot(
            targets=cloned_targets,
            stats=stats,
            selected_id=selected_id,
            now_ts=now_ts,
        )

    def _maybe_log_debug(
        self,
        target_id: str,
        source: str,
        rssi_raw: int,
        rssi_filt: float,
        band_idx: int,
        radius: float,
        prev_radius: float,
        delta_radius: float,
        ts: float,
    ) -> None:
        if not getattr(self.config, "TARGET_DEBUG_LOG", False):
            return
        last_log = self._last_log_ts.get(target_id, float("-inf"))
        if ts - last_log < getattr(self.config, "TARGET_LOG_INTERVAL", 0.0):
            return
        self._last_log_ts[target_id] = ts
        logger.debug(
            "TARGET id=%s src=%s rssi=%s filt=%.2f band=%s radius=%.3f prev=%.3f Δ=%.3f ts=%.3f",
            target_id,
            source,
            rssi_raw,
            rssi_filt,
            band_idx,
            radius,
            prev_radius,
            delta_radius,
            ts,
        )
