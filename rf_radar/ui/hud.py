"""HUD rendering for the radar UI."""

import pygame

from rf_radar.ui import theme


def _render_text(surface, font, text, x, y):
    surface.blit(font.render(text, True, theme.TEXT), (x, y))


def draw_hud(surface: pygame.Surface, font: pygame.font.Font, view_profile: dict, snap, rendered_count: int) -> None:
    """Draw HUD with view info and optional target list."""
    width, height = surface.get_size()
    line_height = font.get_linesize()
    max_lines = 6
    hud_height = line_height * max_lines + 8
    hud_rect = pygame.Rect(0, height - hud_height, width, hud_height)

    surface.fill(theme.HUD_BG, hud_rect)

    view_name = view_profile.get("name", "N/A")
    range_label = view_profile.get("hud_range", "BASE")
    total = rendered_count
    selected = snap.selected_id if snap else "NONE"
    rssi_min = view_profile.get("rssi_min_visible", None)
    rssi_max = view_profile.get("rssi_max_visible", None)
    rssi_range = f"{rssi_min}..{rssi_max}" if rssi_min is not None and rssi_max is not None else "N/A"

    line1 = f"VIEW:{view_name} | RSSI:{rssi_range} | T:{total:02d}"
    line2 = f"SEL:{selected or 'NONE'}"
    _render_text(surface, font, line1, 8, height - hud_height + 4)
    _render_text(surface, font, line2, 8, height - hud_height + 4 + line_height)

    if snap and view_name == "LIST":
        base_y = height - hud_height + 4 + line_height * 2
        for idx, tgt in enumerate(snap.targets, start=1):
            src = getattr(tgt, "source_mask", None)
            src_label = " ".join(s.value for s in src) if src else "N/A"
            rssi = getattr(tgt, "rssi_filt", getattr(tgt, "rssi_raw_last", 0))
            band_idx = getattr(tgt, "state", None)
            band_label = band_idx.name[0] if band_idx else "?"
            state_label = tgt.state.name[0] if hasattr(tgt, "state") else "?"
            row = f"{idx:02d} {tgt.id[:10]:10} {src_label:3} {int(rssi):4}  {band_label}  {state_label}"
            _render_text(surface, font, row, 8, base_y + line_height * (idx - 1))
