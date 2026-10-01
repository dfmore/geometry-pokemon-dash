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

# We'll assume your UI and Screens code is in other files
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

# Joystick (hot-pluggable)
joystick = None


def _init_joystick() -> None:
    global joystick
    try:
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
    except pygame.error:
        joystick = None


_init_joystick()

class Game:
    # -----------------------------------------------------------------
    # Shared "Persistent" Class Variables
    # -----------------------------------------------------------------
    # These variables carry over across new calls to main() so you don't lose
    # your baseline_coins or lives each time you restart the game loop.
    persistent_baseline_coins = 0  # locked in from completed levels
    persistent_lives = 10         # total lives left
    _font = None                  # shared font, created lazily

    def __init__(self) -> None:
        # Load assets
        self.assets = load_assets()
        self.pokemon_images = self.assets['pokemon_images']
        self.coin_image = self.assets['coin_image']
        self.boing_sound = self.assets['boing_sound']
        self.coin_sound = self.assets['coin_sound']
        
        # Rendering
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        if Game._font is None:
            Game._font = pygame.font.Font(None, 36)
        self.font = Game._font
        
        # Level manager
        self.level_manager = LevelManager(self.pokemon_images, self.coin_image)
        self.current_level_index = self.level_manager.level_index

        # Player & spikes
        self.player = Player()
        self.spikes = Spikes()
        # Spawn resting on the first platform so no level seed can put the
        # player's feet below it (the swept landing test would then miss it).
        if self.level_manager.platforms:
            first = self.level_manager.platforms[0]
            self.player.y = first.y - self.player.height
            self.player.vel_y = 0
            self.player.on_ground = True

        # Bubbles
        self.bubbles = []

        # Timers for coyote time & jump buffer
        self.coyote_frames_charged = 0
        self.jump_buffer_frames_charged = 0
        self.coyote_frames_instant = 0
        self.jump_buffer_frames_instant = 0

        # For each new Game instance, read the persistent variables
        self.lives = Game.persistent_lives
        self.baseline_coins = Game.persistent_baseline_coins

        # This is the partial coins for the level attempt
        self.current_level_coins = 0
        self.final_coins_for_scoreboard = 0

        # Timers
        self.frame_count = 0
        self.level_complete = False

    # -----------------------------------------------------------------
    # EVENT PROCESSING
    # -----------------------------------------------------------------
    def process_events(self) -> None:
        global joystick
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

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.handle_charged_jump_release()

            # Joystick
            if event.type == pygame.JOYDEVICEADDED:
                try:
                    joystick = pygame.joystick.Joystick(event.device_index)
                    joystick.init()
                except pygame.error:
                    joystick = None
            if event.type == pygame.JOYDEVICEREMOVED:
                joystick = None
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    self.handle_charged_jump_press()
            if event.type == pygame.JOYBUTTONUP:
                if event.button == 0:
                    self.handle_charged_jump_release()

    # -----------------------------------------------------------------
    # UPDATING INPUT
    # -----------------------------------------------------------------
    def update_input(self) -> None:
        global joystick
        keys = pygame.key.get_pressed()
        can_charge = self.player.charging and (
            self.player.on_ground or self.coyote_frames_charged > 0
        )

        # Charged jump logic
        charge_held = bool(keys[pygame.K_SPACE])
        horizontal_input = 0
        if joystick is not None:
            try:
                if joystick.get_button(0):
                    charge_held = True
                horizontal_input = joystick.get_axis(0)
            except pygame.error:
                joystick = None
                horizontal_input = 0

        if charge_held and can_charge:
            self.player.charge_frames += 1
            # A quick tap stays a normal jump; only a longer hold charges.
            if self.player.charge_frames > c.POWER_HOLD_FRAMES:
                self.player.jump_charge += c.CHARGE_RATE
                if self.player.jump_charge > c.MAX_JUMP_STRENGTH:
                    self.player.jump_charge = c.MAX_JUMP_STRENGTH

        # Joystick nudge
        if joystick is not None:
            if abs(horizontal_input) < c.JOYSTICK_NUDGE_DEADZONE:
                horizontal_input = 0
            target_x = self.player.default_x + horizontal_input * c.JOYSTICK_NUDGE_RANGE
        else:
            target_x = self.player.default_x

        self.player.x += c.JOYSTICK_NUDGE_SPEED * (target_x - self.player.x)

    # -----------------------------------------------------------------
    # BUBBLES
    # -----------------------------------------------------------------
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

    # -----------------------------------------------------------------
    # UPDATE OBJECTS
    # -----------------------------------------------------------------
    def update_objects(self) -> None:
        self.level_manager.update_platforms()
        self.level_manager.update_obstacles()
        self.level_manager.update_coins()

    # -----------------------------------------------------------------
    # MAIN RUN
    # -----------------------------------------------------------------
    def run(self) -> None:
        """A single "game run". If the player completes the level or dies, we end and call screens."""
        self.current_level_coins = 0
        self.level_complete = False

        self.frame_count = 0

        running = True
        while running:
            self.frame_count += 1
            remaining_time = max(0, c.LEVEL_DURATION - self.frame_count / c.FPS)

            self.process_events()
            self.update_input()

            # Jump buffers expire
            if self.jump_buffer_frames_instant > 0:
                self.jump_buffer_frames_instant -= 1

            self.update_objects()

            # Move the player
            self.player.move(self.level_manager.platforms)

            # Coyote + Jump Buffer
            if self.player.on_ground:
                self.set_coyote_ground_frames('charged', c.COYOTE_FRAMES)
                self.set_coyote_ground_frames('instant', c.COYOTE_FRAMES)
                if self.jump_buffer_frames_for('instant') > 0:
                    self.handle_instant_jump()
                    self.set_jump_buffer_frames('instant', 0)
            else:
                self.dec_coyote_ground_frames('charged')
                self.dec_coyote_ground_frames('instant')

            # Walked off an edge while charging: jump instead of dropping the charge
            if (self.player.charging and not self.player.on_ground
                    and self.coyote_frames_charged <= 1):
                self.handle_charged_jump_release()

            # Coin collection
            player_rect = pygame.Rect(
                self.player.x, self.player.y,
                self.player.width, self.player.height
            )
            for coin in self.level_manager.star_coins[:]:
                if player_rect.colliderect(coin.get_rect()):
                    self.level_manager.star_coins.remove(coin)
                    self.current_level_coins += 1
                    self.coin_sound.play()

            # Collisions => death
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

            # Draw everything
            self.screen.fill(c.LIGHT_BLUE)
            self.update_bubbles()
            self.draw_bubbles()
            self.draw_game(remaining_time)

            pygame.display.update()
            self.clock.tick(c.FPS)

        # End of main loop => either we died or completed
        if self.level_complete:
            # Lock in partial coins from this level
            self.baseline_coins += self.current_level_coins
            # Save back to the persistent class variable
            Game.persistent_baseline_coins = self.baseline_coins

            self.current_level_coins = 0
            show_completion_screen(self)
        else:
            # Died
            self.lives -= 1
            Game.persistent_lives = self.lives

            if self.lives <= 0:
                # final attempt => scoreboard uses partial coins as well
                self.final_coins_for_scoreboard = self.baseline_coins + self.current_level_coins
                show_out_of_lives_screen(self)
            else:
                # died with lives left => lose partial
                self.current_level_coins = 0
                show_game_over_screen(self)

    # -----------------------------------------------------------------
    # DRAW GAME
    # -----------------------------------------------------------------
    def draw_game(self, remaining_time: float) -> None:
        """Draws black bar, player, spikes, platforms, coins, plus HUD and power-up bar."""
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

    # -----------------------------------------------------------------
    # CHARGED + INSTANT JUMP
    # -----------------------------------------------------------------
    def handle_charged_jump_press(self) -> None:
        # One jump key: on the ground it starts a tap-or-hold, in the air it
        # is the double jump (or a buffered normal jump if that is spent).
        if self.player.on_ground:
            self.player.charging = True
            self.player.jump_charge = c.MIN_JUMP_STRENGTH
            self.player.charge_frames = 0
        else:
            self.handle_instant_jump()

    def handle_charged_jump_release(self) -> None:
        if self.player.charging:
            if self.player.on_ground or self.coyote_frames_charged > 0:
                self.player.vel_y = -min(self.player.jump_charge, c.MAX_JUMP_STRENGTH)
                self.boing_sound.play()
                self.coyote_frames_instant = 0
                self.coyote_frames_charged = 0
            self.player.charging = False
            self.player.jump_charge = 0
            self.player.charge_frames = 0

    def handle_instant_jump(self) -> None:
        if self.coyote_ground_frames_for('instant') > 0 and (
            self.player.on_ground or self.player.vel_y >= 0
        ):
            self.player.vel_y = -c.MIN_JUMP_STRENGTH
            self.boing_sound.play()
            self.set_jump_buffer_frames('instant', 0)
            self.coyote_frames_instant = 0
            self.coyote_frames_charged = 0
        else:
            if not self.player.on_ground and self.player.can_double_jump:
                self.player.vel_y = -c.MIN_JUMP_STRENGTH
                self.player.can_double_jump = False
                self.boing_sound.play()
                self.coyote_frames_instant = 0
                self.coyote_frames_charged = 0
            else:
                self.set_jump_buffer_frames('instant', c.JUMP_BUFFER_FRAMES)

    # -----------------------------------------------------------------
    # COYOTE & JUMP BUFFER
    # -----------------------------------------------------------------
    def coyote_ground_frames_for(self, which_type: str) -> int:
        if which_type == 'charged':
            return self.coyote_frames_charged
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
