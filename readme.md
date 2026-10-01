# Geometry Pokemon Dash

Geometry Pokemon Dash is a 2D runner game built with Python and Pygame. Play through 5 levels with 10 lives, 40 seconds per level, dodging obstacles and collecting coins.

## Prerequisites

- Python 3.8 or higher
- Pygame (installed from `requirements.txt`)

## Installation

1. Clone this repository to your local machine and change into its folder.

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

From the project directory, run:

```bash
python main.py
```

The game runs fullscreen, scaled from a 1200x800 layout. To play in a window instead, set `FULLSCREEN = False` in `src/config.py`.

## Controls

- **Space** (hold, then release): charged jump.
- **X**: jump / double jump.
- **ESC**: quit (works on every screen).
- **Joystick button 0**: charged jump (hold and release).
- **Joystick button 2**: jump / double jump.
- **Left stick**: nudge left/right.
- **Any key or button**: continue on the end screens (level complete, game over, scoreboard).

## Scores

When the game ends, enter your initials to save your coin total. High scores are saved to `scoreboard.json` in the project folder.

Enjoy playing Geometry Pokemon Dash!
