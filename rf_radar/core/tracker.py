"""Core tracker for aggregating observations into targets and snapshots."""

import math
from dataclasses import replace
from typing import Dict, Iterable, Tuple

from rf_radar.core import classifier, mapping, snapshot
from rf_radar.core.models import Observation, Target, TargetKind, TargetState


class Tracker:
    """Stateful tracker managing targets derived from observations."""

    def __init__(self, config) -> None:
        self.config = config
        self.targets: Dict[str, Target] = {}

    def update(self, observation: Observation) -> None:
        """Ingest a new observation and update or create the corresponding target."""
        target = self.targets.get(observation.id)

        if target is None:
            angle_rad = mapping.angle_from_id(observation.id)
            angle_deg = math.degrees(angle_rad)
            rssi_filt = observation.rssi
            radius_norm = mapping.radius_from_rssi(rssi_filt, self.config)
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
            return

        alpha = self.config.RSSI_SMOOTHING
        target.rssi_raw_last = observation.rssi
        target.rssi_filt = (1 - alpha) * target.rssi_filt + alpha * observation.rssi
        target.radius_norm = mapping.radius_from_rssi(target.rssi_filt, self.config)
        target.last_seen_ts = observation.ts
        target.state = TargetState.ACTIVE
        target.source_mask.add(observation.source)
        target.kind = classifier.classify(target)

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

    def build_snapshot(self, now_ts: float) -> snapshot.Snapshot:
        """Create an immutable snapshot of the current targets."""
        active_targets: Iterable[Target] = (
            tgt for tgt in self.targets.values() if tgt.state != TargetState.GONE
        )
        # Clone targets to avoid exposing internal mutable instances.
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
