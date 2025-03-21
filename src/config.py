FULLSCREEN = True

# The "starting" or "windowed" resolution
WIDTH = 1200
HEIGHT = 800

###############################################################################
# Fraction-based shape sizes
###############################################################################
# For example, if you used 250 px on a 1200 px-wide screen for platform width,
# that's about 0.2083. We'll store it as a fraction. Similarly for heights.
PLATFORM_WIDTH_FRAC = 250/WIDTH
PLATFORM_HEIGHT_FRAC = 10/HEIGHT
PLATFORM_EDGE_TOLERANCE = 5

SPIKE_HEIGHT_FRAC = 20/HEIGHT  # e.g. 20 px on an 800-tall screen -> 0.025
SPIKE_COUNT = 20
SPIKE_COLOR = (255, 0, 0)  # bright red

###############################################################################
# For images that must keep aspect ratio:
# We'll scale obstacles by OBSTACLE_WIDTH_FRAC * actual window width,
# then derive height from the image's aspect ratio.
###############################################################################
OBSTACLE_WIDTH_FRAC = 40/WIDTH  # e.g. 40 px on a 1200 px width -> ~0.0333
# We'll skip an explicit OBSTACLE_HEIGHT_FRAC so we can preserve ratio automatically.

COIN_WIDTH_FRAC = 30/WIDTH  # e.g. 30 px on a 1200 px width -> 0.025
# We'll skip an explicit height fraction for coins, too, to preserve ratio.

SQUARE_WIDTH_FRAC = 30/WIDTH  # Player's square width fraction.
# We'll also skip height fraction for the player's rectangle if we want it truly "square."

###############################################################################
# Other game constants
###############################################################################
GRAVITY = 1
MIN_JUMP_STRENGTH = 15
MAX_JUMP_STRENGTH = 45
CHARGE_RATE = 1
COYOTE_FRAMES = 5         # number of frames you can still jump after leaving ground
JUMP_BUFFER_FRAMES = 5    # number of frames jump is remembered before landing
SPEED = 6

LEVEL_DURATION = 100  # seconds

WHITE = (255, 255, 255)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

COLLISION_TOLERANCE = 7

###############################################################################
# Spawning / platform / obstacle config
###############################################################################
SPAWN_SAFE_GAP_MIN = 50
SPAWN_SAFE_GAP_MAX = 140

# Keep the vertical offsets in absolute pixels if you like random lumps
SPAWN_VERTICAL_OFFSET_MIN = -200
SPAWN_VERTICAL_OFFSET_MAX = 200

# Make min/max platform Y fraction-based, so it scales with screen size
SPAWN_MIN_PLATFORM_Y = 0.35
SPAWN_MAX_PLATFORM_Y = 0.95

OBSTACLE_SPAWN_CHANCE = 0.7
OBSTACLE_MIN_SPACING = 150
OBSTACLE_MAX_PER_PLATFORM = 2
OBSTACLE_SPAWN_ATTEMPTS = 20

COIN_SPAWN_CHANCE = 0.3
MAX_COINS = 5
COIN_SPAWN_ATTEMPTS = 5
