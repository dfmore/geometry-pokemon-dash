# player.py
import pygame
import src.config as c

class Player:
    def __init__(self):
        # Let's treat it as a square: side = int(SQUARE_WIDTH_FRAC * c.WIDTH)
        side = int(c.SQUARE_WIDTH_FRAC * c.WIDTH)
        self.width = side
        self.height = side

        # Starting position
        self.x = 100
        self.y = 320

        self.vel_y = 0
        self.on_ground = True
        self.charging = False
        self.jump_charge = 0
        self.can_double_jump = True

    def move(self, platforms):
        self.vel_y += c.GRAVITY
        self.y += self.vel_y
        self.on_ground = False

        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for platform in platforms:
            platform_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            if self.vel_y > 0 and player_rect.colliderect(platform_rect):
                self.y = platform.y - self.height
                self.vel_y = 0
                self.on_ground = True
                self.can_double_jump = True
                player_rect.y = self.y

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 255),
                         (self.x, self.y, self.width, self.height))
