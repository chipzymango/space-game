import pygame
from pygame.locals import *
import random
import os

# initialize all pygame modules
pygame.init()

WINDOW_X = 1200
WINDOW_Y = 600

# initialize images
game_icon = pygame.image.load('assets/visual/game/game_icon.png')

WINDOW = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
pygame.display.set_caption("Game")

# we add a surface image as parameter for program icon
pygame.display.set_icon(game_icon)

# initializing color
BLACK = (0, 0, 0)
SPACE_BLACK = (15, 15, 15)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
MENU_GRAY = (210, 215, 215)
INGAME_BG = (225, 225, 225)
DARK_RED = (175, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 126, 0)
LIGHT_RED = (255, 210, 210)

# fixed fps
FPS = 60

clock = pygame.time.Clock()

# import and initalize objects
from classes import *

# initialize groups
from groups import *

# initializing sound effects
from sounds import *

# initialize fonts
from fonts import *