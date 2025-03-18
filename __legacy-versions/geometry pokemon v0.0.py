import pygame
import random

# Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 400
SQUARE_SIZE = 30
GRAVITY = 1
JUMP_STRENGTH = -15
GROUND_HEIGHT = HEIGHT - 50
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 40, 40
SPEED = 5

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Screen Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Pokémon Dash")
clock = pygame.time.Clock()

# Player
class Player:
    def __init__(self):
        self.x = 100
        self.y = GROUND_HEIGHT - SQUARE_SIZE
        self.width = SQUARE_SIZE
        self.height = SQUARE_SIZE
        self.vel_y = 0
        self.is_jumping = False
    
    def jump(self):
        if not self.is_jumping:
            self.vel_y = JUMP_STRENGTH
            self.is_jumping = True

    def move(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y
        if self.y >= GROUND_HEIGHT - self.height:
            self.y = GROUND_HEIGHT - self.height
            self.is_jumping = False

    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))

# Obstacles (Pokémon-like creatures)
# Load Pokémon sprite
POKEMON_IMAGE = pygame.image.load("C:/Users/Daniel Moreira/Desktop/pikachu.png")  # Replace with your file
POKEMON_IMAGE = pygame.transform.scale(POKEMON_IMAGE, (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

class Obstacle:
    def __init__(self):
        self.x = WIDTH
        self.y = GROUND_HEIGHT - OBSTACLE_HEIGHT
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT
        self.speed = SPEED
        self.image = POKEMON_IMAGE  # Assign Pokémon sprite
    
    def move(self):
        self.x -= self.speed
    
    def draw(self):
        screen.blit(self.image, (self.x, self.y))  # Draw Pokémon sprite
    
    def off_screen(self):
        return self.x + self.width < 0

# Game Loop
player = Player()
obstacles = []
running = True
timer = 0

while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
    
    # Spawn obstacles randomly
    if timer % 60 == 0:
        obstacles.append(Obstacle())
    
    # Update & Draw
    player.move()
    player.draw()
    
    for obstacle in obstacles[:]:
        obstacle.move()
        obstacle.draw()
        if obstacle.off_screen():
            obstacles.remove(obstacle)
    
    # Collision Detection
    for obstacle in obstacles:
        if (player.x < obstacle.x + obstacle.width and
            player.x + player.width > obstacle.x and
            player.y < obstacle.y + obstacle.height and
            player.y + player.height > obstacle.y):
            running = False  # Game over
    
    pygame.display.update()
    clock.tick(30)
    timer += 1

pygame.quit()
