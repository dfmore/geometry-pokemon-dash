import pygame
import random

# Initialize Pygame and the mixer for sound effects
pygame.init()
pygame.mixer.init()

# Game Constants
WIDTH, HEIGHT = 800, 400
SQUARE_SIZE = 30
GRAVITY = 1
# Variable jump: minimum and maximum jump strengths (the velocity will be negative)
MIN_JUMP_STRENGTH = 15
MAX_JUMP_STRENGTH = 40
CHARGE_RATE = 1  # Amount by which jump strength increases per frame while holding space
GROUND_HEIGHT = HEIGHT - 50  # (Reference only; the floor is deadly spikes)
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 40, 40
SPEED = 5
PLATFORM_WIDTH = 250
PLATFORM_HEIGHT = 10
SPIKE_HEIGHT = 20

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

# Load Pokémon sprites
POKEMON_IMAGES = [
    pygame.transform.scale(pygame.image.load("C:\\Users\\Daniel Moreira\\Desktop\\pikachu.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT)),
    pygame.transform.scale(pygame.image.load("C:\\Users\\Daniel Moreira\\Desktop\\charmander.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT)),
    pygame.transform.scale(pygame.image.load("C:\\Users\\Daniel Moreira\\Desktop\\bulbasaur.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT)),
    pygame.transform.scale(pygame.image.load("C:\\Users\\Daniel Moreira\\Desktop\\squirtle.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
]

# Load the boing sound (make sure the file exists at this path)
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

        # Check collision with platforms
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

# Spikes Class (Deadly floor)
class Spikes:
    def __init__(self):
        self.y = HEIGHT - SPIKE_HEIGHT
        self.height = SPIKE_HEIGHT

    def draw(self):
        pygame.draw.rect(screen, BLACK, (0, self.y, WIDTH, self.height))

# Main game function
def run_game():
    # Parameters for platform generation relative to physics settings:
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
    
    player = Player()
    spikes = Spikes()
    obstacles = []

    running = True
    while running:
        screen.fill(WHITE)
        
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Start charging jump when space is pressed down if on ground.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.on_ground:
                    player.charging = True
                    player.jump_charge = MIN_JUMP_STRENGTH

            # On release, perform the jump and play the boing sound.
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and player.charging:
                    # Play the boing sound
                    boing_sound.play()
                    if player.on_ground:
                        player.vel_y = -player.jump_charge
                    player.charging = False
                    player.jump_charge = 0

        # If space is held down and the player is on the ground, increase the jump charge.
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and player.charging and player.on_ground:
            player.jump_charge += CHARGE_RATE
            if player.jump_charge > MAX_JUMP_STRENGTH:
                player.jump_charge = MAX_JUMP_STRENGTH

        # Move existing platforms and obstacles
        for platform in platforms[:]:
            platform.move()
            if platform.off_screen():
                platforms.remove(platform)
        for obstacle in obstacles[:]:
            obstacle.move()
            if obstacle.off_screen():
                obstacles.remove(obstacle)

        # Spawn new platforms until the chain extends past the right edge.
        while platforms and platforms[-1].x + platforms[-1].width < WIDTH:
            gap = random.randint(safe_gap_min, safe_gap_max)
            new_x = platforms[-1].x + platforms[-1].width + gap
            new_y = platforms[-1].y + random.randint(vertical_offset_min, vertical_offset_max)
            new_y = max(min_platform_y, min(new_y, max_platform_y))
            new_platform = Platform(new_x, new_y)
            platforms.append(new_platform)
            if random.random() < 0.5:
                for _ in range(random.randint(1, 2)):
                    obstacles.append(Obstacle(new_platform))
        
        # Update player movement (including collision detection)
        player.move(platforms)

        # Draw all game elements
        player.draw()
        spikes.draw()
        for platform in platforms:
            platform.draw()
        for obstacle in obstacles:
            obstacle.draw()

        # Check collision with obstacles
        for obstacle in obstacles:
            if (player.x < obstacle.x + obstacle.width and
                player.x + player.width > obstacle.x and
                player.y < obstacle.y + obstacle.height and
                player.y + player.height > obstacle.y):
                running = False  # Game over

        # Check if the player hits the deadly spikes
        if player.y + player.height >= HEIGHT - SPIKE_HEIGHT:
            running = False  # Game over

        pygame.display.update()
        clock.tick(30)

    # Game Over screen: display message and wait for any key press to restart.
    font = pygame.font.Font(None, 36)
    text = font.render("Game Over! Press any key to restart.", True, RED)
    text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
    screen.blit(text, text_rect)
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

# Main loop to restart the game after game over
def main():
    while True:
        run_game()

if __name__ == "__main__":
    main()
