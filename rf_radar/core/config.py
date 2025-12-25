"""Centralized configuration values for RF Presence Radar."""

# Runtime / Performance
UI_FPS = 30
CORE_TICK_RATE = 10
OBS_QUEUE_MAXSIZE = 256
SNAPSHOT_QUEUE_MAXSIZE = 1

# RSSI / Señal
RSSI_MIN = -100
RSSI_MAX = -20
RSSI_SMOOTHING = 0.5
RSSI_STALE_TIMEOUT = 5.0

# Modos
ENABLE_WIFI = False
ENABLE_BLE = False
ENABLE_SIMULATOR = True

# Logging
LOG_LEVEL = "INFO"
