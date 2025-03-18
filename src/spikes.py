# spikes.py
import pygame
import src.config as c  # So we can reference SPIKE_COUNT, SPIKE_COLOR, etc.

class Spikes:
    def __init__(self):
        self.y = c.HEIGHT - c.SPIKE_HEIGHT
        self.height = c.SPIKE_HEIGHT

    def draw(self, screen):
        # We'll create c.SPIKE_COUNT triangles across the full width
        spike_width = c.WIDTH // c.SPIKE_COUNT

        for i in range(c.SPIKE_COUNT):
            left_x = i * spike_width
            right_x = (i + 1) * spike_width
            # The apex is the midpoint of the top edge
            apex_x = left_x + (spike_width // 2)
            apex_y = self.y

            # The base of the spike is a horizontal line from
            # (left_x, y + height) to (right_x, y + height)
            base_left = (left_x,  self.y + self.height)
            base_right = (right_x, self.y + self.height)
            apex = (apex_x, apex_y)

            # Now draw a polygon (a triangle, in this case)
            pygame.draw.polygon(screen, c.SPIKE_COLOR, [base_left, base_right, apex])
