import pygame
from pygame import DOUBLEBUF
import os

"""display"""
pygame.init()
infoS = pygame.display.Info()
clock = pygame.time.Clock()
WINDOW_WIDTH, WINDOW_HEIGHT = 1600,900
Fullscreen=False
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT),DOUBLEBUF)
dt = 0.0
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Navigate up to the root and then into Fonts
FONT_PATH = os.path.join(BASE_DIR, "..", "Fonts", "PixelFont.ttf")
pixel_font = pygame.font.Font(FONT_PATH, 20)
pixel_font5 = pygame.font.Font(FONT_PATH, 50)
