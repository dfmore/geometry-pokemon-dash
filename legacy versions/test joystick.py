import pygame

# Initialize Pygame and its joystick module
pygame.init()
pygame.joystick.init()

# Setup screen for displaying information
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Joystick Test")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Check for a connected joystick
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    joystick_name = joystick.get_name()
    print("Joystick detected:", joystick_name)
else:
    joystick = None
    joystick_name = "No Joystick Found"
    print("No joystick found.")

# Instruction text
instructions = "Press A button (button index 0) on your joystick" if joystick else "No joystick found."
button_test_message = ""

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle joystick button events
        if event.type == pygame.JOYBUTTONDOWN:
            # Assuming button 0 is the A button
            if event.button == 0:
                print("A button pressed!")
                button_test_message = "A button is working!"
        if event.type == pygame.JOYBUTTONUP:
            if event.button == 0:
                button_test_message = "A button released."

    # Clear the screen
    screen.fill((255, 255, 255))

    # Render joystick information
    text_surface = font.render("Joystick: " + joystick_name, True, (0, 0, 0))
    screen.blit(text_surface, (50, 50))
    
    # Render instructions
    instr_surface = font.render(instructions, True, (0, 0, 0))
    screen.blit(instr_surface, (50, 100))
    
    # Render button test message
    if button_test_message:
        test_surface = font.render(button_test_message, True, (0, 150, 0))
        screen.blit(test_surface, (50, 150))
    
    pygame.display.update()
    clock.tick(30)

pygame.quit()
