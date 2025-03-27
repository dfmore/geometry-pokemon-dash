# config.py

FULLSCREEN = True

# The "starting" or "windowed" resolution
WIDTH = 1200
HEIGHT = 800

###############################################################################
# Fraction-based shape sizes
###############################################################################
PLATFORM_WIDTH_FRAC = 250 / WIDTH
PLATFORM_HEIGHT_FRAC = 10 / HEIGHT
PLATFORM_EDGE_TOLERANCE = 5

SPIKE_HEIGHT_FRAC = 20 / HEIGHT
SPIKE_COUNT = 20
SPIKE_COLOR = (255, 0, 0)

###############################################################################
# For images that must keep aspect ratio:
###############################################################################
OBSTACLE_WIDTH_FRAC = 40 / WIDTH
COIN_WIDTH_FRAC = 30 / WIDTH
SQUARE_WIDTH_FRAC = 30 / WIDTH

###############################################################################
# Other game constants
###############################################################################
GRAVITY = 1
MIN_JUMP_STRENGTH = 15
MAX_JUMP_STRENGTH = 45
CHARGE_RATE = 1

COYOTE_FRAMES = 5
JUMP_BUFFER_FRAMES = 5

SPEED = 6
LEVEL_DURATION = 100  # seconds

WHITE = (255, 255, 255)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

COLLISION_TOLERANCE = 7

###############################################################################
# Instead of random levels, define 5 fixed levels.
# Each "level" is a dictionary with lists of (x, y) for platforms, obstacles, coins.
# Positions are absolute here; you can use fractional references or do any format you prefer.
###############################################################################

# You can tune these as you wish to increase difficulty (more obstacles, fewer platforms, etc.).
LEVELS = [
    {
        "name": "Level 1 (Easy)",
        "platforms": [
            (100, 600),
            (400, 600),
            (700, 600)
        ],
        "obstacles": [
            # Each obstacle: (x, y) => place exactly at this coordinate
            (300, 560),
            (650, 560)
        ],
        "coins": [
            (350, 550),
            (750, 550)
        ],
    },
    {
        "name": "Level 2 (Slightly Harder)",
        "platforms": [
            (100, 550),
            (400, 520),
            (700, 550)
        ],
        "obstacles": [
            (280, 490),
            (620, 490),
        ],
        "coins": [
            (350, 480),
            (750, 530),
        ],
    },
    {
        "name": "Level 3 (Medium)",
        "platforms": [
            (100, 550),
            (350, 500),
            (600, 530),
            (900, 550),
        ],
        "obstacles": [
            (320, 470),
            (570, 500),
            (800, 520),
        ],
        "coins": [
            (380, 460),
            (640, 490),
            (880, 510),
        ],
    },
    {
        "name": "Level 4 (Hard)",
        "platforms": [
            (100, 550),
            (300, 520),
            (500, 490),
            (750, 520),
            (950, 550),
        ],
        "obstacles": [
            (280, 490),
            (480, 460),
            (700, 490),
            (880, 490),
        ],
        "coins": [
            (250, 480),
            (450, 450),
            (690, 480),
            (900, 480),
        ],
    },
    {
        "name": "Level 5 (Very Hard)",
        "platforms": [
            (100, 530),
            (300, 500),
            (500, 480),
            (700, 500),
            (900, 530),
        ],
        "obstacles": [
            (280, 470),
            (480, 450),
            (680, 470),
            (880, 460),
        ],
        "coins": [
            (230, 460),
            (450, 430),
            (650, 450),
            (860, 440),
        ],
    },
]

# Which level to load (0..4)
CURRENT_LEVEL = 0

###############################################################################
# Unused spawning config from the old random logic
###############################################################################
SPAWN_SAFE_GAP_MIN = 50
SPAWN_SAFE_GAP_MAX = 140
SPAWN_VERTICAL_OFFSET_MIN = -200
SPAWN_VERTICAL_OFFSET_MAX = 200
SPAWN_MIN_PLATFORM_Y = 0.35
SPAWN_MAX_PLATFORM_Y = 0.95
OBSTACLE_SPAWN_CHANCE = 0.8
OBSTACLE_MIN_SPACING = 150
OBSTACLE_MAX_PER_PLATFORM = 1
OBSTACLE_SPAWN_ATTEMPTS = 5
COIN_SPAWN_CHANCE = 0.3
MAX_COINS = 5
COIN_SPAWN_ATTEMPTS = 5
