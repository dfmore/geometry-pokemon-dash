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
LEVEL_DURATION = 40  # seconds

WHITE = (255, 255, 255)
RED   = (255,   0,   0)
BLUE  = (  0,   0, 255)
GREEN = (  0, 255,   0)
BLACK = (  0,   0,   0)

COLLISION_TOLERANCE = 7

###############################################################################
# Define 5 "seeded param-based" levels.
###############################################################################
LEVELS = [
    {
        "name": "Level 1 (Easy)",
        "seed": 101,
        "safe_gap_min": 50,
        "safe_gap_max": 140,
        "vertical_offset_min": -30,
        "vertical_offset_max": 30,
        "min_platform_y": 450,
        "max_platform_y": 650,
        "obstacle_spawn_chance": 0.5,
        "obstacle_max_per_platform": 1,
        "coin_chance": 0.4,
    },
    {
        "name": "Level 2",
        "seed": 203,
        "safe_gap_min": 50,
        "safe_gap_max": 140,
        "vertical_offset_min": -45,
        "vertical_offset_max": 45,
        "min_platform_y": 400,
        "max_platform_y": 800,
        "obstacle_spawn_chance": 0.4,
        "obstacle_max_per_platform": 2,
        "coin_chance": 0.4,
    },
    {
        "name": "Level 3",
        "seed": 304,
        "safe_gap_min": 60,
        "safe_gap_max": 150,
        "vertical_offset_min": -75,
        "vertical_offset_max": 75,
        "min_platform_y": 450,
        "max_platform_y": 800,
        "obstacle_spawn_chance": 0.4,
        "obstacle_max_per_platform": 2,
        "coin_chance": 0.4,
    },
    {
        "name": "Level 4",
        "seed": 404,
        "safe_gap_min": 50,
        "safe_gap_max": 170,
        "vertical_offset_min": -95,
        "vertical_offset_max": 95,
        "min_platform_y": 250,
        "max_platform_y": 900,
        "obstacle_spawn_chance": 0.5,
        "obstacle_max_per_platform": 1,
        "coin_chance": 0.4,
    },
    {
        "name": "Level 5",
        "seed": 507,
        "safe_gap_min": 70,
        "safe_gap_max": 180,
        "vertical_offset_min": -135,
        "vertical_offset_max": 135,
        "min_platform_y": 200,
        "max_platform_y": 1100,
        "obstacle_spawn_chance": 0.7,
        "obstacle_max_per_platform": 2,
        "coin_chance": 0.3,
    }
]

# Which level to load
CURRENT_LEVEL = 0
