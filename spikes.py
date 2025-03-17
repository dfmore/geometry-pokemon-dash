# spikes.py
import pygame
from config import WIDTH, SPIKE_HEIGHT, HEIGHT

class Spikes:
    def __init__(self):
        self.y = HEIGHT - SPIKE_HEIGHT
        self.height = SPIKE_HEIGHT

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), (0, self.y, WIDTH, self.height))
