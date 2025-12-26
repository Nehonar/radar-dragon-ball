"""Visual theme constants for the radar UI."""

# Passive green palette for uniform panel + grid
BG_BASE = (0, 153, 0)
GRID_LINE = (14, 95, 36)
TRIANGLE = (200, 45, 45)
TEXT = (170, 215, 170)
HUD_BG = (96, 136, 96)

# Layout constants
GRID_SPACING = 20
GRID_THICKNESS = 2
TRIANGLE_LEN = 12

# Target rendering
TARGET_HOT = (255, 190, 37)
TARGET_COLD = BG_BASE
TARGET_SELECTED = (230, 255, 230)
TARGET_RADIUS = 6
TARGET_RADIUS_MIN = 2
TARGET_FADE_SECONDS = 4.0

# View profiles
VIEW_PROFILES = [
    {
        "name": "LIST",
        "grid_spacing": 20,
        "radius_scale": 0.45,
        "hud_view": "LIST",
        "hud_range": "N/A",
        "rssi_min_visible": -100,
        "rssi_max_visible": -30,
        "draw_radar": False,
    },
    {
        "name": "FAR",
        "grid_spacing": 20,
        "radius_scale": 0.55,
        "hud_view": "FAR",
        "hud_range": "WIDE",
        "rssi_min_visible": -100,
        "rssi_max_visible": -30,
        "draw_radar": True,
    },
    {
        "name": "NEAR",
        "grid_spacing": 40,
        "radius_scale": 0.35,
        "hud_view": "NEAR",
        "hud_range": "CLOSE",
        "rssi_min_visible": -50,
        "rssi_max_visible": -30,
        "draw_radar": True,
    },
]
