# screens.py
import pygame
import sys
import src.config as c
import src.scoreboard as sb
import src.levels_config as lvl

def show_completion_screen(game):
    ...
    # same as before
    if game.current_level_index < len(lvl.LEVELS) - 1:
        lvl.CURRENT_LEVEL += 1
        from src.game_manager import main
        main()
    else:
        show_final_message(game, "All levels completed! Thanks for playing.")


def show_game_over_screen(game):
    ...
    # same as before
    from src.game_manager import main
    main()


def show_out_of_lives_screen(game):
    """
    Now, we also let the user enter their 3-letter initials
    and store their coin count in the scoreboard.
    """
    # Step 1) Prompt user to input 3 letters
    initials = prompt_for_initials(game)

    # Step 2) Add the user's total coin count to scoreboard
    entries = sb.add_score(initials, game.coins_collected)

    # Step 3) Show scoreboard to user
    show_scoreboard(game, entries)

    # Step 4) Reset back to Level 1, 10 lives
    lvl.CURRENT_LEVEL = 0
    from src.game_manager import Game, main
    Game.persistent_lives = 10

    # Step 5) Finally go to main
    main()

def show_scoreboard(game, entries):
    """
    Display the top 5 scoreboard entries on screen.
    e.g. Rank, Name, Score
    """
    game.screen.fill((0, 0, 0))  # black background for scoreboard
    title_text = game.font.render("TOP SCORES", True, c.WHITE)
    title_rect = title_text.get_rect(center=(c.WIDTH // 2, 50))
    game.screen.blit(title_text, title_rect)

    # Each entry: { "name": "ABC", "score": 42 }
    y_start = 150
    for i, entry in enumerate(entries):
        rank = i + 1
        line = f"{rank}. {entry['name']}  -  {entry['score']} coins"
        line_surf = game.font.render(line, True, c.WHITE)
        game.screen.blit(line_surf, (100, y_start + i * 40))

    pygame.display.update()

    # Wait for user to press a key
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                waiting = False

def show_final_message(game, msg):
    ...
    # same as before

def prompt_for_initials(game):
    """
    Arcade-style: user can input 3 letters (A-Z).
    We'll ignore numeric or special chars and only store letters.
    If user hits backspace, we remove last char.
    Once 3 letters are input, we auto-confirm or wait for ENTER.
    """
    entered = ""
    while True:
        game.screen.fill((0, 0, 0))
        prompt = game.font.render("Enter your initials (3 letters):", True, c.WHITE)
        prompt_rect = prompt.get_rect(center=(c.WIDTH // 2, 150))
        game.screen.blit(prompt, prompt_rect)

        initials_surf = game.font.render(entered, True, c.WHITE)
        initials_rect = initials_surf.get_rect(center=(c.WIDTH // 2, 250))
        game.screen.blit(initials_surf, initials_rect)

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
                    if len(entered) > 0:
                        return finalize_initials(entered)
                else:
                    # Convert the key to uppercase letter if it's A-Z
                    char = event.unicode
                    if char.isalpha():
                        char = char.upper()
                        if len(entered) < 3:
                            entered += char
                        # If we automatically want to finish after 3 chars:
                        if len(entered) == 3:
                            return finalize_initials(entered)

def finalize_initials(letters):
    """ Pad or trim to exactly 3 uppercase letters. """
    letters = letters.upper()
    if len(letters) < 3:
        letters += "AAA"  # or something
    return letters[:3]
