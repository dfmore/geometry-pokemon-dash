# ui.py

import pygame
import src.config as c
import src.levels_config as lvl

def draw_black_bar_behind_spikes(game):
    spike_height = int(c.SPIKE_HEIGHT_FRAC * c.HEIGHT)
    black_bar_top = c.HEIGHT - spike_height - c.SPIKE_BG_OVERLAP
    black_bar_height = spike_height + c.SPIKE_BG_OVERLAP
    if black_bar_top < 0:
        black_bar_top = 0
        black_bar_height = c.HEIGHT

    pygame.draw.rect(
        game.screen,
        c.SPIKE_BG_COLOR,
        (0, black_bar_top, c.WIDTH, black_bar_height)
    )

def draw_powerup_bar(game):
    bar_max_height = c.HEIGHT / 6 * c.POWER_BAR_SCALE
    bar_width = 30

    # The bottom share is green (normal jump) and fills during the tap
    # window; past it the bar turns red and fills up to the maximum charge.
    player = game.player
    green_frac = c.NORMAL_JUMP_BAR_FRAC
    if not player.charging:
        fraction = 0
    elif player.charge_frames <= c.POWER_HOLD_FRAMES:
        fraction = green_frac * player.charge_frames / c.POWER_HOLD_FRAMES
    else:
        power = ((player.jump_charge - c.MIN_JUMP_STRENGTH)
                 / (c.MAX_JUMP_STRENGTH - c.MIN_JUMP_STRENGTH))
        fraction = green_frac + (1 - green_frac) * power
    fraction = max(0, min(fraction, 1))

    fill_height = bar_max_height * fraction
    green_height = min(fill_height, bar_max_height * green_frac)
    bar_x = c.WIDTH - bar_width - 10
    bar_y = c.HEIGHT - 10 - bar_max_height

    # Outline
    pygame.draw.rect(game.screen, (0, 0, 0),
                     (bar_x, bar_y, bar_width, bar_max_height), 2)
    # Fill
    fill_rect = (bar_x, bar_y + (bar_max_height - fill_height), bar_width, fill_height)
    pygame.draw.rect(game.screen, (255, 0, 0), fill_rect)
    green_rect = (bar_x, bar_y + (bar_max_height - green_height), bar_width, green_height)
    pygame.draw.rect(game.screen, (0, 200, 0), green_rect)

def draw_hud_text(game, remaining_time):
    # Timer
    timer_text = game.font.render(f"Time: {int(remaining_time)}", True, c.BLACK)
    game.screen.blit(timer_text, (10, 10))

    # Combine baseline_coins + current_level_coins for display
    total_coins = game.baseline_coins + game.current_level_coins

    coin_text = game.font.render(f"Coins: {total_coins}", True, c.BLACK)
    coin_rect_disp = coin_text.get_rect(topright=(c.WIDTH - 10, 10))
    game.screen.blit(coin_text, coin_rect_disp)

    # Show level out of total
    level_text = game.font.render(
        f"Level: {game.current_level_index + 1} / {len(lvl.LEVELS)}",
        True, c.BLACK
    )
    level_rect = level_text.get_rect(center=(c.WIDTH // 2, 20))
    game.screen.blit(level_text, level_rect)

    # Lives
    lives_text = game.font.render(f"Lives: {game.lives}", True, c.BLACK)
    game.screen.blit(lives_text, (10, 50))
