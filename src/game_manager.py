# game_manager.py

import pygame
import sys
import random

import src.config as c
from src.assets import load_assets
from src.player import Player
from src.spikes import Spikes
from src.level_manager import LevelManager
from src.bubbles import Bubble

# Import UI & screens
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
# Import mechanics
from src.mechanics import (
    handle_charged_jump_press,
    handle_charged_jump_release,
    handle_instant_jump,
    coyote_ground_frames_for,
    set_coyote_ground_frames,
    dec_coyote_ground_frames,
    jump_buffer_frames_for,
    set_jump_buffer_frames
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

        # Timers & counters
        self.start_ticks = pygame.time.get_ticks()
        self.coins_collected = 0
        self.level_complete = False

        # Coyote time / jump buffer frames
        self.coyote_frames_charged = 0
        self.jump_buffer_frames_charged = 0
        self.coyote_frames_instant = 0
        self.jump_buffer_frames_instant = 0

        # Lives
        self.lives = Game.persistent_lives

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
                    handle_charged_jump_press(self)
                elif event.key == pygame.K_x:
                    handle_instant_jump(self)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    handle_charged_jump_release(self)

            # Joystick
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    handle_charged_jump_press(self)
                elif event.button == 2:
                    handle_instant_jump(self)
            if event.type == pygame.JOYBUTTONUP:
                if event.button == 0:
                    handle_charged_jump_release(self)

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
        self.level_manager.coins_spawned = 0
        self.coins_collected = 0
        self.start_ticks = pygame.time.get_ticks()
        
        running = True
        self.level_complete = False

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

            # Coyote + jump buffer
            if self.player.on_ground:
                set_coyote_ground_frames(self, 'charged', c.COYOTE_FRAMES)
                if jump_buffer_frames_for(self, 'charged') > 0:
                    handle_charged_jump_press(self)
                    set_jump_buffer_frames(self, 'charged', 0)

                set_coyote_ground_frames(self, 'instant', c.COYOTE_FRAMES)
                if jump_buffer_frames_for(self, 'instant') > 0:
                    handle_instant_jump(self)
                    set_jump_buffer_frames(self, 'instant', 0)
            else:
                dec_coyote_ground_frames(self, 'charged')
                dec_coyote_ground_frames(self, 'instant')

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

            # Collisions => death
            if self.level_manager.check_obstacle_collisions(player_rect):
                running = False
                self.level_complete = False

            # Spikes => death
            spike_height = int(c.SPIKE_HEIGHT_FRAC * c.HEIGHT)
            if (self.player.y + self.player.height) >= (c.HEIGHT - spike_height):
                running = False
                self.level_complete = False

            # Timer => complete
            if remaining_time <= 0:
                running = False
                self.level_complete = True

            pygame.display.update()
            self.clock.tick(30)

        # End of loop => died or time ran out
        if self.level_complete:
            from src.screens import show_completion_screen
            show_completion_screen(self)
        else:
            self.lives -= 1
            Game.persistent_lives = self.lives
            if self.lives <= 0:
                from src.screens import show_out_of_lives_screen
                show_out_of_lives_screen(self)
            else:
                from src.screens import show_game_over_screen
                show_game_over_screen(self)

    def draw_game(self, remaining_time: float) -> None:
        from src.ui import (
            draw_black_bar_behind_spikes,
            draw_powerup_bar,
            draw_hud_text
        )
        draw_black_bar_behind_spikes(self)

        self.player.draw(self.screen)
        self.spikes.draw(self.screen)

        for platform in self.level_manager.platforms:
            platform.draw(self.screen)
        for obs in self.level_manager.obstacles:
            obs.draw(self.screen)
        for coin in self.level_manager.star_coins:
            coin.draw(self.screen)

        draw_hud_text(self, remaining_time)
        draw_powerup_bar(self)

def main() -> None:
    while True:
        game = Game()
        game.run()

if __name__ == "__main__":
    main()
