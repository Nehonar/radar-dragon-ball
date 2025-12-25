"""Domain models and contracts for RF Presence Radar."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Set


class ObservationSource(Enum):
    """Sources that can emit observations."""

    WIFI = "WIFI"
    BLE = "BLE"
    SIM = "SIM"


@dataclass(frozen=True)
class Observation:
    """Immutable raw observation produced by scanners."""

    source: ObservationSource
    id: str
    rssi: int
    ts: float
    meta: Optional[Dict[str, Any]] = None


class TargetState(Enum):
    """Lifecycle state of a tracked target."""

    ACTIVE = "ACTIVE"
    STALE = "STALE"
    GONE = "GONE"


class TargetKind(Enum):
    """Classification kind of a target."""

    MOBILE = "MOBILE"
    LAPTOP = "LAPTOP"
    AP = "AP"
    UNKNOWN = "UNKNOWN"


@dataclass
class Target:
    """Mutable internal representation of a tracked target."""

    id: str
    source_mask: Set[ObservationSource]
    rssi_raw_last: int
    rssi_filt: float
    angle_deg: float
    radius_norm: float
    last_seen_ts: float
    state: TargetState
    kind: TargetKind

    def __post_init__(self) -> None:
        if not 0.0 <= self.radius_norm <= 1.0:
            raise ValueError("radius_norm must be between 0 and 1 inclusive.")
