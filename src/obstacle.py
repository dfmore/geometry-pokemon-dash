# obstacle.py
import pygame
import random
import src.config as c

class Obstacle:
    def __init__(self, x, y, pokemon_images):
        """
        Instead of passing a platform, we pass the direct coordinates (x, y).
        We'll still pick a random Pokémon image from pokemon_images.
        """
        # Choose a random pre-scaled Pokémon image
        self.image = random.choice(pokemon_images)
        self.width, self.height = self.image.get_size()

        # Use x,y directly
        self.x = x
        self.y = y

        # Same speed as before
        self.speed = c.SPEED

    def move(self):
        self.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def off_screen(self):
        return (self.x + self.width) < 0
