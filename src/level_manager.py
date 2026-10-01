# level_manager.py

import pygame
import random

import src.config as c
import src.levels_config as lvl

from src.game_platform import Platform
from src.obstacle import Obstacle
from src.coin import StarCoin

# Safe platform band in design pixels (800px-high screen)
SAFE_TOP = 150      # below the HUD
SAFE_BOTTOM = 680   # above the spike bar, with room for the player

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

        # 1) Local RNG (leaves the global random stream untouched)
        seed_val = level_data.get("seed", 0)
        rng = random.Random(seed_val)

        # 2) Platform count from LEVEL_DURATION
        platform_count = int(c.LEVEL_DURATION)

        # 3) Retrieve spawn parameters (y values are design pixels, 800px high)
        safe_gap_min = level_data.get("safe_gap_min", 50)
        safe_gap_max = level_data.get("safe_gap_max", 140)
        vertical_offset_min = level_data.get("vertical_offset_min", -10)
        vertical_offset_max = level_data.get("vertical_offset_max", 10)
        min_py = max(level_data.get("min_platform_y", 550), SAFE_TOP)
        max_py = min(level_data.get("max_platform_y", 600), SAFE_BOTTOM)
        if min_py > max_py:
            min_py = max_py

        obstacle_chance = level_data.get("obstacle_spawn_chance", 0.3)
        obstacle_max = max(1, level_data.get("obstacle_max_per_platform", 1))
        coin_chance = level_data.get("coin_chance", 0.3)

        max_rise = int(0.6 * c.MAX_JUMP_STRENGTH ** 2 / (2 * c.GRAVITY))
        max_gap = int(0.5 * c.SPEED * 2 * c.MAX_JUMP_STRENGTH / c.GRAVITY)

        # Real-screen ceiling so a platform never sinks into the spike bar
        spike_height = int(c.SPIKE_HEIGHT_FRAC * c.HEIGHT)
        player_side = int(c.SQUARE_WIDTH_FRAC * c.WIDTH)
        screen_max_y = c.HEIGHT - spike_height - c.SPIKE_BG_OVERLAP - player_side - 10

        def make_platform(x, y_design):
            return Platform(x, min(c.design_y(y_design), screen_max_y))

        # 4) First platform
        y_design = min_py + int(rng.random() * (max_py - min_py + 1))
        self.platforms.append(make_platform(100, y_design))

        # 5) Generate more platforms (draw count varies: Obstacle() draws an
        #    image from rng only when an obstacle spawns; still deterministic)
        for _ in range(platform_count - 1):
            last_plat = self.platforms[-1]
            gap = safe_gap_min + int(rng.random() * (safe_gap_max - safe_gap_min + 1))
            gap = min(gap, max_gap)
            new_x = last_plat.x + last_plat.width + gap
            offset = vertical_offset_min + int(
                rng.random() * (vertical_offset_max - vertical_offset_min + 1))
            new_y = max(min_py, min(y_design + offset, max_py))
            if y_design - new_y > max_rise:
                new_y = y_design - max_rise
            y_design = new_y

            p = make_platform(new_x, y_design)
            self.platforms.append(p)

            obs_roll = rng.random()
            obs_count = 1 + int(rng.random() * obstacle_max)
            obs_fracs = [rng.random() for _ in range(obstacle_max)]
            if obs_roll < obstacle_chance:
                for i in range(obs_count):
                    obs = Obstacle(0, 0, self.pokemon_images, rng=rng)
                    obs.x = p.x + int(obs_fracs[i] * max(0, p.width - obs.width))
                    obs.y = p.y - obs.height
                    self.obstacles.append(obs)

            coin_roll = rng.random()
            coin_fracs = [rng.random() for _ in range(5)]
            if coin_roll < coin_chance:
                c_obj = StarCoin(0, 0, self.coin_image)
                for frac in coin_fracs:
                    coin_x = p.x + int(frac * max(0, p.width - c_obj.width))
                    coin_y = p.y - c_obj.height - 10
                    coin_rect = pygame.Rect(coin_x, coin_y, c_obj.width, c_obj.height)

                    # Check obstacles on the same platform to avoid overlap
                    overlap = False
                    for obs in self.obstacles:
                        if p.x <= obs.x <= (p.x + p.width):
                            obs_rect = pygame.Rect(obs.x, obs.y, obs.width, obs.height)
                            if coin_rect.colliderect(obs_rect):
                                overlap = True
                                break

                    if not overlap:
                        c_obj.x = coin_x
                        c_obj.y = coin_y
                        self.star_coins.append(c_obj)
                        self.coins_spawned += 1
                        break

    def update_platforms(self):
        """Move each platform left and remove if off-screen."""
        for p in self.platforms:
            p.move()
        self.platforms = [p for p in self.platforms if not p.off_screen()]

    def update_obstacles(self):
        """Move each obstacle left and remove if off-screen."""
        for obs in self.obstacles:
            obs.move()
        self.obstacles = [obs for obs in self.obstacles if not obs.off_screen()]

    def update_coins(self):
        """Move each coin left and remove if off-screen."""
        for ccoin in self.star_coins:
            ccoin.x -= c.SPEED
        self.star_coins = [cc for cc in self.star_coins if (cc.x + cc.width) >= 0]

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
