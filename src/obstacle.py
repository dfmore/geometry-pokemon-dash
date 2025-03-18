# obstacle.py
import pygame
import random
from src.config import OBSTACLE_WIDTH, OBSTACLE_HEIGHT, SPEED

class Obstacle:
    def __init__(self, platform, pokemon_images):
        self.x = platform.x + random.randint(0, platform.width - OBSTACLE_WIDTH)
        self.y = platform.y - OBSTACLE_HEIGHT
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT
        self.speed = SPEED
        self.image = random.choice(pokemon_images)

    def move(self):
        self.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def off_screen(self):
        return self.x + self.width < 0
