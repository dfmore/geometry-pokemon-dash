# level_manager.py
import pygame
import random
import src.config as c
from src.game_platform import Platform
from src.obstacle import Obstacle
from src.coin import StarCoin

class LevelManager:
    """
    Manages all platform, obstacle, and coin spawning and updating.
    """

    def __init__(self, pokemon_images, coin_image):
        self.pokemon_images = pokemon_images
        self.coin_image = coin_image
        
        self.platforms = []
        self.obstacles = []
        self.star_coins = []
        
        # Track how many coins have spawned in this run
        self.coins_spawned = 0

    def generate_initial_platforms(self, screen_width):
        # Fill up the screen width with initial platforms
        while self.platforms[-1].x + self.platforms[-1].width < screen_width:
            gap = random.randint(c.SPAWN_SAFE_GAP_MIN, c.SPAWN_SAFE_GAP_MAX)
            last_platform = self.platforms[-1]
            new_x = last_platform.x + last_platform.width + gap
            new_y = last_platform.y + random.randint(c.SPAWN_VERTICAL_OFFSET_MIN,
                                                     c.SPAWN_VERTICAL_OFFSET_MAX)
            new_y = max(c.SPAWN_MIN_PLATFORM_Y, min(new_y, c.SPAWN_MAX_PLATFORM_Y))
            self.platforms.append(Platform(new_x, new_y))

    def spawn_new_platforms(self, screen_width):
        # Continually spawn new platforms and obstacles/coins once the last platform is fully on-screen
        while self.platforms and (self.platforms[-1].x + self.platforms[-1].width < screen_width):
            gap = random.randint(c.SPAWN_SAFE_GAP_MIN, c.SPAWN_SAFE_GAP_MAX)
            last_platform = self.platforms[-1]
            new_x = last_platform.x + last_platform.width + gap
            new_y = last_platform.y + random.randint(c.SPAWN_VERTICAL_OFFSET_MIN,
                                                     c.SPAWN_VERTICAL_OFFSET_MAX)
            new_y = max(c.SPAWN_MIN_PLATFORM_Y, min(new_y, c.SPAWN_MAX_PLATFORM_Y))
            
            new_platform = Platform(new_x, new_y)
            self.platforms.append(new_platform)
            
            # Potentially spawn obstacles
            if random.random() < c.OBSTACLE_SPAWN_CHANCE:
                num_obs = random.randint(1, c.OBSTACLE_MAX_PER_PLATFORM)
                obs_positions = []
                for _ in range(num_obs):
                    attempts = 0
                    while attempts < c.OBSTACLE_SPAWN_ATTEMPTS:
                        candidate = (new_platform.x
                                     + random.randint(0, new_platform.width - c.OBSTACLE_WIDTH))
                        if all(abs(candidate - pos) >= c.OBSTACLE_MIN_SPACING for pos in obs_positions):
                            obs_positions.append(candidate)
                            break
                        attempts += 1
                for pos in obs_positions:
                    obs = Obstacle(new_platform, self.pokemon_images)
                    obs.x = pos
                    self.obstacles.append(obs)
            
            # Potentially spawn a coin if we haven't reached max
            if (self.coins_spawned < c.MAX_COINS) and (random.random() < c.COIN_SPAWN_CHANCE):
                placed = False
                attempts = 0
                while not placed and attempts < c.COIN_SPAWN_ATTEMPTS:
                    coin_x = new_platform.x + random.randint(0, new_platform.width - c.COIN_SIZE)
                    coin_y = new_platform.y - 50
                    coin_rect = pygame.Rect(coin_x, coin_y, c.COIN_SIZE, c.COIN_SIZE)
                    # Make sure it doesn't overlap obstacles
                    safe = True
                    for obstacle in self.obstacles:
                        if new_platform.x <= obstacle.x <= new_platform.x + new_platform.width:
                            obs_rect = pygame.Rect(obstacle.x, obstacle.y,
                                                   obstacle.width, obstacle.height)
                            if coin_rect.colliderect(obs_rect.inflate(
                                    -c.COLLISION_TOLERANCE * 2, -c.COLLISION_TOLERANCE * 2)):
                                safe = False
                                break
                    if safe:
                        self.star_coins.append(StarCoin(coin_x, coin_y, self.coin_image))
                        self.coins_spawned += 1
                        placed = True
                    attempts += 1

    def update_platforms(self):
        """Move existing platforms; remove if they're off-screen."""
        for p in self.platforms[:]:
            p.move()
            if p.off_screen():
                self.platforms.remove(p)

    def update_obstacles(self):
        """Move obstacles; remove if they're off-screen."""
        for obs in self.obstacles[:]:
            obs.move()
            if obs.off_screen():
                self.obstacles.remove(obs)

    def update_coins(self):
        """Move coins at the same speed; remove if off-screen."""
        for ccoin in self.star_coins[:]:
            ccoin.x -= c.SPEED
            if ccoin.x + ccoin.width < 0:
                self.star_coins.remove(ccoin)

    def check_obstacle_collisions(self, player_rect):
        """Return True if the player collides with an obstacle."""
        for obstacle in self.obstacles:
            obs_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
            if player_rect.colliderect(obs_rect.inflate(-c.COLLISION_TOLERANCE*2,
                                                        -c.COLLISION_TOLERANCE*2)):
                return True
        return False
