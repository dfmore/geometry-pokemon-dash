# coin.py
import pygame
from src.config import COIN_SIZE, COIN_COLOR

class StarCoin:
    def __init__(self, x, y):
        self.width = COIN_SIZE
        self.height = COIN_SIZE
        self.color = COIN_COLOR
        self.x = x
        self.y = y

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
