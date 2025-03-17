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
# Variable jump strengths (velocity is negative when jumping)
MIN_JUMP_STRENGTH = 15
MAX_JUMP_STRENGTH = 45  # Maximum jump strength
CHARGE_RATE = 1        # Increase per frame while charging
GROUND_HEIGHT = HEIGHT - 50  # Reference (the floor is deadly spikes)
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 40, 40
SPEED = 5
PLATFORM_WIDTH = 250   # Platforms are 250 pixels long
PLATFORM_HEIGHT = 10
SPIKE_HEIGHT = 20

COIN_SIZE = 30         # Star coin dimensions

# Level duration in seconds (1 minute 40 seconds = 100 seconds)
LEVEL_DURATION = 100

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

# Load Pokémon sprites (including squirtle.png)
POKEMON_IMAGES = [
    pygame.transform.scale(pygame.image.load("C:\\Users\\Daniel Moreira\\Desktop\\pikachu.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT)),
    pygame.transform.scale(pygame.image.load("C:\\Users\\Daniel Moreira\\Desktop\\charmander.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT)),
    pygame.transform.scale(pygame.image.load("C:\\Users\\Daniel Moreira\\Desktop\\bulbasaur.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT)),
    pygame.transform.scale(pygame.image.load("C:\\Users\\Daniel Moreira\\Desktop\\squirtle.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
]

# Load the star coin image and scale it (now using star_coin.gif)
coin_image = pygame.transform.scale(pygame.image.load("C:\\Users\\Daniel Moreira\\Desktop\\star_coin.gif"), (COIN_SIZE, COIN_SIZE))

# Load the boing sound (using boing.mp3)
boing_sound = pygame.mixer.Sound("C:\\Users\\Daniel Moreira\\Desktop\\boing.mp3")

# Player Class with variable jump charge and double jump capability
class Player:
    def __init__(self):
        self.x = 100
        self.y = 320
        self.width = SQUARE_SIZE
        self.height = SQUARE_SIZE
        self.vel_y = 0
        self.on_ground = True
        self.charging = False
        self.jump_charge = 0
        self.can_double_jump = True  # Reset when landing

    def move(self, platforms):
        self.vel_y += GRAVITY
        self.y += self.vel_y
        self.on_ground = False
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for platform in platforms:
            platform_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            if self.vel_y > 0 and player_rect.colliderect(platform_rect):
                self.y = platform.y - self.height
                self.vel_y = 0
                self.on_ground = True
                self.can_double_jump = True  # Reset double jump on landing
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
    safe_gap_min = 50
    safe_gap_max = 140
    vertical_offset_min = -5
    vertical_offset_max = 10
    min_platform_y = 310
    max_platform_y = 340

    platforms = []
    first_platform = Platform(100, 320)
    platforms.append(first_platform)
    while platforms[-1].x + platforms[-1].width < WIDTH:
        gap = random.randint(safe_gap_min, safe_gap_max)
        new_x = platforms[-1].x + platforms[-1].width + gap
        new_y = platforms[-1].y + random.randint(vertical_offset_min, vertical_offset_max)
        new_y = max(min_platform_y, min(new_y, max_platform_y))
        platforms.append(Platform(new_x, new_y))
    
    star_coins = []
    coins_spawned = 0
    coins_collected = 0

    player = Player()
    spikes = Spikes()
    obstacles = []

    start_ticks = pygame.time.get_ticks()

    running = True
    while running:
        screen.fill(WHITE)
        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000.0
        remaining_time = max(0, LEVEL_DURATION - elapsed_time)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            # Keyboard input:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if player.on_ground:
                        player.charging = True
                        player.jump_charge = MIN_JUMP_STRENGTH
                if event.key == pygame.K_x and (not player.on_ground) and player.can_double_jump:
                    boing_sound.play()
                    player.vel_y = -MIN_JUMP_STRENGTH
                    player.can_double_jump = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and player.charging:
                    boing_sound.play()
                    if player.on_ground:
                        player.vel_y = -player.jump_charge
                    player.charging = False
                    player.jump_charge = 0

            # Joystick input:
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    print("Joystick button A pressed")
                    if player.on_ground:
                        player.charging = True
                        player.jump_charge = MIN_JUMP_STRENGTH
                if event.button == 2 and (not player.on_ground) and player.can_double_jump:
                    print("Joystick button X pressed for double jump")
                    boing_sound.play()
                    player.vel_y = -MIN_JUMP_STRENGTH
                    player.can_double_jump = False
            if event.type == pygame.JOYBUTTONUP:
                if event.button == 0 and player.charging:
                    print("Joystick button A released")
                    boing_sound.play()
                    if player.on_ground:
                        player.vel_y = -player.jump_charge
                    player.charging = False
                    player.jump_charge = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and player.charging and player.on_ground:
            player.jump_charge += CHARGE_RATE
            if player.jump_charge > MAX_JUMP_STRENGTH:
                player.jump_charge = MAX_JUMP_STRENGTH
        if joystick is not None and joystick.get_button(0) and player.charging and player.on_ground:
            player.jump_charge += CHARGE_RATE
            if player.jump_charge > MAX_JUMP_STRENGTH:
                player.jump_charge = MAX_JUMP_STRENGTH

        for platform in platforms[:]:
            platform.move()
            if platform.off_screen():
                platforms.remove(platform)
        for obstacle in obstacles[:]:
            obstacle.move()
            if obstacle.off_screen():
                obstacles.remove(obstacle)
        for coin in star_coins[:]:
            coin.x -= SPEED
            if coin.x + coin.width < 0:
                star_coins.remove(coin)

        while platforms and platforms[-1].x + platforms[-1].width < WIDTH:
            gap = random.randint(safe_gap_min, safe_gap_max)
            new_x = platforms[-1].x + platforms[-1].width + gap
            new_y = platforms[-1].y + random.randint(vertical_offset_min, vertical_offset_max)
            new_y = max(min_platform_y, min(new_y, max_platform_y))
            new_platform = Platform(new_x, new_y)
            platforms.append(new_platform)
            # Spawn obstacles on this platform ensuring they are at least 150 pixels apart.
            if random.random() < 0.5:
                num_obs = random.randint(1, 2)
                obs_positions = []
                for i in range(num_obs):
                    attempts = 0
                    candidate = None
                    while attempts < 10:
                        candidate = new_platform.x + random.randint(0, new_platform.width - OBSTACLE_WIDTH)
                        valid = True
                        for pos in obs_positions:
                            if abs(candidate - pos) < 150:
                                valid = False
                                break
                        if valid:
                            obs_positions.append(candidate)
                            break
                        attempts += 1
                for pos in obs_positions:
                    obs = Obstacle(new_platform)
                    obs.x = pos
                    obstacles.append(obs)
            # Spawn a coin if possible, ensuring it's at least 100 pixels away from obstacles on this platform.
            if coins_spawned < 3 and random.random() < 0.3:
                placed = False
                attempts = 0
                while not placed and attempts < 5:
                    coin_x = new_platform.x + random.randint(0, new_platform.width - COIN_SIZE)
                    coin_y = new_platform.y - 50
                    coin_rect = pygame.Rect(coin_x, coin_y, COIN_SIZE, COIN_SIZE)
                    safe = True
                    for obstacle in obstacles:
                        if new_platform.x <= obstacle.x <= new_platform.x + new_platform.width:
                            obs_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
                            if coin_rect.colliderect(obs_rect.inflate(200, 200)):
                                safe = False
                                break
                    if safe:
                        star_coins.append(StarCoin(coin_x, coin_y))
                        coins_spawned += 1
                        placed = True
                    attempts += 1
        
        player.move(platforms)

        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        for coin in star_coins[:]:
            if player_rect.colliderect(coin.get_rect()):
                star_coins.remove(coin)
                coins_collected += 1

        player.draw()
        spikes.draw()
        for platform in platforms:
            platform.draw()
        for obstacle in obstacles:
            obstacle.draw()
        for coin in star_coins:
            coin.draw()

        timer_text = font.render(f"Time: {int(remaining_time)}", True, BLACK)
        screen.blit(timer_text, (10, 10))
        coin_text = font.render(f"Coins: {coins_collected}", True, BLACK)
        coin_rect_disp = coin_text.get_rect(topright=(WIDTH - 10, 10))
        screen.blit(coin_text, coin_rect_disp)

        for obstacle in obstacles:
            obstacle_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
            if player_rect.colliderect(obstacle_rect):
                running = False

        if player.y + player.height >= HEIGHT - SPIKE_HEIGHT:
            running = False

        if remaining_time <= 0:
            running = False

        pygame.display.update()
        clock.tick(30)

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
            if event.type == pygame.KEYDOWN:
                waiting = False
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 3:
                    print("Joystick Y button pressed for restart")
                    waiting = False

def main():
    while True:
        run_game()

if __name__ == "__main__":
    main()
