# level_manager.py

import pygame
import random
import src.config as c
from src.game_platform import Platform
from src.obstacle import Obstacle
from src.coin import StarCoin

class LevelManager:
    def __init__(self, pokemon_images, coin_image):
        self.pokemon_images = pokemon_images
        self.coin_image = coin_image
        
        self.platforms = []
        self.obstacles = []
        self.star_coins = []
        
        self.coins_spawned = 0

        # Load one of the 5 fixed levels from config
        self.load_level(c.CURRENT_LEVEL)

    def load_level(self, level_index):
        """
        Loads a fixed level layout from config.LEVELS[level_index].
        Clears any existing platforms/obstacles/coins and spawns them
        according to the data in the config.
        """
        self.platforms.clear()
        self.obstacles.clear()
        self.star_coins.clear()
        self.coins_spawned = 0

        if level_index < 0 or level_index >= len(c.LEVELS):
            print(f"Warning: level_index {level_index} out of range. Defaulting to 0.")
            level_index = 0

        level_data = c.LEVELS[level_index]
        print(f"Loading: {level_data.get('name', 'Unknown Level')}")

        # Create platforms
        for (px, py) in level_data.get("platforms", []):
            plat = Platform(px, py)
            self.platforms.append(plat)

        # Create obstacles
        for (ox, oy) in level_data.get("obstacles", []):
            # If you want to place obstacle exactly at y => just use that y
            # Or if you want it to spawn on top of the nearest platform, you can do that logic here.
            obs = Obstacle(ox, oy, self.pokemon_images)
            self.obstacles.append(obs)

        # Create coins
        for (cx, cy) in level_data.get("coins", []):
            coin_obj = StarCoin(cx, cy, self.coin_image)
            self.star_coins.append(coin_obj)

    # The old random methods are no longer used, so we can remove or leave them empty:

    def generate_initial_platforms(self, screen_width):
        pass

    def spawn_new_platforms(self, screen_width):
        pass

    # Below: no change to the update or collision checks

    def update_platforms(self):
        for p in self.platforms[:]:
            p.move()
            if p.off_screen():
                self.platforms.remove(p)

    def update_obstacles(self):
        for obs in self.obstacles[:]:
            obs.move()
            if obs.off_screen():
                self.obstacles.remove(obs)

    def update_coins(self):
        # Move coins left
        for ccoin in self.star_coins[:]:
            ccoin.x -= c.SPEED
            if (ccoin.x + ccoin.width) < 0:
                self.star_coins.remove(ccoin)

    def check_obstacle_collisions(self, player_rect):
        for obstacle in self.obstacles:
            obs_rect = pygame.Rect(obstacle.x, obstacle.y,
                                   obstacle.width, obstacle.height)
            if player_rect.colliderect(obs_rect.inflate(-c.COLLISION_TOLERANCE*2,
                                                        -c.COLLISION_TOLERANCE*2)):
                return True
        return False
