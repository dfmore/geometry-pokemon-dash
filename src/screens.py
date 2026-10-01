# screens.py
#
# End-of-level / end-of-game screens. These never start the next attempt
# themselves: Game.run() returns after calling them and the outer loop in
# the game module starts the next attempt. Do not import that module here.

import pygame
import sys

import src.config as c
import src.levels_config as lvl
import src.scoreboard as sb

_INPUT_EVENTS = [pygame.KEYDOWN, pygame.KEYUP,
                 pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]

def _quit():
    pygame.quit()
    sys.exit()

def _draw_centered(game, text, y, color, font=None):
    surf = (font or game.font).render(text, True, color)
    game.screen.blit(surf, surf.get_rect(center=(c.WIDTH // 2, y)))

def _small_font(game):
    try:
        return pygame.font.Font(None, max(18, int(game.font.get_height() * 0.8)))
    except pygame.error:
        return game.font

def _draw_esc_hint(game, y):
    _draw_centered(game, "ESC to quit", y, (200, 200, 200), _small_font(game))

def wait_for_continue(game, min_delay_ms=500):
    """
    Block until any key or joystick button is pressed. Presses during the first
    min_delay_ms are ignored so a held jump key cannot skip the screen.
    ESC or closing the window quits.
    """
    # Drop stale input only; keep JOYDEVICEADDED/REMOVED for hot-plug.
    pygame.event.clear(eventtype=_INPUT_EVENTS)
    start = pygame.time.get_ticks()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                _quit()
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                if pygame.time.get_ticks() - start >= min_delay_ms:
                    return
        game.clock.tick(c.FPS)

def show_completion_screen(game):
    if game.current_level_index < len(lvl.LEVELS) - 1:
        _draw_centered(game, f"Level {game.current_level_index + 1} Complete!",
                       c.HEIGHT // 2 - 20, c.RED)
        _draw_centered(game, "Press any key or button to continue", c.HEIGHT // 2 + 20, c.RED)
        _draw_esc_hint(game, c.HEIGHT // 2 + 55)
        pygame.display.update()
        wait_for_continue(game)
        lvl.CURRENT_LEVEL += 1
        return

    show_final_message(game, "All levels completed! Thanks for playing.")
    initials = prompt_for_initials(game)
    entries = sb.add_score(initials, game.baseline_coins)
    show_scoreboard(game, entries)

    lvl.CURRENT_LEVEL = 0
    type(game).persistent_lives = 10
    type(game).persistent_baseline_coins = 0

def show_game_over_screen(game):
    """
    Called when the player dies but still has lives left => retry same level.
    """
    _draw_centered(game, "Game Over!", c.HEIGHT // 2 - 20, c.RED)
    _draw_centered(game, f"Press any key or button to retry level {game.current_level_index + 1}",
                   c.HEIGHT // 2 + 20, c.RED)
    _draw_esc_hint(game, c.HEIGHT // 2 + 55)
    pygame.display.update()
    wait_for_continue(game)

def show_out_of_lives_screen(game):
    """
    Called when the player has 0 lives left => prompt for initials,
    store scoreboard with baseline_coins plus partial coins from final attempt,
    then reset to level 1 with 10 lives.
    """
    final_coins = getattr(game, 'final_coins_for_scoreboard', game.baseline_coins)

    initials = prompt_for_initials(game)
    entries = sb.add_score(initials, final_coins)
    show_scoreboard(game, entries)

    lvl.CURRENT_LEVEL = 0
    type(game).persistent_lives = 10
    type(game).persistent_baseline_coins = 0

def prompt_for_initials(game):
    """
    Wait for up to 3 letters (A-Z). Press Enter to confirm.
    Any gamepad button confirms after a short grace period.
    """
    entered = ""
    # Drop stale input only; keep JOYDEVICEADDED/REMOVED for hot-plug.
    pygame.event.clear(eventtype=_INPUT_EVENTS)
    start = pygame.time.get_ticks()
    while True:
        game.screen.fill((0, 0, 0))
        _draw_centered(game, "Enter your initials (up to 3 letters), then press Enter:",
                       int(c.HEIGHT * 0.3), c.WHITE)
        _draw_centered(game, entered, int(c.HEIGHT * 0.45), c.WHITE)
        _draw_centered(game, "[Backspace=delete | Enter or gamepad button=confirm | ESC=quit]",
                       int(c.HEIGHT * 0.6), (200, 200, 200))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _quit()

            if event.type == pygame.JOYBUTTONDOWN:
                if pygame.time.get_ticks() - start >= 500:
                    return finalize_initials(entered) if entered else "AAA"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    _quit()

                elif event.key == pygame.K_BACKSPACE:
                    if len(entered) > 0:
                        entered = entered[:-1]

                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if len(entered) == 0:
                        return "AAA"
                    else:
                        return finalize_initials(entered)
                else:
                    char = event.unicode
                    if char and char.isascii() and char.isalpha():
                        if len(entered) < 3:
                            entered += char.upper()
        game.clock.tick(c.FPS)

def finalize_initials(letters):
    letters = letters.upper()
    if len(letters) < 3:
        letters += "AAA"
    return letters[:3]

def show_scoreboard(game, entries):
    """
    Display the top scoreboard entries on screen.
    """
    game.screen.fill((0, 0, 0))
    _draw_centered(game, "TOP SCORES", 50, c.WHITE)

    y_start = 110
    line_height = 32
    max_rows = max(1, (c.HEIGHT - 110 - 60) // line_height)
    for i, entry in enumerate(entries[:max_rows]):
        name = str(entry.get('name', '???'))
        score = entry.get('score', 0)
        _draw_centered(game, f"{i + 1}. {name}  -  {score} coins",
                       y_start + i * line_height, c.WHITE)

    _draw_centered(game, "Press any key or button to continue  |  ESC to quit",
                   c.HEIGHT - 30, (200, 200, 200), _small_font(game))
    pygame.display.update()
    wait_for_continue(game)

def show_final_message(game, msg):
    """
    Called after all levels completed.
    """
    _draw_centered(game, msg, c.HEIGHT // 2, c.RED)
    _draw_centered(game, "Press any key or button to continue", c.HEIGHT // 2 + 40, c.RED)
    _draw_esc_hint(game, c.HEIGHT // 2 + 75)
    pygame.display.update()
    wait_for_continue(game)
