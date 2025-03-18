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
        
        # Level manager
        self.level_manager = LevelManager(self.pokemon_images, self.coin_image)

        # Create an initial platform (70% down the screen)
        initial_y = int(0.7 * c.HEIGHT)
        first_platform = Platform(100, initial_y)
        self.level_manager.platforms.append(first_platform)
        self.level_manager.generate_initial_platforms(c.WIDTH)
        
        # Player + Spikes
        self.player = Player()
        self.spikes = Spikes()

        # Timers for coyote time (still can jump after leaving ground)
        # and jump buffer (pressed jump just before landing).
        self.coyote_frames_charged = 0
        self.jump_buffer_frames_charged = 0

        self.coyote_frames_instant = 0
        self.jump_buffer_frames_instant = 0

        self.start_ticks = pygame.time.get_ticks()
        self.coins_collected = 0

    # ------------------------------------------------------------------
    # HELPER METHODS: Coyote Time & Jump Buffer
    # ------------------------------------------------------------------

    def coyote_ground_frames_for(self, which_type:str) -> int:
        """
        Returns how many coyote frames remain for 'charged' or 'instant' jump.
        """
        if which_type == 'charged':
            return self.coyote_frames_charged
        else:  # 'instant'
            return self.coyote_frames_instant

    def set_coyote_ground_frames(self, which_type:str, value:int) -> None:
        """Sets the coyote frames for the requested jump type."""
        if which_type == 'charged':
            self.coyote_frames_charged = value
        else:
            self.coyote_frames_instant = value

    def dec_coyote_ground_frames(self, which_type:str) -> None:
        """Decrement coyote frames if > 0."""
        if which_type == 'charged':
            if self.coyote_frames_charged > 0:
                self.coyote_frames_charged -= 1
        else:
            if self.coyote_frames_instant > 0:
                self.coyote_frames_instant -= 1

    def jump_buffer_frames_for(self, which_type:str) -> int:
        """Returns how many jump-buffer frames remain for 'charged' or 'instant'."""
        if which_type == 'charged':
            return self.jump_buffer_frames_charged
        else:
            return self.jump_buffer_frames_instant

    def set_jump_buffer_frames(self, which_type:str, value:int) -> None:
        if which_type == 'charged':
            self.jump_buffer_frames_charged = value
        else:
            self.jump_buffer_frames_instant = value

    # ------------------------------------------------------------------
    # Jump Methods (DRY)
    # ------------------------------------------------------------------

    def handle_charged_jump_press(self) -> None:
        """
        Called when user first presses the 'charged jump' (Space or button 0).
        Incorporates coyote time + jump buffer for the charged jump.
        """
        if self.coyote_ground_frames_for('charged') > 0:
            # We treat that as effectively on_ground
            self.player.charging = True
            self.player.jump_charge = c.MIN_JUMP_STRENGTH
            self.set_jump_buffer_frames('charged', 0)  # Clear any buffer
        else:
            # Not on ground + no coyote frames => store a jump buffer
            self.set_jump_buffer_frames('charged', c.JUMP_BUFFER_FRAMES)

    def handle_charged_jump_release(self) -> None:
        """
        Called when user releases the 'charged jump' button.
        """
        if self.player.charging:
            if self.player.on_ground:
                self.player.vel_y = -self.player.jump_charge
                self.boing_sound.play()
            self.player.charging = False
            self.player.jump_charge = 0

    def handle_instant_jump(self) -> None:
        """
        Called when user presses the 'instant jump' button (X or button 2).
        Incorporates coyote time + jump buffer + double jump.
        """
        # If we have coyote frames, treat as if on the ground
        if self.coyote_ground_frames_for('instant') > 0:
            self.player.vel_y = -c.MIN_JUMP_STRENGTH
            self.boing_sound.play()
            self.set_jump_buffer_frames('instant', 0)  # no need to buffer
        else:
            # No coyote frames left: check if we can do a double jump
            if not self.player.on_ground and self.player.can_double_jump:
                self.player.vel_y = -c.MIN_JUMP_STRENGTH
                self.player.can_double_jump = False
                self.boing_sound.play()
            else:
                # If neither on ground nor can double jump => store jump buffer
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

                # Charged jump press (Space)
                if event.key == pygame.K_SPACE:
                    self.handle_charged_jump_press()

                # Instant jump press (X)
                if event.key == pygame.K_x:
                    self.handle_instant_jump()

            if event.type == pygame.KEYUP:
                # Charged jump release (Space)
                if event.key == pygame.K_SPACE:
                    self.handle_charged_jump_release()

            # Joystick
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # A => charged jump press
                    self.handle_charged_jump_press()
                if event.button == 2:  # X => instant jump
                    self.handle_instant_jump()

            if event.type == pygame.JOYBUTTONUP:
                if event.button == 0:  # releasing A => charged jump release
                    self.handle_charged_jump_release()

    # ------------------------------------------------------------------
    # update_input => continuous charging
    # ------------------------------------------------------------------

    def update_input(self) -> None:
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

    # ------------------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------------------

    def run(self) -> None:
        self.level_manager.coins_spawned = 0
        self.coins_collected = 0
        self.start_ticks = pygame.time.get_ticks()
        
        running = True
        while running:
            self.screen.fill(c.WHITE)
            elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            remaining_time = max(0, c.LEVEL_DURATION - elapsed_time)
            
            # 1) Process events
            self.process_events()

            # 2) Continuous input (charging)
            self.update_input()

            # 3) Update objects
            self.update_objects()
            self.level_manager.spawn_new_platforms(c.WIDTH)

            # 4) Player movement
            self.player.move(self.level_manager.platforms)

            # 5) COYOTE TIME + JUMP BUFFER LOGIC
            #    If on_ground => reset coyote frames, check if we had a jump buffer
            #    If not on_ground => decrement coyote frames
            if self.player.on_ground:
                # CHARGED
                self.set_coyote_ground_frames('charged', c.COYOTE_FRAMES)
                if self.jump_buffer_frames_for('charged') > 0:
                    # user pressed jump in midair, now we landed => do it
                    self.handle_charged_jump_press()
                    self.set_jump_buffer_frames('charged', 0)

                # INSTANT
                self.set_coyote_ground_frames('instant', c.COYOTE_FRAMES)
                if self.jump_buffer_frames_for('instant') > 0:
                    self.handle_instant_jump()
                    self.set_jump_buffer_frames('instant', 0)
            else:
                # decrement coyote frames if in midair
                self.dec_coyote_ground_frames('charged')
                self.dec_coyote_ground_frames('instant')

            # 6) Coin collection
            player_rect = pygame.Rect(self.player.x, self.player.y,
                                      self.player.width, self.player.height)
            for coin in self.level_manager.star_coins[:]:
                if player_rect.colliderect(coin.get_rect()):
                    self.level_manager.star_coins.remove(coin)
                    self.coins_collected += 1
                    self.coin_sound.play()
            
            # 7) Draw
            self.draw_game(remaining_time)

            # 8) Collisions, spikes, time
            if self.level_manager.check_obstacle_collisions(player_rect):
                running = False

            spike_height = int(c.SPIKE_HEIGHT_FRAC * c.HEIGHT)
            if (self.player.y + self.player.height) >= (c.HEIGHT - spike_height):
                running = False

            if remaining_time <= 0:
                running = False

            pygame.display.update()
            self.clock.tick(30)

        # Game Over screen
        over_text = self.font.render("Game Over! Press any key or Y button to restart.", True, c.RED)
        over_rect = over_text.get_rect(center=(c.WIDTH // 2, c.HEIGHT // 2))
        self.screen.blit(over_text, over_rect)
        pygame.display.update()
        
        # Wait for a key or joystick button
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
