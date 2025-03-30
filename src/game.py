# game.py

import pygame
import sys
import random  # for bubble spawning
import src.config as c
from src.assets import load_assets
from src.player import Player
from src.spikes import Spikes
from src.level_manager import LevelManager
from src.bubbles import Bubble

# Check for joystick/gamepad availability
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
else:
    joystick = None

class Game:
    def __init__(self) -> None:
        # Load assets (images, sounds, etc.)
        self.assets = load_assets()
        self.pokemon_images = self.assets['pokemon_images']
        self.coin_image = self.assets['coin_image']
        self.boing_sound = self.assets['boing_sound']
        self.coin_sound = self.assets['coin_sound']
        
        # Primary rendering surface, timing, and font
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Level manager loads the chosen level from config
        self.level_manager = LevelManager(self.pokemon_images, self.coin_image)
        self.current_level_index = self.level_manager.level_index

        # Player + Spikes
        self.player = Player()
        self.spikes = Spikes()

        # Bubble storage
        self.bubbles = []

        # Timers for coyote time + jump buffer (two types of jumps)
        self.coyote_frames_charged = 0
        self.jump_buffer_frames_charged = 0
        self.coyote_frames_instant = 0
        self.jump_buffer_frames_instant = 0

        # Tracking time, coins, and completion
        self.start_ticks = pygame.time.get_ticks()
        self.coins_collected = 0
        self.level_complete = False

    # ------------------------------------------------------------------
    # COYOTE TIME & JUMP BUFFER HELPERS
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
    # JUMP METHODS
    # ------------------------------------------------------------------

    def handle_charged_jump_press(self) -> None:
        # If we still have "coyote" ground frames left, begin charging
        if self.coyote_ground_frames_for('charged') > 0:
            self.player.charging = True
            self.player.jump_charge = c.MIN_JUMP_STRENGTH
            self.set_jump_buffer_frames('charged', 0)
        else:
            # If no ground frames left, store the jump input for a few frames
            self.set_jump_buffer_frames('charged', c.JUMP_BUFFER_FRAMES)

    def handle_charged_jump_release(self) -> None:
        # If we were charging, finalize the jump
        if self.player.charging:
            if self.player.on_ground:
                self.player.vel_y = -self.player.jump_charge
                self.boing_sound.play()
            self.player.charging = False
            self.player.jump_charge = 0

    def handle_instant_jump(self) -> None:
        # "Instant" jump is triggered right away if on ground or within coyote frames
        if self.coyote_ground_frames_for('instant') > 0:
            self.player.vel_y = -c.MIN_JUMP_STRENGTH
            self.boing_sound.play()
            self.set_jump_buffer_frames('instant', 0)
        else:
            # If in mid-air and we have a double jump available, use it
            if not self.player.on_ground and self.player.can_double_jump:
                self.player.vel_y = -c.MIN_JUMP_STRENGTH
                self.player.can_double_jump = False
                self.boing_sound.play()
            else:
                # else store the jump input (jump buffer)
                self.set_jump_buffer_frames('instant', c.JUMP_BUFFER_FRAMES)

    # ------------------------------------------------------------------
    # EVENT HANDLING
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
                elif event.key == pygame.K_SPACE:
                    self.handle_charged_jump_press()
                elif event.key == pygame.K_x:
                    self.handle_instant_jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.handle_charged_jump_release()

            # Joystick / gamepad
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # e.g. 'A' button
                    self.handle_charged_jump_press()
                elif event.button == 2:  # e.g. 'X' button
                    self.handle_instant_jump()

            if event.type == pygame.JOYBUTTONUP:
                if event.button == 0:
                    self.handle_charged_jump_release()

    def update_input(self) -> None:
        """Check continuous inputs each frame (holding space to charge jump, etc.)."""
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

        # ----------------------------------------------------------------
        # Nudge the player's X using the left stick
        # ----------------------------------------------------------------
        if joystick is not None:
            horizontal_input = joystick.get_axis(0)  # left stick X axis => -1.0 to +1.0
            if abs(horizontal_input) < c.JOYSTICK_NUDGE_DEADZONE:
                horizontal_input = 0

            # Calculate target X offset from default_x
            target_x = self.player.default_x + horizontal_input * c.JOYSTICK_NUDGE_RANGE
        else:
            # No joystick => no offset
            target_x = self.player.default_x

        # Smoothly move the player's x toward target_x each frame:
        self.player.x += c.JOYSTICK_NUDGE_SPEED * (target_x - self.player.x)

    # ------------------------------------------------------------------
    # BUBBLES
    # ------------------------------------------------------------------

    def update_bubbles(self):
        """
        - Possibly spawn new bubbles if under BUBBLE_MAX_COUNT
        - Each frame, there's a c.BUBBLE_SPAWN_RATE chance to spawn
        - Remove bubbles that go off screen
        """
        # 1) Spawn new bubble if possible
        if len(self.bubbles) < c.BUBBLE_MAX_COUNT:
            if random.random() < c.BUBBLE_SPAWN_RATE:
                # We'll spawn them near the bottom, just above spikes
                spike_height = int(c.SPIKE_HEIGHT_FRAC * c.HEIGHT)
                y_position = random.randint(c.HEIGHT - spike_height - 10,
                                            c.HEIGHT - spike_height + 10)
                x_position = random.randint(0, c.WIDTH)
                new_bubble = Bubble(x_position, y_position)
                self.bubbles.append(new_bubble)

        # 2) Update existing bubbles
        for bubble in self.bubbles[:]:
            bubble.update()
            if bubble.off_screen():
                self.bubbles.remove(bubble)

    def draw_bubbles(self):
        """Draw all bubbles behind the main game objects."""
        for bubble in self.bubbles:
            bubble.draw(self.screen)

    # ------------------------------------------------------------------
    # UPDATE OBJECTS
    # ------------------------------------------------------------------

    def update_objects(self) -> None:
        self.level_manager.update_platforms()
        self.level_manager.update_obstacles()
        self.level_manager.update_coins()

    # ------------------------------------------------------------------
    # MAIN GAME LOOP
    # ------------------------------------------------------------------

    def run(self) -> None:
        self.level_manager.coins_spawned = 0
        self.coins_collected = 0
        self.start_ticks = pygame.time.get_ticks()
        
        running = True
        self.level_complete = False

        while running:
            # 1) Fill background light blue
            self.screen.fill(c.LIGHT_BLUE)

            # 2) Update & draw bubbles behind everything
            self.update_bubbles()
            self.draw_bubbles()

            # 3) Main logic
            elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            remaining_time = max(0, c.LEVEL_DURATION - elapsed_time)
            
            self.process_events()
            self.update_input()
            self.update_objects()

            # Move player
            self.player.move(self.level_manager.platforms)

            # Handle coyote + jump buffer
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

            # Check coin collection
            player_rect = pygame.Rect(self.player.x, self.player.y,
                                      self.player.width, self.player.height)
            for coin in self.level_manager.star_coins[:]:
                if player_rect.colliderect(coin.get_rect()):
                    self.level_manager.star_coins.remove(coin)
                    self.coins_collected += 1
                    self.coin_sound.play()
            
            # Draw the main game elements (player, spikes, platforms, etc.)
            self.draw_game(remaining_time)

            # Check collisions
            if self.level_manager.check_obstacle_collisions(player_rect):
                running = False  
                self.level_complete = False

            # Spikes => game over if player touches them
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

        # End-of-loop => either died or time ran out
        if self.level_complete:
            self.show_completion_screen()
        else:
            self.show_game_over_screen()

    # ------------------------------------------------------------------
    # DRAW MAIN GAME OBJECTS
    # ------------------------------------------------------------------

    def draw_game(self, remaining_time: float) -> None:
        """
        Draws the player, spikes, platforms, obstacles, coins, 
        and some on-screen text (timer, coin count, etc.).
        """
        # Player & spikes
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

        # Level counter
        level_text = self.font.render(
            f"Level: {self.current_level_index + 1} / {len(c.LEVELS)}", True, c.BLACK
        )
        level_rect = level_text.get_rect(center=(c.WIDTH // 2, 20))
        self.screen.blit(level_text, level_rect)
        
        # 1) Black rectangle behind spikes
        spike_height = int(c.SPIKE_HEIGHT_FRAC * c.HEIGHT)
        # The top of our black bar is (HEIGHT - spike_height - overlap)
        black_bar_top = c.HEIGHT - spike_height - c.SPIKE_BG_OVERLAP
        black_bar_height = spike_height + c.SPIKE_BG_OVERLAP

        # Make sure we don't go negative if overlap is large
        if black_bar_top < 0:
            black_bar_top = 0
            black_bar_height = c.HEIGHT

        # Draw black rectangle across the full screen width
        pygame.draw.rect(
            self.screen,
            c.SPIKE_BG_COLOR,
            (0, black_bar_top, c.WIDTH, black_bar_height)
        )

        # 2) Draw the player, spikes, platforms, etc. on top
        self.player.draw(self.screen)
        self.spikes.draw(self.screen)

        for platform in self.level_manager.platforms:
            platform.draw(self.screen)
        for obs in self.level_manager.obstacles:
            obs.draw(self.screen)
        for coin in self.level_manager.star_coins:
            coin.draw(self.screen)

        # 3) UI text (timer, coin count, etc.)
        timer_text = self.font.render(f"Time: {int(remaining_time)}", True, c.BLACK)
        self.screen.blit(timer_text, (10, 10))

        coin_text = self.font.render(f"Coins: {self.coins_collected}", True, c.BLACK)
        coin_rect_disp = coin_text.get_rect(topright=(c.WIDTH - 10, 10))
        self.screen.blit(coin_text, coin_rect_disp)

        level_text = self.font.render(
            f"Level: {self.current_level_index + 1} / {len(c.LEVELS)}", True, c.BLACK
        )
        level_rect = level_text.get_rect(center=(c.WIDTH // 2, 20))
        self.screen.blit(level_text, level_rect)

    # ------------------------------------------------------------------
    # SCREENS
    # ------------------------------------------------------------------

    def show_completion_screen(self) -> None:
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
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 3:  # 'Y' button
                        waiting = False

        # If more levels remain, move to next level
        if self.current_level_index < len(c.LEVELS) - 1:
            c.CURRENT_LEVEL += 1
            main()  # re-run with next level
        else:
            self.show_final_message("All levels completed! Thanks for playing.")

    def show_game_over_screen(self) -> None:
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
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 3:  # 'Y' button
                        waiting = False

        # Retry the same level
        main()

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
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 3:
                        waiting = False

def main() -> None:
    """
    Start a new game loop repeatedly.
    """
    while True:
        game = Game()
        game.run()

if __name__ == "__main__":
    main()
