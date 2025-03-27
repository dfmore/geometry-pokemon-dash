# obstacle.py
import pygame
import random
import src.config as c

class Obstacle:
    def __init__(self, x, y, pokemon_images):
        self.image = random.choice(pokemon_images)
        self.width, self.height = self.image.get_size()

        self.x = x
        self.y = y
        self.speed = c.SPEED

    def move(self):
        self.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def off_screen(self):
        return (self.x + self.width) < 0
