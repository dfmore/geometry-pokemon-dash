# assets.py
import pygame
import src.config as c

_ASSET_CACHE = {}


class _SilentSound:
    """Stand-in used when audio is unavailable."""
    def play(self, *a, **k):
        return None


def _load_sound(name):
    if not pygame.mixer.get_init():
        return _SilentSound()
    try:
        return pygame.mixer.Sound(c.asset_path(name))
    except (pygame.error, FileNotFoundError):
        return _SilentSound()


def load_assets():
    if _ASSET_CACHE:
        return _ASSET_CACHE

    assets = {}

    def scale_preserving_ratio(original_surf, new_width):
        orig_w, orig_h = original_surf.get_size()
        aspect = orig_h / float(orig_w)
        new_height = int(new_width * aspect)
        return pygame.transform.scale(original_surf, (new_width, new_height))

    pikachu_original = pygame.image.load(c.asset_path("pikachu.png")).convert_alpha()
    charmander_original = pygame.image.load(c.asset_path("charmander.png")).convert_alpha()
    bulbasaur_original = pygame.image.load(c.asset_path("bulbasaur.png")).convert_alpha()
    squirtle_original = pygame.image.load(c.asset_path("squirtle.png")).convert_alpha()

    obstacle_desired_w = int(c.OBSTACLE_WIDTH_FRAC * c.WIDTH)
    assets['pokemon_images'] = [
        scale_preserving_ratio(pikachu_original, obstacle_desired_w),
        scale_preserving_ratio(charmander_original, obstacle_desired_w),
        scale_preserving_ratio(bulbasaur_original, obstacle_desired_w),
        scale_preserving_ratio(squirtle_original, obstacle_desired_w)
    ]

    coin_original = pygame.image.load(c.asset_path("star_coin.gif")).convert_alpha()
    coin_desired_w = int(c.COIN_WIDTH_FRAC * c.WIDTH)
    assets['coin_image'] = scale_preserving_ratio(coin_original, coin_desired_w)

    assets['boing_sound'] = _load_sound("boing.mp3")
    assets['coin_sound'] = _load_sound("coin.mp3")

    _ASSET_CACHE.update(assets)
    return _ASSET_CACHE
