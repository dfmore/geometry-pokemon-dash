# config.py
import os

FULLSCREEN = True

FPS = 30

# Fixed logical resolution. main.py opens a pygame.SCALED window at this size,
# so the OS window can be any size while game logic always sees 1200x800.
# Level layouts are only guaranteed identical at this logical size.
WIDTH = 1200
HEIGHT = 800

# Resolution the levels and physics are designed for
DESIGN_WIDTH = 1200
DESIGN_HEIGHT = 800

# Project root (parent of src/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def asset_path(name):
    return os.path.join(BASE_DIR, 'assets', name)


def design_y(v):
    # Reads the module-global HEIGHT at call time (main.py reassigns it)
    return int(round(v * HEIGHT / DESIGN_HEIGHT))


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
MAX_JUMP_STRENGTH = 32
MAX_FALL_SPEED = 30
CHARGE_RATE = 1

COYOTE_FRAMES = 3
JUMP_BUFFER_FRAMES = 2

SPEED = 6
# Counted in frames at FPS (LEVEL_DURATION * FPS frames), so the level runs
# longer in wall-clock time if the game drops below FPS.
LEVEL_DURATION = 40  # seconds at FPS

WHITE = (255, 255, 255)
RED   = (255,   0,   0)
BLUE  = (  0,   0, 255)
GREEN = (  0, 255,   0)
BLACK = (  0,   0,   0)
LIGHT_BLUE = (173, 216, 230)

COLLISION_TOLERANCE = 7

JOYSTICK_NUDGE_RANGE = 50   # How far (in pixels) we can nudge left/right
JOYSTICK_NUDGE_DEADZONE = 0.1
JOYSTICK_NUDGE_SPEED = 0.15  # 0.0 -> never moves, 1.0 -> instant snap

BUBBLE_COLOR = (0, 255, 0)        # Green bubbles
BUBBLE_MIN_RADIUS = 5
BUBBLE_MAX_RADIUS = 10

BUBBLE_SPEED_MIN = 1
BUBBLE_SPEED_MAX = 3

BUBBLE_SPAWN_RATE = 0.03         # Probability each frame that a new bubble spawns
BUBBLE_MAX_COUNT = 15            # Max bubbles on screen

SPIKE_BG_COLOR = (0, 0, 0)
SPIKE_BG_OVERLAP = 30