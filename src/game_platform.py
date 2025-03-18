# game_platform.py
import pygame
import src.config as c

class Platform:
    def __init__(self, x, y):
        self.width = int(c.PLATFORM_WIDTH_FRAC * c.WIDTH)
        self.height = int(c.PLATFORM_HEIGHT_FRAC * c.HEIGHT)
        self.x = x
        self.y = y
        self.speed = c.SPEED

    def move(self):
        self.x -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, self.width, self.height))

    def off_screen(self):
        return (self.x + self.width) < 0
