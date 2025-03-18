import pygame
import src.config as c

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

if c.FULLSCREEN:
    # Use the user's current desktop size in fullscreen:
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
else:
    # Windowed mode at the config resolution
    screen = pygame.display.set_mode((c.WIDTH, c.HEIGHT))

# Store the actual final window size so other code can see it
c.WIDTH, c.HEIGHT = screen.get_size()

from src.game import main

if __name__ == "__main__":
    main()
