# spikes.py
import pygame
import src.config as c

class Spikes:
    def __init__(self):
        self.height = int(c.SPIKE_HEIGHT_FRAC * c.HEIGHT)
        self.y = c.HEIGHT - self.height

    def draw(self, screen):
        spike_width = c.WIDTH // c.SPIKE_COUNT

        for i in range(c.SPIKE_COUNT):
            left_x = i * spike_width
            right_x = (i + 1) * spike_width
            apex_x = left_x + (spike_width // 2)
            apex_y = self.y

            base_left = (left_x,  self.y + self.height)
            base_right = (right_x, self.y + self.height)
            apex = (apex_x, apex_y)

            pygame.draw.polygon(screen, c.SPIKE_COLOR, [base_left, base_right, apex])
