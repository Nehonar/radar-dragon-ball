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


def draw_grid(surface: pygame.Surface, spacing: int) -> None:
    """Draw grid lines across the radar panel."""
    width, height = surface.get_size()
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


def _filter_targets_for_view(snap, view_profile: dict):
    rssi_min = view_profile.get("rssi_min_visible", -100)
    filtered = []
    for target in snap.targets:
        try:
            if target.rssi_filt < rssi_min and target.state == TargetState.ACTIVE:
                continue
        except Exception:
            pass
        filtered.append(target)
    return filtered


def _render_targets(surface: pygame.Surface, snap, view_profile: dict) -> int:
    width, height = surface.get_size()
    cx = width // 2
    cy = height // 2
    max_radius = min(width, height) * view_profile.get("radius_scale", 0.45)
    fade_seconds = getattr(config, "TARGET_UPDATE_INTERVAL", theme.TARGET_FADE_SECONDS)
    rssi_min = view_profile.get("rssi_min_visible", -100)
    rssi_max = view_profile.get("rssi_max_visible", -30)

    filtered = _filter_targets_for_view(snap, view_profile)

    for target in filtered:
        if target.state == TargetState.GONE:
            continue
        angle_rad = math.radians(target.angle_deg)
        rssi = getattr(target, "rssi_filt", None)
        if rssi is None:
            continue
        norm = (rssi_max - max(rssi_min, min(rssi_max, rssi))) / max(1e-6, (rssi_max - rssi_min))
        radius_px = norm * max_radius
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
    return len(filtered)


def _render_list(surface: pygame.Surface, font, snap) -> None:
    surface.fill(theme.BG_BASE)
    if not snap:
        return
    header = "ID        SRC  RSSI  BAND  ST"
    surface.blit(font.render(header, True, theme.TEXT), (12, 12))
    for idx, tgt in enumerate(snap.targets):
        src = getattr(tgt, "source_mask", None)
        src_label = " ".join(s.value for s in src) if src else "N/A"
        rssi = getattr(tgt, "rssi_filt", getattr(tgt, "rssi_raw_last", 0))
        band = getattr(tgt, "state", None)
        state_label = band.name[0] if band else "?"
        line = f"{tgt.id[:10]:10} {src_label:3} {int(rssi):4}  --   {state_label}"
        surface.blit(font.render(line, True, theme.TEXT), (12, 12 + (idx + 1) * font.get_linesize()))


def render(surface: pygame.Surface, view_profile: dict, snap, font) -> int:
    """Render according to view profile; returns count of rendered targets."""
    draw_background(surface)
    if view_profile.get("draw_radar", True):
        draw_grid(surface, view_profile.get("grid_spacing", theme.GRID_SPACING))
        draw_crosshair(surface)
        if snap:
            return _render_targets(surface, snap, view_profile)
    else:
        _render_list(surface, font, snap)
    return snap.stats.get("total", 0) if snap else 0
