# game_manager.py

import pygame
import sys
import random

import src.config as c
import src.levels_config as lvl
from src.assets import load_assets
from src.player import Player
from src.spikes import Spikes
from src.level_manager import LevelManager
from src.bubbles import Bubble

# UI + screens
from src.ui import (
    draw_black_bar_behind_spikes,
    draw_powerup_bar,
    draw_hud_text
)
from src.screens import (
    show_completion_screen,
    show_game_over_screen,
    show_out_of_lives_screen
)

if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
else:
    joystick = None

class Game:
    persistent_lives = 10  # shared among restarts

    def __init__(self) -> None:
        # Load assets
        self.assets = load_assets()
        self.pokemon_images = self.assets['pokemon_images']
        self.coin_image = self.assets['coin_image']
        self.boing_sound = self.assets['boing_sound']
        self.coin_sound = self.assets['coin_sound']
        
        # Rendering & font
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Level manager
        self.level_manager = LevelManager(self.pokemon_images, self.coin_image)
        self.current_level_index = self.level_manager.level_index

        # Player + spikes
        self.player = Player()
        self.spikes = Spikes()

        # Bubbles
        self.bubbles = []

        # For coyote time + jump buffer
        self.coyote_frames_charged = 0
        self.jump_buffer_frames_charged = 0
        self.coyote_frames_instant = 0
        self.jump_buffer_frames_instant = 0

        # Lives
        self.lives = Game.persistent_lives

        # COINS: track "baseline" for completed levels + "current" for the attempt
        self.baseline_coins = 0
        self.current_level_coins = 0

        # Timer
        self.start_ticks = pygame.time.get_ticks()
        self.level_complete = False

    def process_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    self.handle_charged_jump_press()
                elif event.key == pygame.K_x:
                    self.handle_instant_jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.handle_charged_jump_release()

            # Joystick
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    self.handle_charged_jump_press()
                elif event.button == 2:
                    self.handle_instant_jump()
            if event.type == pygame.JOYBUTTONUP:
                if event.button == 0:
                    self.handle_charged_jump_release()

    def update_input(self) -> None:
        keys = pygame.key.get_pressed()

        # Charged jump logic
        if keys[pygame.K_SPACE] and self.player.charging and self.player.on_ground:
            self.player.jump_charge += c.CHARGE_RATE
            if self.player.jump_charge > c.MAX_JUMP_STRENGTH:
                self.player.jump_charge = c.MAX_JUMP_STRENGTH

        if joystick is not None and joystick.get_button(0) and self.player.charging and self.player.on_ground:
            self.player.jump_charge += c.CHARGE_RATE
            if self.player.jump_charge > c.MAX_JUMP_STRENGTH:
                self.player.jump_charge = c.MAX_JUMP_STRENGTH

        # Joystick nudge
        if joystick is not None:
            horizontal_input = joystick.get_axis(0)
            if abs(horizontal_input) < c.JOYSTICK_NUDGE_DEADZONE:
                horizontal_input = 0
            target_x = self.player.default_x + horizontal_input * c.JOYSTICK_NUDGE_RANGE
        else:
            target_x = self.player.default_x

        self.player.x += c.JOYSTICK_NUDGE_SPEED * (target_x - self.player.x)

    def update_bubbles(self):
        if len(self.bubbles) < c.BUBBLE_MAX_COUNT:
            if random.random() < c.BUBBLE_SPAWN_RATE:
                spike_height = int(c.SPIKE_HEIGHT_FRAC * c.HEIGHT)
                y_position = random.randint(c.HEIGHT - spike_height - 10,
                                            c.HEIGHT - spike_height + 10)
                x_position = random.randint(0, c.WIDTH)
                new_bubble = Bubble(x_position, y_position)
                self.bubbles.append(new_bubble)

        for bubble in self.bubbles[:]:
            bubble.update()
            if bubble.off_screen():
                self.bubbles.remove(bubble)

    def draw_bubbles(self):
        for bubble in self.bubbles:
            bubble.draw(self.screen)

    def update_objects(self) -> None:
        self.level_manager.update_platforms()
        self.level_manager.update_obstacles()
        self.level_manager.update_coins()

    def run(self) -> None:
        # Each run -> we start a "new attempt" of the level => current_level_coins = 0
        self.current_level_coins = 0

        running = True
        self.level_complete = False
        self.start_ticks = pygame.time.get_ticks()

        while running:
            self.screen.fill(c.LIGHT_BLUE)
            self.update_bubbles()
            self.draw_bubbles()

            elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            remaining_time = max(0, c.LEVEL_DURATION - elapsed_time)
            
            self.process_events()
            self.update_input()
            self.update_objects()

            # Move player
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
                    self.current_level_coins += 1
                    self.coin_sound.play()

            # Draw everything
            self.draw_game(remaining_time)

            # Check collisions => death
            if self.level_manager.check_obstacle_collisions(player_rect):
                running = False
                self.level_complete = False

            # Spikes => death
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

        # End of loop => either completed or died
        if self.level_complete:
            # Add coins for finishing
            self.baseline_coins += self.current_level_coins
            self.current_level_coins = 0
            show_completion_screen(self)
        else:
            # Died => lose the coins from this attempt
            self.current_level_coins = 0
            self.lives -= 1
            Game.persistent_lives = self.lives
            if self.lives <= 0:
                show_out_of_lives_screen(self)
            else:
                show_game_over_screen(self)

    # ------------------------------------------------------------------
    # draw_game (REQUIRED)
    # ------------------------------------------------------------------
    def draw_game(self, remaining_time: float) -> None:
        """
        Draw the spikes background, player, obstacles, coins, 
        plus the on-screen HUD: time, coins, level, lives, power-up bar.
        """
        # 1) Draw black bar behind spikes
        draw_black_bar_behind_spikes(self)

        # 2) Draw player & spikes
        self.player.draw(self.screen)
        self.spikes.draw(self.screen)

        # 3) Draw platforms, obstacles, coins
        for platform in self.level_manager.platforms:
            platform.draw(self.screen)
        for obs in self.level_manager.obstacles:
            obs.draw(self.screen)
        for coin in self.level_manager.star_coins:
            coin.draw(self.screen)

        # 4) HUD text (time, coins, level, lives)
        draw_hud_text(self, remaining_time)

        # 5) Power-up bar
        draw_powerup_bar(self)

    # ------------------------------------------------------------------
    # Jump / Coyote Time Methods
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


def main() -> None:
    while True:
        game = Game()
        game.run()

if __name__ == "__main__":
    main()
