# main.py
import pygame
import src.config as c

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

if c.FULLSCREEN:
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode((c.WIDTH, c.HEIGHT))

# Store the final window size so other code sees it
c.WIDTH, c.HEIGHT = screen.get_size()

from src.game_manager import main

if __name__ == "__main__":
    main()
