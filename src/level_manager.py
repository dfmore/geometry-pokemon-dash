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
        self.level_index = c.CURRENT_LEVEL

        self.generate_seeded_level(self.level_index)

    def generate_seeded_level(self, level_index):
        """
        - Always sets platform_count = int(c.LEVEL_DURATION).
        - Places multiple obstacles (up to obstacle_max_per_platform) on top of each platform
          if random.random() < obstacle_spawn_chance.
        - Coins are placed above the platform, not overlapping obstacles.
        """
        self.platforms.clear()
        self.obstacles.clear()
        self.star_coins.clear()
        self.coins_spawned = 0

        if level_index < 0 or level_index >= len(c.LEVELS):
            print(f"Warning: level_index {level_index} out of range. Defaulting to 0.")
            level_index = 0

        level_data = c.LEVELS[level_index]
        print(f"Generating level: {level_data.get('name', 'Unknown')}")

        # 1) Seed
        seed_val = level_data.get("seed", 0)
        random.seed(seed_val)

        # 2) Compute platform count from LEVEL_DURATION
        platform_count = int(c.LEVEL_DURATION)

        # 3) Read or default the other parameters
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
        for i in range(platform_count - 1):
            last_plat = self.platforms[-1]
            gap = random.randint(safe_gap_min, safe_gap_max)
            new_x = last_plat.x + last_plat.width + gap
            offset = random.randint(vertical_offset_min, vertical_offset_max)
            new_y = last_plat.y + offset
            new_y = max(min_py, min(new_y, max_py))

            p = Platform(new_x, new_y)
            self.platforms.append(p)

            # Attempt obstacle spawning
            if random.random() < obstacle_chance:
                num_obs = random.randint(1, obstacle_max)  
                for _ in range(num_obs):
                    obs = Obstacle(0, 0, self.pokemon_images)
                    obs.x = p.x + random.randint(0, max(0, p.width - obs.width))
                    obs.y = p.y - obs.height
                    # Optionally check overlap among obstacles on the same platform
                    # if you want no obstacle overlap, do so here with attempts
                    self.obstacles.append(obs)

            # Attempt coin spawning
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
                        if obs.x >= p.x and obs.x <= (p.x + p.width):
                            # obstacle is on the same platform horizontally
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
                # skip coin if we can't find a free spot

    def generate_initial_platforms(self, screen_width):
        pass

    def spawn_new_platforms(self, screen_width):
        pass

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
