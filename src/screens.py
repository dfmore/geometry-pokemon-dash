# screens.py

import pygame
import sys

import src.config as c
import src.levels_config as lvl
import src.scoreboard as sb

def show_completion_screen(game):
    over_text = game.font.render(
        f"Level {game.current_level_index + 1} Complete! Press any key or Y to continue.",
        True, c.RED
    )
    over_rect = over_text.get_rect(center=(c.WIDTH // 2, c.HEIGHT // 2))
    game.screen.blit(over_text, over_rect)
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 3:  # 'Y' button
                    waiting = False

    # Move to next level or end
    if game.current_level_index < len(lvl.LEVELS) - 1:
        lvl.CURRENT_LEVEL += 1
        from src.game_manager import main
        main()
    else:
        show_final_message(game, "All levels completed! Thanks for playing.")

def show_game_over_screen(game):
    over_text = game.font.render(
        f"Game Over! Press any key or Y to retry level {game.current_level_index + 1}",
        True, c.RED
    )
    over_rect = over_text.get_rect(center=(c.WIDTH // 2, c.HEIGHT // 2))
    game.screen.blit(over_text, over_rect)
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 3:
                    waiting = False

    from src.game_manager import main
    main()

def show_out_of_lives_screen(game):
    initials = prompt_for_initials(game)
    final_coins = game.baseline_coins

    entries = sb.add_score(initials, final_coins)
    show_scoreboard(game, entries)

    lvl.CURRENT_LEVEL = 0
    from src.game_manager import Game, main
    Game.persistent_lives = 10
    main()

def prompt_for_initials(game):
    entered = ""
    while True:
        game.screen.fill((0, 0, 0))
        prompt = game.font.render("Enter your initials (up to 3 letters), then Press Enter:", True, c.WHITE)
        prompt_rect = prompt.get_rect(center=(c.WIDTH // 2, 150))
        game.screen.blit(prompt, prompt_rect)

        initials_surf = game.font.render(entered, True, c.WHITE)
        initials_rect = initials_surf.get_rect(center=(c.WIDTH // 2, 250))
        game.screen.blit(initials_surf, initials_rect)

        instructions = game.font.render("[Backspace=delete | Enter=confirm]", True, (200,200,200))
        instructions_rect = instructions.get_rect(center=(c.WIDTH // 2, 350))
        game.screen.blit(instructions, instructions_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                elif event.key == pygame.K_BACKSPACE:
                    if len(entered) > 0:
                        entered = entered[:-1]

                elif event.key == pygame.K_RETURN:
                    if len(entered) == 0:
                        return "AAA"
                    else:
                        return finalize_initials(entered)
                else:
                    char = event.unicode
                    if char.isalpha():
                        char = char.upper()
                        if len(entered) < 3:
                            entered += char

def finalize_initials(letters):
    letters = letters.upper()
    if len(letters) < 3:
        letters += "AAA"
    return letters[:3]

def show_scoreboard(game, entries):
    game.screen.fill((0, 0, 0))
    title_text = game.font.render("TOP SCORES", True, c.WHITE)
    title_rect = title_text.get_rect(center=(c.WIDTH // 2, 50))
    game.screen.blit(title_text, title_rect)

    y_start = 150
    for i, entry in enumerate(entries):
        rank = i + 1
        line = f"{rank}. {entry['name']}  -  {entry['score']} coins"
        line_surf = game.font.render(line, True, c.WHITE)
        game.screen.blit(line_surf, (100, y_start + i * 40))

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                waiting = False

def show_final_message(game, msg):
    over_text = game.font.render(msg, True, c.RED)
    over_rect = over_text.get_rect(center=(c.WIDTH // 2, c.HEIGHT // 2))
    game.screen.blit(over_text, over_rect)
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                waiting = False
