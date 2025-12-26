"""Input handling for radar UI."""

import pygame


def handle_events(current_index: int, total_views: int) -> tuple[bool, int]:
    """Process pygame events; returns (running, new_view_index)."""
    running = True
    view_index = current_index
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_c:
                view_index = (view_index + 1) % total_views
    return running, view_index
