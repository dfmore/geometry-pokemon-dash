import pygame, random
from typing import List, Tuple
from src.config import (
    WIDTH, HEIGHT, WHITE, RED, BLUE, GREEN, BLACK, LEVEL_DURATION,
    SQUARE_SIZE, GRAVITY, CHARGE_RATE, MIN_JUMP_STRENGTH, MAX_JUMP_STRENGTH,
    OBSTACLE_WIDTH, OBSTACLE_HEIGHT, SPEED, PLATFORM_WIDTH, PLATFORM_HEIGHT,
    SPIKE_HEIGHT, COIN_SIZE, COLLISION_TOLERANCE
)
from src.assets import load_assets
from src.player import Player
from src.game_platform import Platform
from src.obstacle import Obstacle
from src.coin import StarCoin
from src.spikes import Spikes

# Cache the joystick instance if available
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
else:
    joystick = None

class Game:
    def __init__(self) -> None:
        """Initialize game assets and objects."""
        self.assets = load_assets()
        self.pokemon_images = self.assets['pokemon_images']
        self.coin_image = self.assets['coin_image']
        self.boing_sound = self.assets['boing_sound']

        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        # Pre-generate initial platforms
        self.platforms: List[Platform] = []
        first_platform = Platform(100, 320)
        self.platforms.append(first_platform)
        self._generate_initial_platforms()

        self.star_coins: List[StarCoin] = []
        self.coins_spawned = 0
        self.coins_collected = 0
        self.obstacles: List[Obstacle] = []

        self.player = Player()
        self.spikes = Spikes()

        self.start_ticks = pygame.time.get_ticks()

    def _generate_initial_platforms(self) -> None:
        """Generate initial platforms until the last platform extends to the screen width."""
        safe_gap_min = 50
        safe_gap_max = 140
        vertical_offset_min = -5
        vertical_offset_max = 10
        min_platform_y = 310
        max_platform_y = 340
        while self.platforms[-1].x + self.platforms[-1].width < WIDTH:
            gap = random.randint(safe_gap_min, safe_gap_max)
            new_x = self.platforms[-1].x + self.platforms[-1].width + gap
            new_y = self.platforms[-1].y + random.randint(vertical_offset_min, vertical_offset_max)
            new_y = max(min_platform_y, min(new_y, max_platform_y))
            self.platforms.append(Platform(new_x, new_y))

    def process_events(self) -> None:
        """Handle keyboard and joystick events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            # Keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.player.on_ground:
                        self.player.charging = True
                        self.player.jump_charge = MIN_JUMP_STRENGTH
                if event.key == pygame.K_x:
                    self.boing_sound.play()
                    if self.player.on_ground:
                        self.player.vel_y = -MIN_JUMP_STRENGTH
                    elif not self.player.on_ground and self.player.can_double_jump:
                        self.player.vel_y = -MIN_JUMP_STRENGTH
                        self.player.can_double_jump = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and self.player.charging:
                    self.boing_sound.play()
                    if self.player.on_ground:
                        self.player.vel_y = -self.player.jump_charge
                    self.player.charging = False
                    self.player.jump_charge = 0
            # Joystick input
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    if self.player.on_ground:
                        self.player.charging = True
                        self.player.jump_charge = MIN_JUMP_STRENGTH
                if event.button == 2:
                    self.boing_sound.play()
                    if self.player.on_ground:
                        self.player.vel_y = -MIN_JUMP_STRENGTH
                    elif not self.player.on_ground and self.player.can_double_jump:
                        self.player.vel_y = -MIN_JUMP_STRENGTH
                        self.player.can_double_jump = False
            if event.type == pygame.JOYBUTTONUP:
                if event.button == 0 and self.player.charging:
                    self.boing_sound.play()
                    if self.player.on_ground:
                        self.player.vel_y = -self.player.jump_charge
                    self.player.charging = False
                    self.player.jump_charge = 0

    def update_input(self) -> None:
        """Update jump charge while the jump button is held."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.player.charging and self.player.on_ground:
            self.player.jump_charge += CHARGE_RATE
            if self.player.jump_charge > MAX_JUMP_STRENGTH:
                self.player.jump_charge = MAX_JUMP_STRENGTH
        if joystick is not None and joystick.get_button(0) and self.player.charging and self.player.on_ground:
            self.player.jump_charge += CHARGE_RATE
            if self.player.jump_charge > MAX_JUMP_STRENGTH:
                self.player.jump_charge = MAX_JUMP_STRENGTH

    def update_objects(self) -> None:
        """Move platforms, obstacles, and coins; remove off-screen objects."""
        for platform in self.platforms[:]:
            platform.move()
            if platform.off_screen():
                self.platforms.remove(platform)
        for obstacle in self.obstacles[:]:
            obstacle.move()
            if obstacle.off_screen():
                self.obstacles.remove(obstacle)
        for coin in self.star_coins[:]:
            coin.x -= SPEED
            if coin.x + coin.width < 0:
                self.star_coins.remove(coin)

    def spawn_new_platforms(self) -> None:
        """Spawn new platforms until the chain extends past the screen width.
           Also spawn obstacles and coins on the new platform.
        """
        safe_gap_min = 50
        safe_gap_max = 140
        vertical_offset_min = -5
        vertical_offset_max = 10
        min_platform_y = 310
        max_platform_y = 340
        
        while self.platforms and self.platforms[-1].x + self.platforms[-1].width < WIDTH:
            gap = random.randint(safe_gap_min, safe_gap_max)
            new_x = self.platforms[-1].x + self.platforms[-1].width + gap
            new_y = self.platforms[-1].y + random.randint(vertical_offset_min, vertical_offset_max)
            new_y = max(min_platform_y, min(new_y, max_platform_y))
            new_platform = Platform(new_x, new_y)
            self.platforms.append(new_platform)
            # Spawn obstacles on this platform ensuring they are at least 150 pixels apart.
            if random.random() < 0.5:
                num_obs = random.randint(1, 2)
                obs_positions: List[int] = []
                for i in range(num_obs):
                    attempts = 0
                    candidate = None
                    while attempts < 10:
                        candidate = new_platform.x + random.randint(0, new_platform.width - OBSTACLE_WIDTH)
                        valid = True
                        for pos in obs_positions:
                            if abs(candidate - pos) < 150:
                                valid = False
                                break
                        if valid:
                            obs_positions.append(candidate)
                            break
                        attempts += 1
                for pos in obs_positions:
                    obs = Obstacle(new_platform, self.pokemon_images)
                    obs.x = pos
                    self.obstacles.append(obs)
            # Spawn a coin if possible, ensuring it's at least 100 pixels away from obstacles on this platform.
            if self.coins_spawned < 3 and random.random() < 0.3:
                placed = False
                attempts = 0
                while not placed and attempts < 5:
                    coin_x = new_platform.x + random.randint(0, new_platform.width - COIN_SIZE)
                    coin_y = new_platform.y - 50
                    coin_rect = pygame.Rect(coin_x, coin_y, COIN_SIZE, COIN_SIZE)
                    safe = True
                    for obstacle in self.obstacles:
                        if new_platform.x <= obstacle.x <= new_platform.x + new_platform.width:
                            obs_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
                            # Inflate by tolerance on each side (2x tolerance total)
                            if coin_rect.colliderect(obs_rect.inflate(COLLISION_TOLERANCE * 2, COLLISION_TOLERANCE * 2)):
                                safe = False
                                break
                    if safe:
                        self.star_coins.append(StarCoin(coin_x, coin_y, self.coin_image))
                        self.coins_spawned += 1
                        placed = True
                    attempts += 1

    def check_collisions(self) -> bool:
        """Check if the player collides with any obstacles using collision tolerance."""
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        for obstacle in self.obstacles:
            obs_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
            if player_rect.colliderect(obs_rect.inflate(COLLISION_TOLERANCE * 2, COLLISION_TOLERANCE * 2)):
                return True
        return False

    def draw_game(self, remaining_time: float, coins_collected: int) -> None:
        """Draw game objects and HUD elements."""
        self.player.draw(self.screen)
        self.spikes.draw(self.screen)
        for platform in self.platforms:
            platform.draw(self.screen)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        for coin in self.star_coins:
            coin.draw(self.screen)
        timer_text = self.font.render(f"Time: {int(remaining_time)}", True, BLACK)
        self.screen.blit(timer_text, (10, 10))
        coin_text = self.font.render(f"Coins: {coins_collected}", True, BLACK)
        coin_rect_disp = coin_text.get_rect(topright=(WIDTH - 10, 10))
        self.screen.blit(coin_text, coin_rect_disp)

    def run(self) -> None:
        """Main game loop."""
        self.coins_spawned = 0
        self.coins_collected = 0
        self.start_ticks = pygame.time.get_ticks()

        running = True
        while running:
            self.screen.fill(WHITE)
            elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            remaining_time = max(0, LEVEL_DURATION - elapsed_time)
            
            self.process_events()
            self.update_input()
            self.update_objects()
            self.spawn_new_platforms()
            
            self.player.move(self.platforms)
            
            # Check coin collection
            player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
            for coin in self.star_coins[:]:
                if player_rect.colliderect(coin.get_rect()):
                    self.star_coins.remove(coin)
                    self.coins_collected += 1
            
            self.draw_game(remaining_time, self.coins_collected)
            
            if self.check_collisions():
                running = False
            if self.player.y + self.player.height >= HEIGHT - SPIKE_HEIGHT:
                running = False
            if remaining_time <= 0:
                running = False
            
            pygame.display.update()
            self.clock.tick(30)
        
        # Game Over screen
        over_text = self.font.render("Game Over! Press any key or Y button to restart.", True, RED)
        over_rect = over_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(over_text, over_rect)
        pygame.display.update()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 3:
                        waiting = False

def main() -> None:
    while True:
        game = Game()
        game.run()

if __name__ == "__main__":
    main()
