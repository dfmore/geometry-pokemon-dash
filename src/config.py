# config.py

WIDTH = 800
HEIGHT = 400
SQUARE_SIZE = 30
GRAVITY = 1
MIN_JUMP_STRENGTH = 15
MAX_JUMP_STRENGTH = 45
CHARGE_RATE = 1
GROUND_HEIGHT = HEIGHT - 50
OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 40
SPEED = 5
PLATFORM_WIDTH = 250
PLATFORM_HEIGHT = 10
SPIKE_HEIGHT = 20
COIN_SIZE = 30
LEVEL_DURATION = 100  # seconds

# Colors
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Collision tolerance
COLLISION_TOLERANCE = 5

######################################################################################
# NEW: spawning-related parameters (moved here from the game or other hard-coded logic)
######################################################################################
SPAWN_SAFE_GAP_MIN = 50
SPAWN_SAFE_GAP_MAX = 140

SPAWN_VERTICAL_OFFSET_MIN = -5
SPAWN_VERTICAL_OFFSET_MAX = 10

SPAWN_MIN_PLATFORM_Y = 310
SPAWN_MAX_PLATFORM_Y = 340

OBSTACLE_SPAWN_CHANCE = 0.5
OBSTACLE_MIN_SPACING = 150
OBSTACLE_MAX_PER_PLATFORM = 2
OBSTACLE_SPAWN_ATTEMPTS = 10

COIN_SPAWN_CHANCE = 0.3
MAX_COINS = 3
COIN_SPAWN_ATTEMPTS = 5
