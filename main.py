import pygame
import src.config as c  # So we can read WIDTH, HEIGHT, and FULLSCREEN

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

# If FULLSCREEN is True, create a fullscreen display
if c.FULLSCREEN:
    screen = pygame.display.set_mode((c.WIDTH, c.HEIGHT), pygame.FULLSCREEN)
else:
    # Otherwise, create a window of the specified size
    screen = pygame.display.set_mode((c.WIDTH, c.HEIGHT))

from src.game import main

if __name__ == "__main__":
    main()