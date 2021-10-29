import pygame

# configure things
from config import *
from transitions import menu_screen_loop

screen_transition_in(menu_screen_loop, transition_type='fade')

pygame.quit()
exit()

if __name__ == "__main__":
    run = True
else:
    run = False