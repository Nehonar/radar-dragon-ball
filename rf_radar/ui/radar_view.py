"""Radar background, grid, and target rendering."""

import logging
import math
import time
from typing import Optional

import pygame

from rf_radar.core import config, mapping
from rf_radar.core.models import TargetState
from rf_radar.ui import theme

logger = logging.getLogger(__name__)


def draw_background(surface: pygame.Surface) -> None:
    """Fill the entire radar area with a uniform base color."""
    surface.fill(theme.BG_BASE)


def draw_grid(surface: pygame.Surface) -> None:
    """Draw grid lines across the radar panel."""
    width, height = surface.get_size()
    spacing = theme.GRID_SPACING
    thickness = theme.GRID_THICKNESS

    for x in range(0, width, spacing):
        pygame.draw.line(surface, theme.GRID_LINE, (x, 0), (x, height), thickness)
    for y in range(0, height, spacing):
        pygame.draw.line(surface, theme.GRID_LINE, (0, y), (width, y), thickness)


def draw_crosshair(surface: pygame.Surface) -> None:
    """Draw a small central triangle marker."""
    width, height = surface.get_size()
    cx = width // 2
    cy = height // 2
    half_len = theme.TRIANGLE_LEN // 2

    points = [
        (cx, cy - half_len),
        (cx - half_len, cy + half_len),
        (cx + half_len, cy + half_len),
    ]
    pygame.draw.polygon(surface, theme.TRIANGLE, points)


def _blend(color_from, color_to, factor: float):
    factor = max(0.0, min(1.0, factor))
    return tuple(
        int(a + (b - a) * factor)
        for a, b in zip(color_from, color_to)
    )


_last_snapshot = None
_last_snapshot_walltime: Optional[float] = None
_target_reset_seen_ts = {}
_target_reset_walltime = {}


def set_snapshot(snap) -> None:
    global _last_snapshot
    global _last_snapshot_walltime
    global _target_reset_seen_ts
    global _target_reset_walltime
    _last_snapshot = snap
    _last_snapshot_walltime = time.time()
    current_ids = set()
    for t in snap.targets:
        current_ids.add(t.id)
        prev_seen = _target_reset_seen_ts.get(t.id, float("-inf"))
        if t.last_seen_ts - prev_seen >= getattr(config, "TARGET_UPDATE_INTERVAL", 0.0):
            _target_reset_seen_ts[t.id] = t.last_seen_ts
            _target_reset_walltime[t.id] = _last_snapshot_walltime
    for known_id in list(_target_reset_seen_ts.keys()):
        if known_id not in current_ids:
            _target_reset_seen_ts.pop(known_id, None)
            _target_reset_walltime.pop(known_id, None)


def _render_targets(surface: pygame.Surface, snap) -> None:
    width, height = surface.get_size()
    cx = width // 2
    cy = height // 2
    max_radius = min(width, height) * 0.45
    fade_seconds = getattr(config, "TARGET_UPDATE_INTERVAL", theme.TARGET_FADE_SECONDS)

    for target in snap.targets:
        if target.state == TargetState.GONE:
            continue
        angle_rad = math.radians(target.angle_deg)
        radius_px = target.radius_norm * max_radius
        x_norm, y_norm = mapping.polar_to_cartesian(angle_rad, radius_px)
        x = int(cx + x_norm)
        y = int(cy + y_norm)

        last_seen_wall = _target_reset_walltime.get(target.id, _last_snapshot_walltime or time.time())
        age = max(0.0, time.time() - last_seen_wall)
        fade = max(0.0, 1.0 - age / fade_seconds) if fade_seconds > 0 else 0.0
        if fade <= 0.0:
            continue

        alpha = int(255 * fade)
        if snap.selected_id and snap.selected_id == target.id:
            alpha = min(255, int(alpha * 1.2))

        radius = max(
            theme.TARGET_RADIUS_MIN,
            int(round(theme.TARGET_RADIUS_MIN + (theme.TARGET_RADIUS - theme.TARGET_RADIUS_MIN) * fade)),
        )
        diameter = radius * 2
        temp = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(
            temp,
            (*theme.TARGET_HOT, alpha),
            (radius, radius),
            radius,
        )
        surface.blit(temp, (x - radius, y - radius))
        logger.debug(
            "UI_DRAW id=%s age=%.2f fade=%.2f alpha=%s radius=%s pos=(%s,%s)",
            target.id,
            age,
            fade,
            alpha,
            radius,
            x,
            y,
        )


def render(surface: pygame.Surface) -> None:
    """Render the radar background, grid, center marker, and targets."""
    draw_background(surface)
    draw_grid(surface)
    draw_crosshair(surface)
    if _last_snapshot:
        _render_targets(surface, _last_snapshot)
