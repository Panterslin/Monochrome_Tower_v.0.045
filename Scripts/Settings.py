import pygame
import time
from pygame import DOUBLEBUF


"""display"""
pygame.init()
infoS = pygame.display.Info()
clock = pygame.time.Clock()
WINDOW_WIDTH, WINDOW_HEIGHT = 1600,900
Fullscreen=False
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT),DOUBLEBUF)
previous_time=time.time()
dt = clock.tick(60)/1000
