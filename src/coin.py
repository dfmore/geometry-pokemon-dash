# coin.py
import pygame

class StarCoin:
    def __init__(self, x, y, coin_image):
        self.coin_image = coin_image
        self.width, self.height = coin_image.get_size()
        self.x = x
        self.y = y

    def draw(self, screen):
        screen.blit(self.coin_image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
