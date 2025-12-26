"""Pygame UI consuming snapshots from the runtime."""

import logging
import sys

import pygame

from rf_radar.app.runtime import Runtime
from rf_radar.core import config
from rf_radar.infrastructure import queues
from rf_radar.infrastructure.logging import setup_logging
from rf_radar.ui import hud, radar_view

logger = logging.getLogger(__name__)


def run(width: int = 400, height: int = 400, fps: int = None) -> None:
    """Run the radar UI loop consuming snapshots."""
    setup_logging(config)
    pygame.init()
    pygame.display.set_caption("RF Presence Radar")
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 18)
    target_fps = fps or config.UI_FPS

    observation_queue = queues.create_observation_queue(config)
    snapshot_queue = queues.create_snapshot_queue(config)
    runtime = Runtime(config, observation_queue, snapshot_queue)
    runtime.start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        try:
            snap = snapshot_queue.get_nowait()
            radar_view.set_snapshot(snap)
        except Exception:
            pass

        radar_view.render(screen)
        hud.draw_hud(screen, font)

        pygame.display.flip()
        clock.tick(target_fps)

    runtime.stop()
    pygame.quit()


if __name__ == "__main__":
    run()
