import pygame
from pygame.locals import *

pygame.init() # initalize pygame stuff + background timer starts

WINDOW_X = 1200
WINDOW_Y = 600

WINDOW = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
pygame.display.set_caption("Game")

GUI_FONT = pygame.font.SysFont('consolas', 20) # defining font to use in game score and health
GAME_OVER_FONT = pygame.font.SysFont('consolas', 30) # for game over font

BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
INGAME_BG = (150, 120, 110)
DARK_RED = (175, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 126, 0)

FPS = 60

VEL = 4

BULLET_VEL = 7

BIG_BULLET_VEL = 4

BULLETS_LIMIT = 3


PLAYER_WAS_HIT_EVENT = pygame.USEREVENT + 1 # create a new event for when player gets hit by enemy

PLAYER_BULLET_HIT_EVENT = pygame.USEREVENT + 2 # create new element for when a bullet hits an enemy


PLAYER_IMAGE = pygame.image.load("assets/images/rocket_class_2.png") # load image

PLAYER_IMAGE = pygame.transform.scale(PLAYER_IMAGE, (28, 28)) # resize image

PLAYER_IMAGE = pygame.transform.rotate(PLAYER_IMAGE, 180)

PLAYER_IMAGE.set_colorkey(WHITE) # make white pixels transparent

PLAYER_WIDTH = PLAYER_IMAGE.get_width()

PLAYER_HEIGHT = PLAYER_IMAGE.get_height()

SHOOT_SOUND = pygame.mixer.Sound("assets/sounds/shooting_sfx.wav")

NEW_LIFE = pygame.mixer.Sound("assets/sounds/1up_sfx.wav")

ROCKET_EXPLOSION_SOUND = pygame.mixer.Sound("assets/sounds/player_lost.wav")

background_image = pygame.image.load("assets/images/space_bg.jpg")

background_image = pygame.transform.scale(background_image, (1200, 800))

background_surface = pygame.Surface((WINDOW_X, WINDOW_Y)) # size of surface is equal to size of window

def draw_window(
    player_box, 
    keys_pressed, 
    active_bullets, 
    enemy_box, 
    ENEMY_MINION, 
    MOVING_ENEMY, 
    PLAYER_HEALTH, 
    PLAYER_SCORE, 
    active_enemy_bullets, 
    PLAYER_LOST, 
    MOUSE_BOX,
    active_mouse_bullets): # all drawing happens inside this

    background_surface.fill(WHITE) # adds white to the display

    health_text = GUI_FONT.render("Health: " + str(PLAYER_HEALTH), 1, WHITE)
    score_text = GUI_FONT.render("Score: " + str(PLAYER_SCORE), 1, YELLOW)

    WINDOW.blit(background_surface, (0, 0))
    WINDOW.blit(background_image, (0, 0))
    WINDOW.blit(health_text, (WINDOW_X - 120, WINDOW_Y - 20))
    WINDOW.blit(score_text, (25, WINDOW_Y - 20))

    pygame.draw.rect(WINDOW, DARK_RED, enemy_box)
    pygame.draw.rect(WINDOW, YELLOW, MOVING_ENEMY)
    pygame.draw.rect(WINDOW, ORANGE, MOUSE_BOX)

    if PLAYER_LOST:
        draw_results(PLAYER_SCORE)
    else:
        WINDOW.blit(PLAYER_IMAGE, (player_box.x, player_box.y))

    for bullet in active_bullets:
        pygame.draw.rect(WINDOW, RED, bullet)
    
    for evil_bullet in active_enemy_bullets:
        pygame.draw.rect(WINDOW, ORANGE, evil_bullet)

    pygame.display.update()

def handle_bullets(active_bullets, player_box, enemy_box, ENEMY_MINION, MOVING_ENEMY, active_enemy_bullets, MOUSE_BOX, active_mouse_bullets): # handle collision of bullets aswell as movement
    
    for bullet in active_bullets:
        bullet.y -= BULLET_VEL
        if enemy_box.colliderect(bullet) or ENEMY_MINION.colliderect(bullet):
            pygame.event.post(pygame.event.Event(PLAYER_BULLET_HIT_EVENT))
            active_bullets.remove(bullet)

            print("bullet has collided!")
    
    for evil_bullet in active_enemy_bullets:
        evil_bullet.x -= BULLET_VEL
        if player_box.colliderect(evil_bullet):
            pygame.event.post(pygame.event.Event(PLAYER_WAS_HIT_EVENT))
            active_enemy_bullets.remove(evil_bullet)
            print("you got hit")

def draw_results(total_score):

    game_over_text = GAME_OVER_FONT.render("You have lost! Total score: " + str(total_score), 1, RED)
    WINDOW.blit(game_over_text, (WINDOW_X / 2 - game_over_text.get_width() / 2, WINDOW_Y / 2 - game_over_text.get_height() ) )
    print(game_over_text.get_width())
    ROCKET_EXPLOSION_SOUND.play()
    length_of_audio = pygame.mixer.Sound("assets/sounds/player_lost.wav").get_length()
    length_of_audio *= 1000
    length_of_audio = int(length_of_audio)
    print(length_of_audio)

    pause_time = length_of_audio
    if length_of_audio < 4000: # check if the length of audio is less than 4 seconds
        pause_time = 4000 # then make the pause 4 seconds long (to prevent immediate restart)

    pygame.display.update()

    pygame.time.delay(pause_time)

    print("game is restarting...")
    main_loop() # restart main loop (game setting)

def draw_effect(scale, effect_type, rect_box):

    image = pygame.image.load('assets/images/effect/' + effect_type + '/effect.png')

    # scale image after it's original width and height
    image = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))

    time = pygame.time.get_ticks()

    # 300 milliseconds = 0.3 seconds which will be how long the effect is on screen
    EFFECT_DURATION = 300
    
    if pygame.time.get_ticks() - time > EFFECT_DURATION:
        pass
    else:
        WINDOW.blit(image, (rect_box.x - rect_box.width, rect_box.y - rect_box.height))

    pygame.display.update()

def main_loop():

    active_bullets = []

    active_enemy_bullets = []

    active_mouse_bullets = []

    PLAYER_HEALTH = 10

    PLAYER_SCORE = 0

    PLAYER_LOST = False

    player_box = pygame.Rect(100, 300, PLAYER_WIDTH, PLAYER_HEIGHT) # initialize rectangle (define dimensions)

    enemy_box = pygame.Rect(50, 0, WINDOW_X - 100, 40) # enemy rectangle box

    ENEMY_MINION = pygame.Rect(25, 25, 50, 50) # mini enemies rectangle box

    MOVING_ENEMY = pygame.Rect(500, 60, 40, 40) # flying mini enemies. Starts at position: (x, y) = (500, 600)

    MOUSE_BOX = pygame.Rect(40, 40, 8, 8)

    clock = pygame.time.Clock()


    run = True # game loop = True

    while run: # while game is looping...
    
        clock.tick(FPS) # ensures loop never goes above fps variable

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.KEYDOWN and len(active_bullets) < BULLETS_LIMIT: # True if key is held down and list of bullets has not reached max
                if event.key == pygame.K_SPACE:
                    SHOOT_SOUND.play()
                    bullet_box = pygame.Rect(player_box.x + player_box.width / 2 - 2, player_box.y, 4, 4) # create new bullet Rect
                    active_bullets.append(bullet_box) # append bullet Rect to active bullets list

                if event.key == pygame.K_BACKSPACE:
                    SHOOT_SOUND.play()
                    bullet_box = pygame.Rect(MOVING_ENEMY.x + MOVING_ENEMY.width / 2 - 2, MOVING_ENEMY.y + MOVING_ENEMY.height / 2 - 2, 4, 4) # create new bullet Rect
                    active_enemy_bullets.append(bullet_box) # append bullet Rect to active bullets list

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    SHOOT_SOUND.play()
                    bullet_box = pygame.Rect(MOUSE_BOX.x + MOUSE_BOX.width / 2 - 2, MOUSE_BOX.y + MOUSE_BOX.height / 2, 8,8)
                    active_mouse_bullets.append(bullet_box)

            if event.type == PLAYER_WAS_HIT_EVENT:
                PLAYER_HEALTH -= 1 # subtract hp every time player is attacked

            if event.type == PLAYER_BULLET_HIT_EVENT:
                if PLAYER_SCORE >= 69:
                    PLAYER_SCORE = 0
                    PLAYER_HEALTH += 1
                    NEW_LIFE.play()
                    print("New life!")
                else:
                    PLAYER_SCORE += 1

        if PLAYER_HEALTH <= 0:
            draw_effect(5, 'explosion', player_box)
            PLAYER_LOST = True

        keys_pressed = pygame.key.get_pressed()
        # this variable is assigned to whatever
        # key is being pressed at the current frame

        if keys_pressed[pygame.K_w]:
            MOVING_ENEMY.y -= 3
        if keys_pressed[pygame.K_s]:
            MOVING_ENEMY.y += 3
        if keys_pressed[pygame.K_a]:
            MOVING_ENEMY.x -= 3
        if keys_pressed[pygame.K_d]:
            MOVING_ENEMY.x += 3

        if keys_pressed[pygame.K_RIGHT] and player_box.x + player_box.width < WINDOW_X:
            player_box.x += VEL
        if keys_pressed[pygame.K_LEFT] and player_box.x > 0:
            player_box.x -= VEL
        if keys_pressed[pygame.K_DOWN] and player_box.y + player_box.height < WINDOW_Y:
            player_box.y += VEL
        if keys_pressed[pygame.K_UP] and player_box.y > 0:
            player_box.y -= VEL
        #if keys_pressed[pygame.K_f]:

        mouse_cursor_x = pygame.mouse.get_pos()[0] - 20
        mouse_cursor_y = pygame.mouse.get_pos()[1] - 20
        pygame.mouse.set_visible(False)
        
        MOUSE_BOX.x = mouse_cursor_x
        MOUSE_BOX.y = mouse_cursor_y

        handle_bullets(active_bullets, player_box, enemy_box, ENEMY_MINION, MOVING_ENEMY, active_enemy_bullets, active_mouse_bullets, MOUSE_BOX)

        draw_window(
            player_box, 
            keys_pressed, 
            active_bullets, 
            enemy_box, 
            ENEMY_MINION, 
            MOVING_ENEMY, 
            PLAYER_HEALTH, 
            PLAYER_SCORE, 
            active_enemy_bullets, 
            PLAYER_LOST,
            MOUSE_BOX,
            active_mouse_bullets
            )

        #if keys_pressed[pygame.K_r]:

    pygame.quit()

if __name__ == "__main__":
    main_loop()

# https://youtu.be/jO6qQDNa2UY?t=3903