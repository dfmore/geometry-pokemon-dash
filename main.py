# main.py
import pygame

# Pre-initialize mixer
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

# Set the display mode
pygame.display.set_mode((800, 400))

from game import main

if __name__ == "__main__":
    main()
