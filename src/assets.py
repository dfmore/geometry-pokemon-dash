# assets.py
import pygame
import src.config as c

def load_assets():
    assets = {}

    # Helper function: scale while preserving aspect ratio
    def scale_preserving_ratio(original_surf, new_width):
        orig_w, orig_h = original_surf.get_size()
        aspect = orig_h / float(orig_w)
        new_height = int(new_width * aspect)
        return pygame.transform.scale(original_surf, (new_width, new_height))

    # Load original Pokémon images
    pikachu_original = pygame.image.load("assets/pikachu.png").convert_alpha()
    charmander_original = pygame.image.load("assets/charmander.png").convert_alpha()
    bulbasaur_original = pygame.image.load("assets/bulbasaur.png").convert_alpha()
    squirtle_original = pygame.image.load("assets/squirtle.png").convert_alpha()

    # Desired obstacle width in pixels
    obstacle_desired_w = int(c.OBSTACLE_WIDTH_FRAC * c.WIDTH)

    # Scale each sprite
    assets['pokemon_images'] = [
        scale_preserving_ratio(pikachu_original, obstacle_desired_w),
        scale_preserving_ratio(charmander_original, obstacle_desired_w),
        scale_preserving_ratio(bulbasaur_original, obstacle_desired_w),
        scale_preserving_ratio(squirtle_original, obstacle_desired_w)
    ]

    # Coin
    coin_original = pygame.image.load("assets/star_coin.gif").convert_alpha()
    coin_desired_w = int(c.COIN_WIDTH_FRAC * c.WIDTH)
    assets['coin_image'] = scale_preserving_ratio(coin_original, coin_desired_w)

    # Load sounds
    assets['boing_sound'] = pygame.mixer.Sound("assets/boing.mp3")
    assets['coin_sound'] = pygame.mixer.Sound("assets/coin.mp3")

    return assets
