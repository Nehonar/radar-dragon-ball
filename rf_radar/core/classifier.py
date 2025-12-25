"""Minimal placeholder classifier."""

from rf_radar.core.models import Target, TargetKind


def classify(target: Target) -> TargetKind:
    """Return a placeholder classification for the target."""
    return TargetKind.UNKNOWN
