# screens.py

import pygame
import sys
import src.config as c

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
                if event.button == 3:  # 'Y'
                    waiting = False

    if game.current_level_index < len(c.LEVELS) - 1:
        c.CURRENT_LEVEL += 1
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
    over_text = game.font.render(
        "No more lives! Press any key or Y to restart from Level 1.",
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

    c.CURRENT_LEVEL = 0
    # reset persistent lives
    from src.game_manager import Game, main
    Game.persistent_lives = 10
    main()

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
            if event.type == pygame.KEYDOWN:
                waiting = False
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 3:
                    waiting = False
