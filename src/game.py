# game.py

import pygame
import random
import sys
import src.config as c
from src.assets import load_assets
from src.player import Player
from src.spikes import Spikes
from src.game_platform import Platform
from src.level_manager import LevelManager

# If a joystick is present, initialize it once
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
        self.coin_sound = self.assets['coin_sound']
        
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Level manager to handle platform/obstacle/coin creation
        self.level_manager = LevelManager(self.pokemon_images, self.coin_image)

        # Create an initial platform near the bottom of the screen
        # For example, ~70% down the screen:
        initial_y = int(0.7 * c.HEIGHT)
        first_platform = Platform(100, initial_y)
        self.level_manager.platforms.append(first_platform)
        
        # Generate enough platforms to fill up the screen
        self.level_manager.generate_initial_platforms(c.WIDTH)
        
        # Create the Player and Spikes
        self.player = Player()
        self.spikes = Spikes()

        self.start_ticks = pygame.time.get_ticks()
        self.coins_collected = 0

    def process_events(self) -> None:
        """
        Handles all input: keyboard, joystick, window events.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                # Begin charging jump if on ground
                if event.key == pygame.K_SPACE:
                    if self.player.on_ground:
                        self.player.charging = True
                        self.player.jump_charge = c.MIN_JUMP_STRENGTH

                # Instant jump (X key) -> check ground or double-jump
                if event.key == pygame.K_x:
                    if self.player.on_ground:
                        self.player.vel_y = -c.MIN_JUMP_STRENGTH
                        self.boing_sound.play()
                    elif not self.player.on_ground and self.player.can_double_jump:
                        self.player.vel_y = -c.MIN_JUMP_STRENGTH
                        self.player.can_double_jump = False
                        self.boing_sound.play()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and self.player.charging:
                    if self.player.on_ground:
                        self.player.vel_y = -self.player.jump_charge
                        self.boing_sound.play()
                    self.player.charging = False
                    self.player.jump_charge = 0

            # Joystick input
            if event.type == pygame.JOYBUTTONDOWN:
                # A button
                if event.button == 0:
                    if self.player.on_ground:
                        self.player.charging = True
                        self.player.jump_charge = c.MIN_JUMP_STRENGTH

                # X button
                if event.button == 2:
                    if self.player.on_ground:
                        self.player.vel_y = -c.MIN_JUMP_STRENGTH
                        self.boing_sound.play()
                    elif not self.player.on_ground and self.player.can_double_jump:
                        self.player.vel_y = -c.MIN_JUMP_STRENGTH
                        self.player.can_double_jump = False
                        self.boing_sound.play()

            if event.type == pygame.JOYBUTTONUP:
                # Releasing the A button
                if event.button == 0 and self.player.charging:
                    if self.player.on_ground:
                        self.player.vel_y = -self.player.jump_charge
                        self.boing_sound.play()
                    self.player.charging = False
                    self.player.jump_charge = 0

    def update_input(self) -> None:
        """
        Handles continuous input (keys held down), such as charging jump.
        """
        keys = pygame.key.get_pressed()

        # Charge jump while holding SPACE if on ground
        if keys[pygame.K_SPACE] and self.player.charging and self.player.on_ground:
            self.player.jump_charge += c.CHARGE_RATE
            if self.player.jump_charge > c.MAX_JUMP_STRENGTH:
                self.player.jump_charge = c.MAX_JUMP_STRENGTH

        # Joystick continuous check
        if joystick is not None and joystick.get_button(0) and self.player.charging and self.player.on_ground:
            self.player.jump_charge += c.CHARGE_RATE
            if self.player.jump_charge > c.MAX_JUMP_STRENGTH:
                self.player.jump_charge = c.MAX_JUMP_STRENGTH

    def update_objects(self) -> None:
        """
        Updates movement of platforms, obstacles, coins, etc.
        """
        self.level_manager.update_platforms()
        self.level_manager.update_obstacles()
        self.level_manager.update_coins()

    def run(self) -> None:
        """
        Main game loop: handles events, updates logic, draws everything.
        """
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

            # Player movement and collisions with platforms
            self.player.move(self.level_manager.platforms)

            # Check coin collection
            player_rect = pygame.Rect(self.player.x, self.player.y,
                                      self.player.width, self.player.height)
            for coin in self.level_manager.star_coins[:]:
                if player_rect.colliderect(coin.get_rect()):
                    self.level_manager.star_coins.remove(coin)
                    self.coins_collected += 1
                    self.coin_sound.play()
            
            # Draw everything
            self.draw_game(remaining_time)

            # Check obstacle collisions
            if self.level_manager.check_obstacle_collisions(player_rect):
                running = False

            # Check if player fell into spikes
            # SPIKE_HEIGHT_FRAC => fraction-based spike height
            # Compare the bottom of the player to (c.HEIGHT - spike_height)
            spike_height = int(c.SPIKE_HEIGHT_FRAC * c.HEIGHT)
            if (self.player.y + self.player.height) >= (c.HEIGHT - spike_height):
                running = False

            # Check if time is up
            if remaining_time <= 0:
                running = False

            pygame.display.update()
            self.clock.tick(30)

        # Game Over
        over_text = self.font.render("Game Over! Press any key or Y button to restart.", True, c.RED)
        over_rect = over_text.get_rect(center=(c.WIDTH // 2, c.HEIGHT // 2))
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
                    # 'Y' button
                    if event.button == 3:
                        waiting = False

    def draw_game(self, remaining_time: float) -> None:
        """
        Draws the player, spikes, platforms, obstacles, coins, and UI text.
        """
        self.player.draw(self.screen)
        self.spikes.draw(self.screen)
        
        # Platforms, obstacles, coins
        for platform in self.level_manager.platforms:
            platform.draw(self.screen)
        for obs in self.level_manager.obstacles:
            obs.draw(self.screen)
        for coin in self.level_manager.star_coins:
            coin.draw(self.screen)

        # Timer
        timer_text = self.font.render(f"Time: {int(remaining_time)}", True, c.BLACK)
        self.screen.blit(timer_text, (10, 10))

        # Coin count
        coin_text = self.font.render(f"Coins: {self.coins_collected}", True, c.BLACK)
        coin_rect_disp = coin_text.get_rect(topright=(c.WIDTH - 10, 10))
        self.screen.blit(coin_text, coin_rect_disp)

def main() -> None:
    """
    Creates a new Game instance and runs it in an endless loop.
    """
    while True:
        game = Game()
        game.run()

if __name__ == "__main__":
    main()
