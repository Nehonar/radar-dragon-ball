"""HUD rendering for the radar UI."""

import pygame

from rf_radar.ui import theme


def draw_hud(surface: pygame.Surface, font: pygame.font.Font) -> None:
    """Draw a two-line HUD placeholder at the bottom of the screen."""
    width, height = surface.get_size()
    line_height = font.get_linesize()
    hud_height = line_height * 2 + 8
    hud_rect = pygame.Rect(0, height - hud_height, width, hud_height)

    surface.fill(theme.HUD_BG, hud_rect)

    line1 = "MODE:SIM | T:00 | W:00 B:00 | DROP:000"
    line2 = "SEL:NONE"

    text1 = font.render(line1, True, theme.TEXT)
    text2 = font.render(line2, True, theme.TEXT)

    surface.blit(text1, (8, height - hud_height + 4))
    surface.blit(text2, (8, height - hud_height + 4 + line_height))
