# player.py
import pygame
from src.config import SQUARE_SIZE, GRAVITY, CHARGE_RATE, MIN_JUMP_STRENGTH, MAX_JUMP_STRENGTH

class Player:
    def __init__(self):
        self.x = 100
        self.y = 320
        self.width = SQUARE_SIZE
        self.height = SQUARE_SIZE
        self.vel_y = 0
        self.on_ground = True
        self.charging = False
        self.jump_charge = 0
        self.can_double_jump = True  # Reset when landing

    def move(self, platforms):
        self.vel_y += GRAVITY
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
        pygame.draw.rect(screen, (0, 0, 255), (self.x, self.y, self.width, self.height))
