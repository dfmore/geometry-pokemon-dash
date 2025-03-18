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

    def generate_initial_platforms(self, screen_width):
        while self.platforms[-1].x + self.platforms[-1].width < screen_width:
            gap = random.randint(c.SPAWN_SAFE_GAP_MIN, c.SPAWN_SAFE_GAP_MAX)
            last_platform = self.platforms[-1]
            new_x = last_platform.x + last_platform.width + gap

            offset = random.randint(c.SPAWN_VERTICAL_OFFSET_MIN, c.SPAWN_VERTICAL_OFFSET_MAX)
            new_y = last_platform.y + offset

            min_platform_y = int(c.SPAWN_MIN_PLATFORM_Y * c.HEIGHT)
            max_platform_y = int(c.SPAWN_MAX_PLATFORM_Y * c.HEIGHT)
            new_y = max(min_platform_y, min(new_y, max_platform_y))

            self.platforms.append(Platform(new_x, new_y))

    def spawn_new_platforms(self, screen_width):
        while self.platforms and (self.platforms[-1].x + self.platforms[-1].width < screen_width):
            gap = random.randint(c.SPAWN_SAFE_GAP_MIN, c.SPAWN_SAFE_GAP_MAX)
            last_platform = self.platforms[-1]
            new_x = last_platform.x + last_platform.width + gap

            offset = random.randint(c.SPAWN_VERTICAL_OFFSET_MIN, c.SPAWN_VERTICAL_OFFSET_MAX)
            new_y = last_platform.y + offset

            min_platform_y = int(c.SPAWN_MIN_PLATFORM_Y * c.HEIGHT)
            max_platform_y = int(c.SPAWN_MAX_PLATFORM_Y * c.HEIGHT)
            new_y = max(min_platform_y, min(new_y, max_platform_y))

            new_platform = Platform(new_x, new_y)
            self.platforms.append(new_platform)
            
            # Spawn obstacles
            if random.random() < c.OBSTACLE_SPAWN_CHANCE:
                num_obs = random.randint(1, c.OBSTACLE_MAX_PER_PLATFORM)
                obs_positions = []
                
                for _ in range(num_obs):
                    attempts = 0
                    while attempts < c.OBSTACLE_SPAWN_ATTEMPTS:
                        # We'll guess a position, then see if it conflicts
                        candidate_x = new_platform.x + random.randint(0, new_platform.width - 1)
                        # Check if it's at least c.OBSTACLE_MIN_SPACING away from other obstacles
                        if all(abs(candidate_x - px) >= c.OBSTACLE_MIN_SPACING for px in obs_positions):
                            obs_positions.append(candidate_x)
                            break
                        attempts += 1

                for pos in obs_positions:
                    # Create the obstacle
                    obs = Obstacle(new_platform, self.pokemon_images)
                    # Now we know obs.width
                    # So clamp pos so the obstacle doesn't go off the right edge
                    max_obs_x = new_platform.x + new_platform.width - obs.width
                    if pos > max_obs_x:
                        pos = max_obs_x
                    obs.x = pos
                    self.obstacles.append(obs)
            
            # Spawn a coin
            if (self.coins_spawned < c.MAX_COINS) and (random.random() < c.COIN_SPAWN_CHANCE):
                placed = False
                attempts = 0
                while not placed and attempts < c.COIN_SPAWN_ATTEMPTS:
                    coin_test = StarCoin(0, 0, self.coin_image)
                    coin_w = coin_test.width
                    coin_x = new_platform.x + random.randint(0, new_platform.width - coin_w)
                    coin_y = new_platform.y - 50
                    coin_rect = pygame.Rect(coin_x, coin_y, coin_w, coin_test.height)

                    safe = True
                    for obstacle in self.obstacles:
                        if new_platform.x <= obstacle.x <= (new_platform.x + new_platform.width):
                            obs_rect = pygame.Rect(obstacle.x, obstacle.y,
                                                   obstacle.width, obstacle.height)
                            if coin_rect.colliderect(obs_rect.inflate(-c.COLLISION_TOLERANCE * 2,
                                                                      -c.COLLISION_TOLERANCE * 2)):
                                safe = False
                                break
                    if safe:
                        coin_obj = StarCoin(coin_x, coin_y, self.coin_image)
                        self.star_coins.append(coin_obj)
                        self.coins_spawned += 1
                        placed = True
                    attempts += 1

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
