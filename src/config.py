# config.py

FULLSCREEN = True

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
LEVEL_DURATION = 50  # seconds

WHITE = (255, 255, 255)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

COLLISION_TOLERANCE = 7

###############################################################################
# Define 5 "seeded param-based" levels.
# You can tweak each dictionary's parameters to shape your level.
###############################################################################
LEVELS = [
    {
        "name": "Level 1 (Easy)",
        "seed": 101,
        # We'll still do 1 platform per second
        "safe_gap_min": 50,
        "safe_gap_max": 140,
        "vertical_offset_min": -30,
        "vertical_offset_max": 30,
        "min_platform_y": 450,
        "max_platform_y": 650,

        "obstacle_spawn_chance": 0.5,
        "obstacle_max_per_platform": 1,    # For easy
        "coin_chance": 0.2,  # optional
    },
    {
        "name": "Level 2",
        "seed": 203,
        "safe_gap_min": 50,
        "safe_gap_max": 140,
        "vertical_offset_min": -45,
        "vertical_offset_max": 45,
        "min_platform_y": 300,
        "max_platform_y": 700,

        "obstacle_spawn_chance": 0.4,
        "obstacle_max_per_platform": 2,    # Harder
        "coin_chance": 0.4,
    }
]

# Which level to load
CURRENT_LEVEL = 0

###############################################################################
# (Optional) remove or comment out old random config that is no longer used:
# SPAWN_SAFE_GAP_MIN = 50
# SPAWN_SAFE_GAP_MAX = 140
# SPAWN_VERTICAL_OFFSET_MIN = -200
# SPAWN_VERTICAL_OFFSET_MAX = 200
# SPAWN_MIN_PLATFORM_Y = 0.35
# SPAWN_MAX_PLATFORM_Y = 0.95
# OBSTACLE_SPAWN_CHANCE = 0.8
# OBSTACLE_MIN_SPACING = 150
# OBSTACLE_MAX_PER_PLATFORM = 1
# OBSTACLE_SPAWN_ATTEMPTS = 5
# COIN_SPAWN_CHANCE = 0.3
# MAX_COINS = 5
# COIN_SPAWN_ATTEMPTS = 5
