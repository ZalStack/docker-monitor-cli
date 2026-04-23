"""Constants used throughout the application."""

# Application version
VERSION = "1.0.0"

# Docker connection settings
DOCKER_BASE_URL = "unix://var/run/docker.sock"
DOCKER_VERSION = "auto"

# Monitoring defaults
DEFAULT_REFRESH_INTERVAL = 2  # seconds
MAX_CONTAINER_NAME_LENGTH = 20

# Display settings
TABLE_STYLE = "bold cyan"
PROGRESS_BAR_WIDTH = 40

# Units for size formatting
SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

# Emojis for visual feedback
SUCCESS_EMOJI = "✅"
ERROR_EMOJI = "❌"
WARNING_EMOJI = "⚠️"
INFO_EMOJI = "ℹ️"
DOCKER_EMOJI = "🐳"

# Container states
CONTAINER_STATE_RUNNING = "running"
CONTAINER_STATE_STOPPED = "exited"
CONTAINER_STATE_PAUSED = "paused"
CONTAINER_STATE_RESTARTING = "restarting"
CONTAINER_STATE_DEAD = "dead"

# Color mapping for container states
STATUS_COLORS = {
    CONTAINER_STATE_RUNNING: "green",
    CONTAINER_STATE_STOPPED: "red",
    CONTAINER_STATE_PAUSED: "yellow",
    CONTAINER_STATE_RESTARTING: "blue",
    CONTAINER_STATE_DEAD: "grey",
    "created": "cyan",
    "removing": "magenta"
}

# Timeout defaults
DEFAULT_STOP_TIMEOUT = 10
DEFAULT_RESTART_TIMEOUT = 10

# Log settings
DEFAULT_LOG_TAIL = 100
MAX_LOG_LINES = 10000