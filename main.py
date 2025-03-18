import pygame

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()
pygame.display.set_mode((800, 400))

from src.game import main

if __name__ == "__main__":
    main()