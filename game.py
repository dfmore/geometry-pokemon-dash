import pygame, random
from config import WIDTH, HEIGHT, WHITE, RED, BLUE, GREEN, BLACK, LEVEL_DURATION, SQUARE_SIZE, GRAVITY, CHARGE_RATE, MIN_JUMP_STRENGTH, MAX_JUMP_STRENGTH, OBSTACLE_WIDTH, OBSTACLE_HEIGHT, SPEED, PLATFORM_WIDTH, PLATFORM_HEIGHT, SPIKE_HEIGHT, COIN_SIZE
from assets import load_assets
from player import Player
from game_platform import Platform
from obstacle import Obstacle
from coin import StarCoin
from spikes import Spikes

# Cache the joystick instance if available
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
else:
    joystick = None

def run_game():
    assets = load_assets()
    pokemon_images = assets['pokemon_images']
    coin_image = assets['coin_image']
    boing_sound = assets['boing_sound']
    
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    # Pre-generate initial platforms
    platforms = []
    first_platform = Platform(100, 320)
    platforms.append(first_platform)
    safe_gap_min = 50
    safe_gap_max = 140
    vertical_offset_min = -5
    vertical_offset_max = 10
    min_platform_y = 310
    max_platform_y = 340
    while platforms[-1].x + platforms[-1].width < WIDTH:
        gap = random.randint(safe_gap_min, safe_gap_max)
        new_x = platforms[-1].x + platforms[-1].width + gap
        new_y = platforms[-1].y + random.randint(vertical_offset_min, vertical_offset_max)
        new_y = max(min_platform_y, min(new_y, max_platform_y))
        platforms.append(Platform(new_x, new_y))
    
    star_coins = []
    coins_spawned = 0
    coins_collected = 0
    obstacles = []
    
    player = Player()
    spikes = Spikes()
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
                # X key now always triggers an immediate jump with minimum strength
                if event.key == pygame.K_x:
                    boing_sound.play()
                    if player.on_ground:
                        player.vel_y = -MIN_JUMP_STRENGTH
                    elif not player.on_ground and player.can_double_jump:
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
                # A button (button 0) for variable jump charging
                if event.button == 0:
                    if player.on_ground:
                        player.charging = True
                        player.jump_charge = MIN_JUMP_STRENGTH
                # X button (button 2) now always triggers an immediate jump with minimum strength
                if event.button == 2:
                    boing_sound.play()
                    if player.on_ground:
                        player.vel_y = -MIN_JUMP_STRENGTH
                    elif not player.on_ground and player.can_double_jump:
                        player.vel_y = -MIN_JUMP_STRENGTH
                        player.can_double_jump = False
            if event.type == pygame.JOYBUTTONUP:
                if event.button == 0 and player.charging:
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
                    obs = Obstacle(new_platform, pokemon_images)
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
                        star_coins.append(StarCoin(coin_x, coin_y, coin_image))
                        coins_spawned += 1
                        placed = True
                    attempts += 1
        
        player.move(platforms)
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        for coin in star_coins[:]:
            if player_rect.colliderect(coin.get_rect()):
                star_coins.remove(coin)
                coins_collected += 1
        
        player.draw(screen)
        spikes.draw(screen)
        for platform in platforms:
            platform.draw(screen)
        for obstacle in obstacles:
            obstacle.draw(screen)
        for coin in star_coins:
            coin.draw(screen)
        
        timer_text = font.render(f"Time: {int(remaining_time)}", True, BLACK)
        screen.blit(timer_text, (10, 10))
        coin_text = font.render(f"Coins: {coins_collected}", True, BLACK)
        coin_rect_disp = coin_text.get_rect(topright=(WIDTH - 10, 10))
        screen.blit(coin_text, coin_rect_disp)
        
        for obstacle in obstacles:
            obs_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
            if player_rect.colliderect(obs_rect):
                running = False
        if player.y + player.height >= HEIGHT - SPIKE_HEIGHT:
            running = False
        if remaining_time <= 0:
            running = False
        
        pygame.display.update()
        clock.tick(30)
    
    over_text = font.render("Game Over! Press any key or Y button to restart.", True, RED)
    over_rect = over_text.get_rect(center=(WIDTH//2, HEIGHT//2))
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
                    waiting = False

def main():
    while True:
        run_game()

if __name__ == "__main__":
    main()
