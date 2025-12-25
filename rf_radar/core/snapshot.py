"""Immutable snapshot structure sent from Core to UI."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple


@dataclass(frozen=True)
class Snapshot:
    """Immutable view of the radar state."""

    targets: Tuple[Any, ...] = field(default_factory=tuple)
    stats: Mapping[str, Any] = field(default_factory=dict)
    selected_id: Optional[str] = None
    now_ts: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "targets", tuple(self.targets))
        object.__setattr__(self, "stats", MappingProxyType(dict(self.stats)))
