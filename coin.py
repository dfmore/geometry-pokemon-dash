# coin.py
import pygame
from config import COIN_SIZE

class StarCoin:
    def __init__(self, x, y, coin_image):
        self.x = x
        self.y = y
        self.width = COIN_SIZE
        self.height = COIN_SIZE
        self.coin_image = coin_image

    def draw(self, screen):
        screen.blit(self.coin_image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
