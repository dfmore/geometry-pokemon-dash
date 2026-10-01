# player.py
import pygame
import src.config as c

class Player:
    def __init__(self):
        side = int(c.SQUARE_WIDTH_FRAC * c.WIDTH)
        self.width = side
        self.height = side

        # Starting position
        self.x = 100
        self.y = 320
        # Keep track of the resting/default X for nudging logic
        self.default_x = self.x

        self.vel_y = 0
        self.on_ground = True
        self.charging = False
        self.jump_charge = 0
        self.can_double_jump = True

    def move(self, platforms):
        prev_bottom = self.y + self.height
        self.vel_y += c.GRAVITY
        self.vel_y = min(self.vel_y, c.MAX_FALL_SPEED)
        self.y += self.vel_y
        new_bottom = self.y + self.height
        self.on_ground = False

        if self.vel_y <= 0:
            return

        # Swept landing test: the bottom edge must cross the platform top
        # this frame, so fast falls never tunnel and side contact is ignored.
        landing = None
        for platform in platforms:
            tol = c.PLATFORM_EDGE_TOLERANCE
            if (self.x + self.width > platform.x - tol
                    and self.x < platform.x + platform.width + tol
                    and prev_bottom <= platform.y + 1
                    and new_bottom >= platform.y):
                if landing is None or platform.y < landing.y:
                    landing = platform

        if landing is not None:
            self.y = landing.y - self.height
            self.vel_y = 0
            self.on_ground = True
            self.can_double_jump = True

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 255),
                         (self.x, self.y, self.width, self.height))
