# config.py
#
# Approach 2: fraction-based scaling for shapes, plus a consistent "desired" width/height
# that gets overridden in main.py if you go fullscreen. We removed old absolute
# constants for platform/obstacle/coin sizes and replaced them with fraction-based
# or ratio-based logic.

FULLSCREEN = True

# The "starting" or "windowed" resolution
WIDTH = 1200
HEIGHT = 800

###############################################################################
# Fraction-based shape sizes
###############################################################################
# For example, if you used 250 px on a 1200 px-wide screen for platform width,
# that's about 0.2083. We'll store it as a fraction. Similarly for heights.
PLATFORM_WIDTH_FRAC = 250/1200.0
PLATFORM_HEIGHT_FRAC = 10/800.0

SPIKE_HEIGHT_FRAC = 20/800.0  # e.g. 20 px on an 800-tall screen -> 0.025
SPIKE_COUNT = 20
SPIKE_COLOR = (255, 0, 0)  # bright red

###############################################################################
# For images that must keep aspect ratio:
# We'll scale obstacles by OBSTACLE_WIDTH_FRAC * actual window width,
# then derive height from the image's aspect ratio.
###############################################################################
OBSTACLE_WIDTH_FRAC = 40/1200.0  # e.g. 40 px on a 1200 px width -> ~0.0333
# We'll skip an explicit OBSTACLE_HEIGHT_FRAC so we can preserve ratio automatically.

COIN_WIDTH_FRAC = 30/1200.0  # e.g. 30 px on a 1200 px width -> 0.025
# We'll skip an explicit height fraction for coins, too, to preserve ratio.

SQUARE_WIDTH_FRAC = 30/1200.0  # Player's square width fraction.
# We'll also skip height fraction for the player's rectangle if we want it truly "square."

###############################################################################
# Other game constants
###############################################################################
GRAVITY = 1
MIN_JUMP_STRENGTH = 15
MAX_JUMP_STRENGTH = 45
CHARGE_RATE = 1
SPEED = 5

LEVEL_DURATION = 100  # seconds

WHITE = (255, 255, 255)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

COLLISION_TOLERANCE = 5

###############################################################################
# Spawning / platform / obstacle config
###############################################################################
SPAWN_SAFE_GAP_MIN = 50
SPAWN_SAFE_GAP_MAX = 140

# Keep the vertical offsets in absolute pixels if you like random lumps
SPAWN_VERTICAL_OFFSET_MIN = -180
SPAWN_VERTICAL_OFFSET_MAX = 200

# Make min/max platform Y fraction-based, so it scales with screen size
SPAWN_MIN_PLATFORM_Y = 0.30
SPAWN_MAX_PLATFORM_Y = 0.95

OBSTACLE_SPAWN_CHANCE = 0.5
OBSTACLE_MIN_SPACING = 150
OBSTACLE_MAX_PER_PLATFORM = 2
OBSTACLE_SPAWN_ATTEMPTS = 10

COIN_SPAWN_CHANCE = 0.3
MAX_COINS = 3
COIN_SPAWN_ATTEMPTS = 5
