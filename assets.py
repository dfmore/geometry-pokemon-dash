# assets.py
import pygame
from config import OBSTACLE_WIDTH, OBSTACLE_HEIGHT, COIN_SIZE

def load_assets():
    assets = {}
    # Load Pokémon sprites
    assets['pokemon_images'] = [
        pygame.transform.scale(pygame.image.load("assets/pikachu.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT)),
        pygame.transform.scale(pygame.image.load("assets/charmander.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT)),
        pygame.transform.scale(pygame.image.load("assets/bulbasaur.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT)),
        pygame.transform.scale(pygame.image.load("assets/squirtle.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
    ]
    # Load coin image (using star_coin.gif)
    assets['coin_image'] = pygame.transform.scale(pygame.image.load("assets/star_coin.gif"), (COIN_SIZE, COIN_SIZE))
    # Load sound
    assets['boing_sound'] = pygame.mixer.Sound("assets/boing.mp3")
    return assets
