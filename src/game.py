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
        
        # LevelManager loads the chosen level from config
        self.level_manager = LevelManager(self.pokemon_images, self.coin_image)
        self.current_level_index = self.level_manager.level_index

        # Player + Spikes
        self.player = Player()
        self.spikes = Spikes()

        # Timers for coyote time + jump buffer for “charged” and “instant”
        self.coyote_frames_charged = 0
        self.jump_buffer_frames_charged = 0
        self.coyote_frames_instant = 0
        self.jump_buffer_frames_instant = 0

        self.start_ticks = pygame.time.get_ticks()
        self.coins_collected = 0

        self.level_complete = False

    # ------------------------------------------------------------------
    # HELPER METHODS: Coyote Time & Jump Buffer
    # ------------------------------------------------------------------

    def coyote_ground_frames_for(self, which_type: str) -> int:
        if which_type == 'charged':
            return self.coyote_frames_charged
        else:
            return self.coyote_frames_instant

    def set_coyote_ground_frames(self, which_type: str, value: int) -> None:
        if which_type == 'charged':
            self.coyote_frames_charged = value
        else:
            self.coyote_frames_instant = value

    def dec_coyote_ground_frames(self, which_type: str) -> None:
        if which_type == 'charged':
            if self.coyote_frames_charged > 0:
                self.coyote_frames_charged -= 1
        else:
            if self.coyote_frames_instant > 0:
                self.coyote_frames_instant -= 1

    def jump_buffer_frames_for(self, which_type: str) -> int:
        if which_type == 'charged':
            return self.jump_buffer_frames_charged
        else:
            return self.jump_buffer_frames_instant

    def set_jump_buffer_frames(self, which_type: str, value: int) -> None:
        if which_type == 'charged':
            self.jump_buffer_frames_charged = value
        else:
            self.jump_buffer_frames_instant = value

    # ------------------------------------------------------------------
    # Jump Methods (DRY)
    # ------------------------------------------------------------------

    def handle_charged_jump_press(self) -> None:
        if self.coyote_ground_frames_for('charged') > 0:
            self.player.charging = True
            self.player.jump_charge = c.MIN_JUMP_STRENGTH
            self.set_jump_buffer_frames('charged', 0)
        else:
            self.set_jump_buffer_frames('charged', c.JUMP_BUFFER_FRAMES)

    def handle_charged_jump_release(self) -> None:
        if self.player.charging:
            if self.player.on_ground:
                self.player.vel_y = -self.player.jump_charge
                self.boing_sound.play()
            self.player.charging = False
            self.player.jump_charge = 0

    def handle_instant_jump(self) -> None:
        if self.coyote_ground_frames_for('instant') > 0:
            self.player.vel_y = -c.MIN_JUMP_STRENGTH
            self.boing_sound.play()
            self.set_jump_buffer_frames('instant', 0)
        else:
            if not self.player.on_ground and self.player.can_double_jump:
                self.player.vel_y = -c.MIN_JUMP_STRENGTH
                self.player.can_double_jump = False
                self.boing_sound.play()
            else:
                self.set_jump_buffer_frames('instant', c.JUMP_BUFFER_FRAMES)

    # ------------------------------------------------------------------
    # EVENT PROCESSING
    # ------------------------------------------------------------------

    def process_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_SPACE:
                    self.handle_charged_jump_press()

                if event.key == pygame.K_x:
                    self.handle_instant_jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.handle_charged_jump_release()

            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    self.handle_charged_jump_press()
                if event.button == 2:
                    self.handle_instant_jump()

            if event.type == pygame.JOYBUTTONUP:
                if event.button == 0:
                    self.handle_charged_jump_release()

    # ------------------------------------------------------------------
    # CONTINUOUS INPUT => CHARGING
    # ------------------------------------------------------------------

    def update_input(self) -> None:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and self.player.charging and self.player.on_ground:
            self.player.jump_charge += c.CHARGE_RATE
            if self.player.jump_charge > c.MAX_JUMP_STRENGTH:
                self.player.jump_charge = c.MAX_JUMP_STRENGTH

        if joystick is not None and joystick.get_button(0) and self.player.charging and self.player.on_ground:
            self.player.jump_charge += c.CHARGE_RATE
            if self.player.jump_charge > c.MAX_JUMP_STRENGTH:
                self.player.jump_charge = c.MAX_JUMP_STRENGTH

    # ------------------------------------------------------------------
    # UPDATE OBJECTS
    # ------------------------------------------------------------------

    def update_objects(self) -> None:
        self.level_manager.update_platforms()
        self.level_manager.update_obstacles()
        self.level_manager.update_coins()

    # ------------------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------------------

    def run(self) -> None:
        self.level_manager.coins_spawned = 0
        self.coins_collected = 0
        self.start_ticks = pygame.time.get_ticks()
        
        running = True
        self.level_complete = False

        while running:
            self.screen.fill(c.WHITE)
            elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            remaining_time = max(0, c.LEVEL_DURATION - elapsed_time)
            
            self.process_events()
            self.update_input()
            self.update_objects()

            # Player movement
            self.player.move(self.level_manager.platforms)

            # Coyote + Jump Buffer
            if self.player.on_ground:
                self.set_coyote_ground_frames('charged', c.COYOTE_FRAMES)
                if self.jump_buffer_frames_for('charged') > 0:
                    self.handle_charged_jump_press()
                    self.set_jump_buffer_frames('charged', 0)

                self.set_coyote_ground_frames('instant', c.COYOTE_FRAMES)
                if self.jump_buffer_frames_for('instant') > 0:
                    self.handle_instant_jump()
                    self.set_jump_buffer_frames('instant', 0)
            else:
                self.dec_coyote_ground_frames('charged')
                self.dec_coyote_ground_frames('instant')

            # Coin collection
            player_rect = pygame.Rect(self.player.x, self.player.y,
                                      self.player.width, self.player.height)
            for coin in self.level_manager.star_coins[:]:
                if player_rect.colliderect(coin.get_rect()):
                    self.level_manager.star_coins.remove(coin)
                    self.coins_collected += 1
                    self.coin_sound.play()
            
            # Draw
            self.draw_game(remaining_time)

            # Obstacle collisions => the player died => end loop
            if self.level_manager.check_obstacle_collisions(player_rect):
                running = False  
                self.level_complete = False

            # Spikes => the player died => end loop
            spike_height = int(c.SPIKE_HEIGHT_FRAC * c.HEIGHT)
            if (self.player.y + self.player.height) >= (c.HEIGHT - spike_height):
                running = False
                self.level_complete = False

            # Timer => level complete
            if remaining_time <= 0:
                running = False
                self.level_complete = True

            pygame.display.update()
            self.clock.tick(30)

        # End of loop => either died or time ran out
        if self.level_complete:
            # Show "Level X Complete" and then proceed or end
            over_text = self.font.render(
                f"Level {self.current_level_index + 1} Complete! Press any key or Y to continue.",
                True, c.RED
            )
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
                        if event.button == 3:  # 'Y'
                            waiting = False

            # Move to next level if available
            if self.current_level_index < len(c.LEVELS) - 1:
                c.CURRENT_LEVEL += 1
                main()  # re-run with next level
            else:
                # All levels complete
                self.show_final_message("All levels completed! Thanks for playing.")
        else:
            # The player died, so let's show "Game Over! Retry this level."
            over_text = self.font.render(
                f"Game Over! Press any key or Y button to retry level {self.current_level_index + 1}",
                True, c.RED
            )
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
                        if event.button == 3:
                            waiting = False

            # We do NOT reset c.CURRENT_LEVEL to 0 => we keep same level
            main()  # re-run the same level

    def show_final_message(self, msg: str) -> None:
        over_text = self.font.render(msg, True, c.RED)
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
                    if event.button == 3:
                        waiting = False

    def draw_game(self, remaining_time: float) -> None:
        """
        Draws the player, spikes, platforms, obstacles, coins, and UI text.
        Also draws the level counter at the top.
        """
        self.player.draw(self.screen)
        self.spikes.draw(self.screen)
        
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

        # Level counter
        level_text = self.font.render(
            f"Level: {self.current_level_index + 1} / {len(c.LEVELS)}", True, c.BLACK
        )
        level_rect = level_text.get_rect(center=(c.WIDTH // 2, 20))
        self.screen.blit(level_text, level_rect)

def main() -> None:
    while True:
        game = Game()
        game.run()

if __name__ == "__main__":
    main()
