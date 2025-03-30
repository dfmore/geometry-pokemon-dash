# bubbles.py
import pygame
import random
import src.config as c

class Bubble:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # random radius
        self.radius = random.randint(c.BUBBLE_MIN_RADIUS, c.BUBBLE_MAX_RADIUS)
        # random upward speed
        self.speed = random.uniform(c.BUBBLE_SPEED_MIN, c.BUBBLE_SPEED_MAX)

    def update(self):
        # Move bubble upward
        self.y -= self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, c.BUBBLE_COLOR, (int(self.x), int(self.y)), self.radius)

    def off_screen(self):
        return (self.y + self.radius) < 0
