import pygame
from pygame.locals import *

WINDOW_X = 600
WINDOW_Y = 400

WINDOW = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
pygame.display.set_caption("Game")


BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
INGAME_BG = (150, 120, 110)
DARK_RED = (175, 0, 0)
YELLOW = (255, 255, 0)

FPS = 60

VEL = 4

BULLET_VEL = 7

BULLETS_LIMIT = 3


PLAYER_HIT_EVENT = pygame.USEREVENT + 1 # create a new event for when player gets hit by enemy
PLAYER_BULLET_HIT_EVENT = pygame.USEREVENT + 2 # create new element for when a bullet hits an enemy


PLAYER_IMAGE = pygame.image.load("rocket_class_1.png") # load image

PLAYER_IMAGE = pygame.transform.scale(PLAYER_IMAGE, (20, 28)) # resize image

PLAYER_IMAGE = pygame.transform.rotate(PLAYER_IMAGE, 180)

PLAYER_IMAGE.set_colorkey(WHITE) # make white pixel transparent

PLAYER_WIDTH = PLAYER_IMAGE.get_width()

PLAYER_HEIGHT = PLAYER_IMAGE.get_height()

background_image = pygame.image.load("background.png")

background_surface = pygame.Surface((WINDOW_X, WINDOW_Y)) # size of surface is equal to size of window

def draw_window(player_box, keys_pressed, active_bullets, enemy_box, enemy_minion, PLAYER_HEALTH, PLAYER_SCORE): # all drawing happens inside this
    background_surface.fill(WHITE) # adds white to the display

    WINDOW.blit(background_surface, (0, 0))
    WINDOW.blit(background_image, (0, 0))
    WINDOW.blit(PLAYER_IMAGE, (player_box.x, player_box.y))

    pygame.draw.rect(WINDOW, DARK_RED, enemy_box)
    pygame.draw.rect(WINDOW, RED, enemy_minion)

    for bullet in active_bullets:
        pygame.draw.rect(WINDOW, RED, bullet)

    pygame.display.update()

def handle_bullets(active_bullets, enemy_box, enemy_minion, moving_enemy): # handle collision of bullets aswell as movement
    for bullet in active_bullets:
        bullet.y -= BULLET_VEL
        if enemy_box.colliderect(bullet) or enemy_minion.colliderect(bullet):
            pygame.event.post(pygame.event.Event(PLAYER_BULLET_HIT_EVENT))
            active_bullets.remove(bullet)
            print("bullet has collided!")

def main_loop():

    active_bullets = []

    PLAYER_HEALTH = 10

    PLAYER_SCORE = 0

    player_box = pygame.Rect(100, 300, PLAYER_WIDTH, PLAYER_HEIGHT) # initialize rectangle (define dimensions)

    enemy_box = pygame.Rect(0, 0, WINDOW_X, 20) # enemy rectangle box

    enemy_minion = pygame.Rect(25, 25, 50, 50) # mini enemies rectangle box

    moving_enemy = pygame.Rect(500, 60, 40, 40) # flying mini enemies. Starts at position: (x, y) = (500, 600)

    clock = pygame.time.Clock()

    run = True # game loop = True

    while run: # while game is running...

        clock.tick(FPS) 
        # ensures loop never goes above fps variable
        # FPS variable can be modified above

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
            if event.type == pygame.KEYDOWN and len(active_bullets) < BULLETS_LIMIT: 
                # True if key is held down and list
                # of bullets has not reached max
                
                if event.key == pygame.K_SPACE:
                    bullet_box = pygame.Rect(player_box.x + player_box.width / 2 - 2, player_box.y, 4, 4) # create new bullet Rect
                    active_bullets.append(bullet_box) # append bullet Rect to active bullets list
        
            if event.type == PLAYER_HIT_EVENT:
                PLAYER_HEALTH -= 1 # subtract hp every time player is attacked

            if event.type == PLAYER_BULLET_HIT_EVENT:
                if PLAYER_SCORE >= 9:
                    PLAYER_SCORE = 0
                    PLAYER_HEALTH += 1
                    print("New life!")
                else:
                    PLAYER_SCORE += 1
                                
        print(active_bullets)

        keys_pressed = pygame.key.get_pressed()
        # this variable is assigned to whatever
        # key is being pressed at the current frame

        if keys_pressed[pygame.K_w]:
            moving_enemy.y -= 3
        if keys_pressed[pygame.K_s]:
            moving_enemy.y += 3

        if keys_pressed[pygame.K_RIGHT] and player_box.x + player_box.width < WINDOW_X:
            player_box.x += VEL
        
        if keys_pressed[pygame.K_LEFT] and player_box.x > 0:
            player_box.x -= VEL
        
        if keys_pressed[pygame.K_DOWN] and player_box.y + player_box.height < WINDOW_Y:
            player_box.y += VEL

        if keys_pressed[pygame.K_UP] and player_box.y > 0:
            player_box.y -= VEL

        handle_bullets(active_bullets, enemy_box, enemy_minion, moving_enemy)

        draw_window(player_box, keys_pressed, active_bullets, enemy_box, enemy_minion, PLAYER_HEALTH, PLAYER_SCORE)

    pygame.quit()

if __name__ == "__main__":
    main_loop()

# https://youtu.be/jO6qQDNa2UY?t=3903