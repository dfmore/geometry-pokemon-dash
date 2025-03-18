# obstacle.py
import pygame
import random
import src.config as c

class Obstacle:
    def __init__(self, platform, pokemon_images):
        # Choose a random pre-scaled Pokémon image
        self.image = random.choice(pokemon_images)
        self.width, self.height = self.image.get_size()

        # By default, place it somewhere on the platform in X, or override in level_manager
        self.x = platform.x
        self.y = platform.y - self.height
        self.speed = c.SPEED

    def move(self):
        self.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def off_screen(self):
        return (self.x + self.width) < 0
