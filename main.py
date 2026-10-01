# main.py
import pygame
import src.config as c

try:
    pygame.mixer.pre_init(44100, -16, 2, 512)
except pygame.error:
    pass
pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass

try:
    pygame.mixer.music.load(c.asset_path("signal.mp3"))
    pygame.mixer.music.play(-1)
except (pygame.error, FileNotFoundError):
    pass

# Fixed logical size so physics and layout are identical on every monitor
flags = pygame.SCALED | (pygame.FULLSCREEN if c.FULLSCREEN else 0)
try:
    screen = pygame.display.set_mode((c.WIDTH, c.HEIGHT), flags)
except pygame.error:
    screen = pygame.display.set_mode((c.WIDTH, c.HEIGHT))
pygame.display.set_caption('Geometry Pokemon Dash')

# Store the final window size so other code sees it
c.WIDTH, c.HEIGHT = screen.get_size()

from src.game_manager import main

if __name__ == "__main__":
    main()
