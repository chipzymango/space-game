import pygame

# initializing events
PLAYER_WAS_HIT_EVENT = pygame.USEREVENT + 1 # create a new event for when player gets hit by enemy
PLAYER_BULLET_HIT_EVENT = pygame.USEREVENT + 2 # create new element for when a bullet hits an enemy