"""Radar background, grid, and central marker rendering."""

import pygame

from rf_radar.ui import theme


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


def render(surface: pygame.Surface) -> None:
    """Render the radar background, grid, and central triangle."""
    draw_background(surface)
    draw_grid(surface)
    draw_crosshair(surface)
