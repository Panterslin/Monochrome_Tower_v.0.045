import pygame
from pygame import DOUBLEBUF


"""display"""
pygame.init()
infoS = pygame.display.Info()
clock = pygame.time.Clock()
WINDOW_WIDTH, WINDOW_HEIGHT = 1600,900
Fullscreen=False
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT),DOUBLEBUF)
dt = 0.0
pixel_font = pygame.font.Font('../Fonts/PixelFont.ttf', 20)
pixel_font5 = pygame.font.Font('../Fonts/PixelFont.ttf', 50)
