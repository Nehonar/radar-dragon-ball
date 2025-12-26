"""Minimal standalone Pygame UI for the radar."""

import logging
import sys

import pygame

from rf_radar.core import config
from rf_radar.ui import hud, radar_view

logger = logging.getLogger(__name__)


def run(width: int = 240, height: int = 240, fps: int = None) -> None:
    """Run the minimal radar UI loop."""
    pygame.init()
    pygame.display.set_caption("RF Presence Radar")
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 18)
    target_fps = fps or config.UI_FPS

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        radar_view.render(screen)
        hud.draw_hud(screen, font)

        pygame.display.flip()
        clock.tick(target_fps)

    pygame.quit()


if __name__ == "__main__":
    run()
