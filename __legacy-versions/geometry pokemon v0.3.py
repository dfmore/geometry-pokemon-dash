import pygame
import random

# Initialize Pygame, its mixer, and joystick modules
pygame.init()
pygame.mixer.init()
pygame.joystick.init()

# Check for a connected joystick (using the first one if available)
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("Joystick detected:", joystick.get_name())
else:
    joystick = None
    print("No joystick found.")

# Game Constants
WIDTH, HEIGHT = 800, 400
SQUARE_SIZE = 30
GRAVITY = 1
# Variable jump: define minimum and maximum jump strengths (velocity is negative when jumping)
MIN_JUMP_STRENGTH = 15
MAX_JUMP_STRENGTH = 45
CHARGE_RATE = 1  # Increase in jump strength per frame while button is held
GROUND_HEIGHT = HEIGHT - 50  # (Reference only; the floor is deadly spikes)
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 40, 40
SPEED = 5
PLATFORM_WIDTH = 250  # Platforms are now 250 pixels long
PLATFORM_HEIGHT = 10
SPIKE_HEIGHT = 20

COIN_SIZE = 30  # Star coin dimensions

# Level duration in seconds
LEVEL_DURATION = 100  # 1 minute and 40 seconds

# Colors
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Screen Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Pokémon Dash")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Load Pokémon sprites
POKEMON_IMAGES = [
    pygame.transform.scale(pygame.image.load("C:\\Users\\Daniel Moreira\\Desktop\\pikachu.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT)),
    pygame.transform.scale(pygame.image.load("C:\\Users\\Daniel Moreira\\Desktop\\charmander.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT)),
    pygame.transform.scale(pygame.image.load("C:\\Users\\Daniel Moreira\\Desktop\\bulbasaur.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT)),
    pygame.transform.scale(pygame.image.load("C:\\Users\\Daniel Moreira\\Desktop\\squirtle.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
]

# Load the star coin image and scale it
coin_image = pygame.transform.scale(pygame.image.load("C:\\Users\\Daniel Moreira\\Desktop\\star_coin.gif"), (COIN_SIZE, COIN_SIZE))

# Load the boing sound (using boing.mp3)
boing_sound = pygame.mixer.Sound("C:\\Users\\Daniel Moreira\\Desktop\\boing.mp3")

# Player Class with variable jump charge
class Player:
    def __init__(self):
        # Start on the first platform (x=100, y=320)
        self.x = 100
        self.y = 320
        self.width = SQUARE_SIZE
        self.height = SQUARE_SIZE
        self.vel_y = 0
        self.on_ground = True
        # For variable jump strength:
        self.charging = False
        self.jump_charge = 0

    def move(self, platforms):
        self.vel_y += GRAVITY
        self.y += self.vel_y
        self.on_ground = False

        # Create a rect for collision detection
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for platform in platforms:
            platform_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            # Only check collision if falling
            if self.vel_y > 0 and player_rect.colliderect(platform_rect):
                self.y = platform.y - self.height
                self.vel_y = 0
                self.on_ground = True
                player_rect.y = self.y

    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))

# Platform Class
class Platform:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLATFORM_WIDTH
        self.height = PLATFORM_HEIGHT
        self.speed = SPEED

    def move(self):
        self.x -= self.speed

    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))

    def off_screen(self):
        return self.x + self.width < 0

# Obstacle Class (Pokémon-like creatures)
class Obstacle:
    def __init__(self, platform):
        self.x = platform.x + random.randint(0, platform.width - OBSTACLE_WIDTH)
        self.y = platform.y - OBSTACLE_HEIGHT
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT
        self.speed = SPEED
        self.image = random.choice(POKEMON_IMAGES)

    def move(self):
        self.x -= self.speed

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def off_screen(self):
        return self.x + self.width < 0

# StarCoin Class (collectible coins)
class StarCoin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = COIN_SIZE
        self.height = COIN_SIZE

    def draw(self):
        screen.blit(coin_image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Spikes Class (Deadly floor)
class Spikes:
    def __init__(self):
        self.y = HEIGHT - SPIKE_HEIGHT
        self.height = SPIKE_HEIGHT

    def draw(self):
        pygame.draw.rect(screen, BLACK, (0, self.y, WIDTH, self.height))

# Main game function
def run_game():
    # Platform generation parameters
    safe_gap_min = 50
    safe_gap_max = 140  # maximum horizontal gap (should be less than ~155 pixels)
    vertical_offset_min = -5
    vertical_offset_max = 10
    min_platform_y = 310
    max_platform_y = 340

    # Pre-populate an initial chain of platforms
    platforms = []
    first_platform = Platform(100, 320)  # Platform under the player
    platforms.append(first_platform)
    while platforms[-1].x + platforms[-1].width < WIDTH:
        gap = random.randint(safe_gap_min, safe_gap_max)
        new_x = platforms[-1].x + platforms[-1].width + gap
        new_y = platforms[-1].y + random.randint(vertical_offset_min, vertical_offset_max)
        new_y = max(min_platform_y, min(new_y, max_platform_y))
        platforms.append(Platform(new_x, new_y))
    
    # Star coin variables
    star_coins = []         # List of coins currently in the level
    coins_spawned = 0       # Total coins spawned (max 3 per level)
    coins_collected = 0

    player = Player()
    spikes = Spikes()
    obstacles = []

    # Start the level timer
    start_ticks = pygame.time.get_ticks()

    running = True
    while running:
        screen.fill(WHITE)

        # Calculate elapsed and remaining time
        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000.0
        remaining_time = max(0, LEVEL_DURATION - elapsed_time)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Handle keyboard input for jump charging
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.on_ground:
                    player.charging = True
                    player.jump_charge = MIN_JUMP_STRENGTH
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and player.charging:
                    boing_sound.play()
                    if player.on_ground:
                        player.vel_y = -player.jump_charge
                    player.charging = False
                    player.jump_charge = 0

            # Handle joystick input: assume button 0 (A button) for jump
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    print("Joystick button A pressed")
                    if player.on_ground:
                        player.charging = True
                        player.jump_charge = MIN_JUMP_STRENGTH
            if event.type == pygame.JOYBUTTONUP:
                if event.button == 0:
                    print("Joystick button A released")
                    if player.charging:
                        boing_sound.play()
                        if player.on_ground:
                            player.vel_y = -player.jump_charge
                        player.charging = False
                        player.jump_charge = 0

        # Increase jump charge if button is held (keyboard or joystick)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and player.charging and player.on_ground:
            player.jump_charge += CHARGE_RATE
            if player.jump_charge > MAX_JUMP_STRENGTH:
                player.jump_charge = MAX_JUMP_STRENGTH

        if joystick is not None and joystick.get_button(0) and player.charging and player.on_ground:
            player.jump_charge += CHARGE_RATE
            if player.jump_charge > MAX_JUMP_STRENGTH:
                player.jump_charge = MAX_JUMP_STRENGTH

        # Move platforms and obstacles
        for platform in platforms[:]:
            platform.move()
            if platform.off_screen():
                platforms.remove(platform)
        for obstacle in obstacles[:]:
            obstacle.move()
            if obstacle.off_screen():
                obstacles.remove(obstacle)
        for coin in star_coins[:]:
            # Coins move with platforms; here we simply move them left at the same speed.
            coin.x -= SPEED
            # Remove coin if it goes off screen
            if coin.x + coin.width < 0:
                star_coins.remove(coin)

        # Spawn new platforms until the chain extends past the right edge
        while platforms and platforms[-1].x + platforms[-1].width < WIDTH:
            gap = random.randint(safe_gap_min, safe_gap_max)
            new_x = platforms[-1].x + platforms[-1].width + gap
            new_y = platforms[-1].y + random.randint(vertical_offset_min, vertical_offset_max)
            new_y = max(min_platform_y, min(new_y, max_platform_y))
            new_platform = Platform(new_x, new_y)
            platforms.append(new_platform)
            # With a 30% chance, and if fewer than 3 coins have been spawned, spawn a star coin on this platform.
            if coins_spawned < 3 and random.random() < 0.3:
                # Place the coin above the platform (50 pixels higher)
                coin_x = new_platform.x + random.randint(0, new_platform.width - COIN_SIZE)
                coin_y = new_platform.y - 50
                star_coins.append(StarCoin(coin_x, coin_y))
                coins_spawned += 1
            # Also possibly spawn obstacles
            if random.random() < 0.5:
                for _ in range(random.randint(1, 2)):
                    obstacles.append(Obstacle(new_platform))

        # Update player movement (including collision with platforms)
        player.move(platforms)

        # Check for collisions with star coins
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        for coin in star_coins[:]:
            if player_rect.colliderect(coin.get_rect()):
                star_coins.remove(coin)
                coins_collected += 1

        # Draw game elements
        player.draw()
        spikes.draw()
        for platform in platforms:
            platform.draw()
        for obstacle in obstacles:
            obstacle.draw()
        for coin in star_coins:
            coin.draw()

        # Display timer on top left and coin counter on top right
        timer_text = font.render(f"Time: {int(remaining_time)}", True, BLACK)
        screen.blit(timer_text, (10, 10))
        coin_text = font.render(f"Coins: {coins_collected}", True, BLACK)
        coin_rect = coin_text.get_rect(topright=(WIDTH - 10, 10))
        screen.blit(coin_text, coin_rect)

        # Collision detection with obstacles
        for obstacle in obstacles:
            obstacle_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
            if player_rect.colliderect(obstacle_rect):
                running = False  # Game over

        # Check if the player hits the deadly spikes
        if player.y + player.height >= HEIGHT - SPIKE_HEIGHT:
            running = False  # Game over

        # Check if time is up
        if remaining_time <= 0:
            running = False

        pygame.display.update()
        clock.tick(30)

    # Game Over screen: display message and wait for key or Y button press to restart
    over_text = font.render("Game Over! Press any key or Y button to restart.", True, RED)
    over_rect = over_text.get_rect(center=(WIDTH/2, HEIGHT/2))
    screen.blit(over_text, over_rect)
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            # Restart on any key press
            if event.type == pygame.KEYDOWN:
                waiting = False
            # Restart if joystick Y button is pressed (assumed to be button index 3)
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 3:
                    print("Joystick Y button pressed for restart")
                    waiting = False

# Main loop to restart the game after game over
def main():
    while True:
        run_game()

if __name__ == "__main__":
    main()
