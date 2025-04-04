# level_manager.py

import pygame
import random

import src.config as c
import src.levels_config as lvl

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
        # Use the CURRENT_LEVEL from levels_config
        self.level_index = lvl.CURRENT_LEVEL

        # Generate the level data
        self.generate_seeded_level(self.level_index)

    def generate_seeded_level(self, level_index):
        """
        Generates platforms, obstacles, and coins based on random seed + level parameters.
        """
        self.platforms.clear()
        self.obstacles.clear()
        self.star_coins.clear()
        self.coins_spawned = 0

        # Validate index
        if level_index < 0 or level_index >= len(lvl.LEVELS):
            print(f"Warning: level_index {level_index} out of range. Defaulting to 0.")
            level_index = 0

        level_data = lvl.LEVELS[level_index]
        print(f"Generating level: {level_data.get('name', 'Unknown')}")

        # 1) Seed
        seed_val = level_data.get("seed", 0)
        random.seed(seed_val)

        # 2) Platform count from LEVEL_DURATION
        platform_count = int(c.LEVEL_DURATION)

        # 3) Retrieve spawn parameters
        safe_gap_min = level_data.get("safe_gap_min", 50)
        safe_gap_max = level_data.get("safe_gap_max", 140)
        vertical_offset_min = level_data.get("vertical_offset_min", -10)
        vertical_offset_max = level_data.get("vertical_offset_max", 10)
        min_py = level_data.get("min_platform_y", 550)
        max_py = level_data.get("max_platform_y", 600)

        obstacle_chance = level_data.get("obstacle_spawn_chance", 0.3)
        obstacle_max = level_data.get("obstacle_max_per_platform", 1)
        coin_chance = level_data.get("coin_chance", 0.3)

        # 4) First platform
        first_y = random.randint(min_py, max_py)
        first_platform = Platform(100, first_y)
        self.platforms.append(first_platform)

        # 5) Generate more platforms
        for _ in range(platform_count - 1):
            last_plat = self.platforms[-1]
            gap = random.randint(safe_gap_min, safe_gap_max)
            new_x = last_plat.x + last_plat.width + gap
            offset = random.randint(vertical_offset_min, vertical_offset_max)
            new_y = last_plat.y + offset
            new_y = max(min_py, min(new_y, max_py))

            p = Platform(new_x, new_y)
            self.platforms.append(p)

            # Maybe spawn obstacles
            if random.random() < obstacle_chance:
                num_obs = random.randint(1, obstacle_max)  
                for _ in range(num_obs):
                    obs = Obstacle(0, 0, self.pokemon_images)
                    obs.x = p.x + random.randint(0, max(0, p.width - obs.width))
                    obs.y = p.y - obs.height
                    self.obstacles.append(obs)

            # Maybe spawn coin
            if random.random() < coin_chance:
                c_obj = StarCoin(0, 0, self.coin_image)
                attempts = 5
                placed = False
                while attempts > 0 and not placed:
                    coin_x = p.x + random.randint(0, max(0, p.width - c_obj.width))
                    coin_y = p.y - c_obj.height - 10
                    coin_rect = pygame.Rect(coin_x, coin_y, c_obj.width, c_obj.height)

                    overlap = False
                    # Check obstacles on the same platform to avoid overlap
                    for obs in self.obstacles:
                        if (obs.x >= p.x and
                            obs.x <= (p.x + p.width)):
                            obs_rect = pygame.Rect(obs.x, obs.y, obs.width, obs.height)
                            if coin_rect.colliderect(obs_rect):
                                overlap = True
                                break

                    if not overlap:
                        c_obj.x = coin_x
                        c_obj.y = coin_y
                        self.star_coins.append(c_obj)
                        self.coins_spawned += 1
                        placed = True
                    attempts -= 1

    def update_platforms(self):
        """Move each platform left and remove if off-screen."""
        for p in self.platforms[:]:
            p.move()
            if p.off_screen():
                self.platforms.remove(p)

    def update_obstacles(self):
        """Move each obstacle left and remove if off-screen."""
        for obs in self.obstacles[:]:
            obs.move()
            if obs.off_screen():
                self.obstacles.remove(obs)

    def update_coins(self):
        """Move each coin left and remove if off-screen."""
        for ccoin in self.star_coins[:]:
            ccoin.x -= c.SPEED
            if (ccoin.x + ccoin.width) < 0:
                self.star_coins.remove(ccoin)

    def check_obstacle_collisions(self, player_rect):
        """
        Returns True if the player rect intersects any obstacle (with some collision tolerance).
        """
        for obstacle in self.obstacles:
            obs_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
            inflated = obs_rect.inflate(-c.COLLISION_TOLERANCE*2, -c.COLLISION_TOLERANCE*2)
            if player_rect.colliderect(inflated):
                return True
        return False
