import pygame
from pygame.locals import *

# initialize font module for font and text
# initialize mixer module for sounds
pygame.init()

WINDOW_X = 600
WINDOW_Y = 400

WINDOW = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
pygame.display.set_caption("Game")

GUI_FONT = pygame.font.SysFont('consolas', 20) # defining font to use in game score and health
GAME_OVER_FONT = pygame.font.SysFont('consolas', 30) # for game over font

BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
INGAME_BG = (225, 225, 225)
DARK_RED = (175, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 126, 0)

FPS = 60

VEL = 4

BULLET_VEL = 7

BULLETS_LIMIT = 3


PLAYER_WAS_HIT_EVENT = pygame.USEREVENT + 1 # create a new event for when player gets hit by enemy

PLAYER_BULLET_HIT_EVENT = pygame.USEREVENT + 2 # create new element for when a bullet hits an enemy


SHOOT_SOUND = pygame.mixer.Sound("assets/sounds/shooting_sfx.wav")

NEW_LIFE = pygame.mixer.Sound("assets/sounds/1up_sfx.wav")

ROCKET_EXPLOSION_SOUND = pygame.mixer.Sound("assets/sounds/player_lost.wav")

background_image = pygame.image.load("assets/visual/background/space_bg.jpg")

background_image = pygame.transform.scale(background_image, (1200, 800))

background_surface = pygame.Surface((WINDOW_X, WINDOW_Y)) # size of surface is equal to size of window

tree_image = pygame.image.load("assets/visual/obstacles/tree.png")

tree_image.set_colorkey((255, 255, 255))
tree_image = pygame.transform.scale(tree_image, (tree_image.get_width()*2, tree_image.get_height()*2) )

class Rocket(): # we use this class every time we want to add a new rocket to the screen
    def __init__(self, rocket_id, x, y, scale, health, speed): # initialize variables

        self.rocket_id = rocket_id

        self.image = pygame.image.load('assets/visual/rockets/rocket_' + str(rocket_id) + '.png')
        
        self.x = x
        self.y = y

        self.dx = 0 # delta x
        self.dy = 0 # delta y

        self.scale = scale
        self.speed = speed
        self.accel = self.speed / 10
        self.health = health
        self.score = 0
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

        # below a is rectangle box of the rocket
        # it can work as a hitbox for collision
        # this is NOT used to move the rocket itself
        # for that you must use dx and dy
        self.rect = self.image.get_rect()
        self.active_bullet_list = []
        self.alive = True

        if self.alive == False:
            print("DED")

        self.image = pygame.transform.rotate(self.image, 90)
        self.image.set_colorkey(WHITE) # make white pixels transparent


    def move(self): # handle movement of the rocket

        self.dx = 0 # delta x
        self.dy = 0 # delta y

        if self.moving_right:
            self.dx = 2 # increase x coordinate by speed which was chosen under __init__ in this class

        if self.moving_left:
            self.dx = -2

        if self.moving_up:
            self.dy = -2

        if self.moving_down:
            self.dy = 2

        self.x += self.dx * self.speed # increment / decrement rectangle's x by dx
        self.y += self.dy * self.speed # increment / decrement rectangle's y by dy


    def handle_bullets(self):

        for each_bullet in self.active_bullet_list:

            pygame.draw.rect(WINDOW, ORANGE, each_bullet)

            each_bullet.x += BULLET_VEL

            r = pygame.Rect(WINDOW_X - 10, 0, 100, WINDOW_Y)

            if r.colliderect(each_bullet):
                ROCKET_EXPLOSION_SOUND.play()
                self.active_bullet_list.remove(each_bullet)
                bullet_explosion = Effect(1, each_bullet.x - 30, each_bullet.y, 5)
                active_effects.append(bullet_explosion)
                

    def shoot(self):

        self.bullet = pygame.Rect(self.x + self.rect.width * 3 * self.scale, self.y + self.rect.height * 3 * self.scale / 4 + 2, 4 * self.scale / 2, 4 * self.scale / 2) 

        self.active_bullet_list.append(self.bullet)
        

    def draw(self):

        self.image = pygame.transform.scale(self.image, (self.rect.height * 3 * self.scale, self.rect.width * 3 * self.scale)) #self.rect.x * self.scale, self.rect.y * self.scale

        self.image.set_colorkey((255, 255, 255))

        WINDOW.blit(self.image, (self.x, self.y))

        pygame.display.update()


class Effect():
    def __init__(self, effect_type, x, y, scale):
        
        self.effect_type = effect_type
        self.x = x
        self.y = y
        self.scale = scale

        self.animation_list = []
        self.frame_index = 0
        for i in range(7):
            current_image = pygame.image.load('assets/visual/explosion_animation/' + str(i) + '.png')
            self.animation_list.append(current_image)

        self.current_image = pygame.image.load('assets/visual/explosion_animation/' + str(self.frame_index) + '.png')

        self.update_time = pygame.time.get_ticks()
        
    def update_frame(self):

        self.current_image = pygame.image.load('assets/visual/explosion_animation/' + str(self.frame_index) + '.png')
        self.current_image = pygame.transform.scale(self.current_image, (self.current_image.get_width() * self.scale, self.current_image.get_height() * self.scale) )

        if pygame.time.get_ticks() - self.update_time > 100:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= 7:
            active_effects.remove(self)

    def draw(self):

        WINDOW.blit(self.current_image, (self.x, self.y))

        pygame.display.update()


def draw_results(total_score):

    game_over_text = GAME_OVER_FONT.render("You have lost! Total score: " + str(total_score), 1, RED)

    WINDOW.blit(game_over_text, (WINDOW_X / 2 - game_over_text.get_width() / 2, WINDOW_Y / 2 - game_over_text.get_height() ) )

    ROCKET_EXPLOSION_SOUND.play()

    length_of_audio = pygame.mixer.Sound("assets/sounds/player_lost.wav").get_length()

    length_of_audio *= 1000

    length_of_audio = int(length_of_audio)

    pause_time = length_of_audio

    if length_of_audio < 4000: # check if the length of audio is less than 4 seconds
        pause_time = 4000 # then make the pause 4 seconds long (to prevent immediate restart)

    pygame.display.update()

    pygame.time.delay(pause_time)

active_effects = []

player = Rocket(1, 250, 250, 1, 15, 1)
print('Rocket has been initialized')

clock = pygame.time.Clock() # set clock for fps

run = True # game loop = True
while run: # while game is looping...

    WINDOW.fill(INGAME_BG)

    player.handle_bullets()
    player.move()
    player.draw()

    for each_animation in active_effects:
        each_animation.draw()
        each_animation.update_frame()

    clock.tick(FPS) # ensures loop never goes above fps variable

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN and len(player.active_bullet_list) < BULLETS_LIMIT: # True if key is held down and list of bullets has not reached max
            if event.key == pygame.K_SPACE:
                SHOOT_SOUND.play()
                player.shoot()

    # this variable is assigned to a key
    # that is being pressed at the current frame
    keys_pressed = pygame.key.get_pressed()

    if keys_pressed[pygame.K_RIGHT] and player.x + player.image.get_width() < WINDOW_X:
        player.moving_right = True
    else:
        player.moving_right = False

    if keys_pressed[pygame.K_LEFT] and player.x > 0:
        player.moving_left = True
    else:
        player.moving_left = False

    if keys_pressed[pygame.K_DOWN] and player.y + player.image.get_height() < WINDOW_Y:
        player.moving_down = True
    else:
        player.moving_down = False

    if keys_pressed[pygame.K_UP] and player.y > 0:
        player.moving_up = True
    else:
        player.moving_up = False

    mouse_cursor_x = pygame.mouse.get_pos()[0]
    mouse_cursor_y = pygame.mouse.get_pos()[1]


pygame.quit()

if __name__ == "__main__":
    run = True
else:
    run = False
