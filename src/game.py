# game.py
import pygame
import random
import src.config as c
from src.assets import load_assets
from src.player import Player
from src.spikes import Spikes
from src.game_platform import Platform
from src.level_manager import LevelManager  # Our new spawner/manager

if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
else:
    joystick = None

class Game:
    def __init__(self) -> None:
        self.assets = load_assets()
        self.pokemon_images = self.assets['pokemon_images']
        self.coin_image = self.assets['coin_image']
        self.boing_sound = self.assets['boing_sound']
        
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Level manager holds platforms/obstacles/coins
        self.level_manager = LevelManager(self.pokemon_images, self.coin_image)

        # Insert an initial platform
        first_platform = Platform(100, 320)
        self.level_manager.platforms.append(first_platform)
        # Generate enough initial platforms to fill the screen
        self.level_manager.generate_initial_platforms(c.WIDTH)
        
        self.player = Player()
        self.spikes = Spikes()

        self.start_ticks = pygame.time.get_ticks()
        self.coins_collected = 0

    def process_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            # Keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.player.on_ground:
                        self.player.charging = True
                        self.player.jump_charge = c.MIN_JUMP_STRENGTH
                if event.key == pygame.K_x:
                    self.boing_sound.play()
                    if self.player.on_ground:
                        self.player.vel_y = -c.MIN_JUMP_STRENGTH
                    elif not self.player.on_ground and self.player.can_double_jump:
                        self.player.vel_y = -c.MIN_JUMP_STRENGTH
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
                if event.button == 0:  # e.g. 'A' on many controllers
                    if self.player.on_ground:
                        self.player.charging = True
                        self.player.jump_charge = c.MIN_JUMP_STRENGTH
                if event.button == 2:  # e.g. 'X' on many controllers
                    self.boing_sound.play()
                    if self.player.on_ground:
                        self.player.vel_y = -c.MIN_JUMP_STRENGTH
                    elif not self.player.on_ground and self.player.can_double_jump:
                        self.player.vel_y = -c.MIN_JUMP_STRENGTH
                        self.player.can_double_jump = False
            if event.type == pygame.JOYBUTTONUP:
                if event.button == 0 and self.player.charging:
                    self.boing_sound.play()
                    if self.player.on_ground:
                        self.player.vel_y = -self.player.jump_charge
                    self.player.charging = False
                    self.player.jump_charge = 0

    def update_input(self) -> None:
        keys = pygame.key.get_pressed()
        # Charging jump
        if keys[pygame.K_SPACE] and self.player.charging and self.player.on_ground:
            self.player.jump_charge += c.CHARGE_RATE
            if self.player.jump_charge > c.MAX_JUMP_STRENGTH:
                self.player.jump_charge = c.MAX_JUMP_STRENGTH
        # Joystick
        if joystick is not None and joystick.get_button(0) and self.player.charging and self.player.on_ground:
            self.player.jump_charge += c.CHARGE_RATE
            if self.player.jump_charge > c.MAX_JUMP_STRENGTH:
                self.player.jump_charge = c.MAX_JUMP_STRENGTH

    def update_objects(self) -> None:
        self.level_manager.update_platforms()
        self.level_manager.update_obstacles()
        self.level_manager.update_coins()

    def run(self) -> None:
        self.level_manager.coins_spawned = 0
        self.coins_collected = 0
        self.start_ticks = pygame.time.get_ticks()
        
        running = True
        while running:
            self.screen.fill(c.WHITE)
            elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            remaining_time = max(0, c.LEVEL_DURATION - elapsed_time)
            
            self.process_events()
            self.update_input()
            self.update_objects()
            self.level_manager.spawn_new_platforms(c.WIDTH)

            # Let the Player handle collisions with current platforms
            self.player.move(self.level_manager.platforms)

            # Check coin collection
            player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
            for coin in self.level_manager.star_coins[:]:
                if player_rect.colliderect(coin.get_rect()):
                    self.level_manager.star_coins.remove(coin)
                    self.coins_collected += 1
            
            # Draw everything
            self.draw_game(remaining_time)

            # Check collisions with obstacles
            if self.level_manager.check_obstacle_collisions(player_rect):
                running = False

            # Check if player fell into spikes
            if self.player.y + self.player.height >= c.HEIGHT - c.SPIKE_HEIGHT:
                running = False

            # Check time
            if remaining_time <= 0:
                running = False

            pygame.display.update()
            self.clock.tick(30)

        # Game Over
        over_text = self.font.render("Game Over! Press any key or Y button to restart.", True, c.RED)
        over_rect = over_text.get_rect(center=(c.WIDTH//2, c.HEIGHT//2))
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
                    if event.button == 3:  # 'Y' on some controllers
                        waiting = False

    def draw_game(self, remaining_time):
        self.player.draw(self.screen)
        self.spikes.draw(self.screen)
        
        # Draw platforms, obstacles, coins
        for platform in self.level_manager.platforms:
            platform.draw(self.screen)
        for obs in self.level_manager.obstacles:
            obs.draw(self.screen)
        for coin in self.level_manager.star_coins:
            coin.draw(self.screen)

        timer_text = self.font.render(f"Time: {int(remaining_time)}", True, c.BLACK)
        self.screen.blit(timer_text, (10, 10))

        coin_text = self.font.render(f"Coins: {self.coins_collected}", True, c.BLACK)
        coin_rect_disp = coin_text.get_rect(topright=(c.WIDTH - 10, 10))
        self.screen.blit(coin_text, coin_rect_disp)

def main() -> None:
    while True:
        game = Game()
        game.run()

if __name__ == "__main__":
    main()
