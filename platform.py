# platform.py
import pygame
from config import PLATFORM_WIDTH, PLATFORM_HEIGHT, SPEED

class Platform:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLATFORM_WIDTH
        self.height = PLATFORM_HEIGHT
        self.speed = SPEED

    def move(self):
        self.x -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, self.width, self.height))

    def off_screen(self):
        return self.x + self.width < 0
