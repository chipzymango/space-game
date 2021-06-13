import pygame
from pygame.locals import *
import random
import os

# initialize all pygame modules
pygame.init()

WINDOW_X = 1200
WINDOW_Y = 600

WINDOW = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
pygame.display.set_caption("Game")

GUI_FONT = pygame.font.SysFont('consolas', 20) # defining ingame font
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
NEW_LIFE_SOUND = pygame.mixer.Sound("assets/sounds/1up_sfx.wav")
ROCKET_EXPLOSION_SOUND = pygame.mixer.Sound("assets/sounds/player_lost.wav")

# we use this class every time we want
# to add a new rocket to the screen
class Rocket(pygame.sprite.Sprite):
    # initialize the rocket's properties 
    # these variables are created
    # immediately as the class is called
    def __init__(self, rocket_id, x, y, size=1, health=10, speed=1, flipped=False, auto_group=True):
        pygame.sprite.Sprite.__init__(self)
        self.rocket_id = rocket_id        
        self.image = pygame.image.load('assets/visual/rockets/rocket_' + str(rocket_id) + '.png')
        self.x = x
        self.y = y
        self.dx = 0 # delta x
        self.dy = 0 # delta y
        self.size = size
        self.speed = speed
        self.accel = self.speed / 10
        self.health = health
        self.score = 0
        self.flipped = flipped
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False
        self.alive = True
        self.autogroup = auto_group

        if self.alive == False:
            print("You have died!")

        # check if rocket is flipped
        if self.flipped:
            self.image = pygame.transform.rotate(self.image, -90)
        else:
            self.image = pygame.transform.rotate(self.image, 90)

        # resize image after input scale
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.size, self.image.get_height() * self.size)) #self.rect.x * self.size, self.rect.y * self.size

        # below a is rectangle box of the rocket
        # it can work as a hitbox for collision
        # between rockets and bullets
        # this is NOT used to move the rocket itself
        # for that you must use self.x and .y / dx and dy

         # create a rect from the final image
        self.rect = self.image.get_rect()
        self.bullet_offset = 4
    
        if self.autogroup:
            rocket_group.add(self)

        print("New rocket created")

    # the method below will run every game frame and handles
    # repetetive tasks such as displaying images
    # and resizing images
    # a method is the exact same as a function
    # except it belongs / is binded to a class
    def update(self):

        # updating the stats every frame
        # for correct position of the rect
        self.rect = self.image.get_rect()
        self.rect.left = self.x
        self.rect.top = self.y

        # draw the hitboxes
        pygame.draw.rect(WINDOW, RED, self.rect)

        # make white pixels transparent
        self.image.set_colorkey((WHITE))

        self.check_collisions()

        WINDOW.blit(self.image, (self.x, self.y))

    def check_collisions(self):
        # check if a bullet collides with this rocket
        # if so, delete bullet and rocket
        if pygame.sprite.spritecollide(self, bullet_group, True):
            print("rocket '" + str(self) + "'has collided with a bullet")
            rocket_group.remove(self)
            self.alive = False
            explode = Effect('explosion_animation', self.x, self.y, size=3)
            self.kill()

    def move(self):
        if self.alive:
            # increase or decrease x coordinate by speed
            # which was chosen when calling the class
            if self.moving_right:
                self.dx = 2
            elif self.moving_left:
                self.dx = -2
            else:
                self.dx = 0

            if self.moving_up:
                self.dy = -2
            elif self.moving_down:
                self.dy = 2
            else:
                self.dy = 0

         # increment / decrement rectangle's
         # x by dx and its y by dy
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    def shoot(self):
        
        # check if rocket is flipped to ensure
        # bullet spawns in the right position
        if self.alive:
            if not self.flipped:
                self.bullet = Bullet(self.x + self.image.get_width() + self.bullet_offset, self.y + self.image.get_height() / 2, size=self.size, speed=self.speed, flipped=self.flipped)
            else:
                self.bullet = Bullet(self.x  - self.bullet_offset, self.y + self.image.get_height() / 2, size=self.size, speed=self.speed, flipped=self.flipped)
        else:
            print("you are dead")

class Bullet(Rocket, pygame.sprite.Sprite):
    def __init__(self, x, y, size=1, speed=5, flipped=False):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/visual/bullets/0.png')
        self.rocket_flipped = flipped
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.size, self.image.get_height() * self.size) )
        self.rect = self.image.get_rect()
        self.effect_startup_timer = pygame.time.get_ticks()
        self.effect_startup_period = 100
        bullet_group.add(self)
        SHOOT_SOUND.play()
        print("Bullet shot!")

    def update(self):
        self.rect = self.image.get_rect()
        self.rect.left = self.x
        self.rect.top = self.y

        if self.rocket_flipped:
            self.x -= 2 * self.speed
        else:
            self.x += 2 * self.speed
        
        if self.x > WINDOW_X or self.x < 0:
            print("Bullet reached border, deleting.")
            bullet_group.remove(self)

        WINDOW.blit(self.image, (self.x, self.y))

class Effect(pygame.sprite.Sprite):
    def __init__(self, effect_type, x, y, size=3, cooldown=80, looping=False, loop_with_reverse=False):
        pygame.sprite.Sprite.__init__(self)
        self.effect_type = effect_type
        self.x = x
        self.y = y
        self.size = size
        self.looping = looping
        self.timer = pygame.time.get_ticks()
        self.COOLDOWN = cooldown
        self.reverse_iteration = False
        self.loop_with_reverse = loop_with_reverse
        self.path = os.listdir('assets/visual/effects/' + str(self.effect_type))

        self.animation_list = []

        for i in self.path:
            if i.count(".png"):
                current_image = pygame.image.load('assets/visual/effects/' + self.effect_type + '/' + str(i))
                self.animation_list.append(current_image)
            else:
                pass
        
        self.animation_frame = 0
        self.current_image = self.animation_list[self.animation_frame]
        
        # resize current image after input scale
        self.current_image = pygame.transform.scale(self.current_image, (self.current_image.get_width() * self.size, self.current_image.get_height() * self.size) )

        # remove white color in the image
        self.current_image.set_colorkey(WHITE)

        effect_group.add(self)
        
    def update(self):

        self.current_image = self.animation_list[self.animation_frame]
        self.current_image = pygame.transform.scale(self.current_image, (self.current_image.get_width() * self.size, self.current_image.get_height() * self.size) )
        self.current_image.set_colorkey((255,255,255))

        if pygame.time.get_ticks() - self.timer > self.COOLDOWN:
            if self.reverse_iteration == False:
                self.animation_frame += 1
            else:
                self.animation_frame -= 1

            self.timer = pygame.time.get_ticks()

        # if animation frame is iterating over total amount of images
        if self.animation_frame >= len(self.animation_list):
            if self.loop_with_reverse:
                self.reverse_iteration = True
                self.animation_frame -= 2
            
            else:
                self.animation_frame = 0
                if not self.looping:
                    effect_group.remove(self)
                    self.animation_list.clear()
            
        # if animation frame is iterating under 0
        if self.animation_frame < 0:
            if self.looping: 
                self.reverse_iteration = False
                self.animation_frame += 2

            else:
                effect_group.remove(self)
                self.animation_list.clear()

        WINDOW.blit(self.current_image, (self.x, self.y))

class BackgroundEffect(pygame.sprite.Sprite):
    def __init__(self, effect_type, x, y, size=1, cooldown=200, looping=False, loop_with_reverse=False):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.size = size
        self.COOLDOWN = cooldown
        self.effect_type = effect_type
        self.path = os.listdir('assets/visual/background_effects/' + str(self.effect_type))

        self.animation_list = []

        for i in self.path:
            if i.count(".png"):
                current_image = pygame.image.load('assets/visual/background_effects/' + self.effect_type + '/' + str(i))
                self.animation_list.append(current_image)
            else:
                pass

        self.animation_frame = 0
        self.image = self.animation_list[self.animation_frame]
        self.image.set_colorkey((255,255,255))
        self.timer = pygame.time.get_ticks()
        self.looping = looping
        self.loop_with_reverse = loop_with_reverse
        self.reverse_iteration = False
        self.moving = False
        background_effect_group.add(self)

    def update(self):

        self.image = self.animation_list[self.animation_frame]
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.size, self.image.get_height() * self.size))
        self.image.set_colorkey((255,255,255))
        
        # if enough time has gone for the animation to update
        if pygame.time.get_ticks() - self.timer > self.COOLDOWN:
            if self.reverse_iteration == False:
                self.animation_frame += 1
            else:
                self.animation_frame -= 1

            self.timer = pygame.time.get_ticks()

        # if animation frame is iterating over total amount of images
        if self.animation_frame >= len(self.animation_list):
            if self.loop_with_reverse:
                self.reverse_iteration = True
                self.animation_frame -= 2

            else:
                self.animation_frame = 0
                if not self.looping:
                    background_effect_group.remove(self)
                    self.animation_list.clear()

        # if animation frame is iterating under 0
        if self.animation_frame < 0:
            if self.looping:
                self.reverse_iteration = False
                self.animation_frame += 2

            else:
                background_effect_group.remove(self)
                # clear animation list aswell to save performance
                self.animation_list.clear()


        if self.x + self.image.get_width() < 0:
            self.x = WINDOW_X + self.image.get_width()

        self.x -= 1


        WINDOW.blit(self.image, (self.x, self.y))

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, object_type, x, y, size=3, x_vel=3, y_vel=0):
        pygame.sprite.Sprite.__init__(self)
        self.object_type = object_type
        self.x = x
        self.y = y
        self.size = size
        self.x_vel = x_vel
        self.y_vel = y_vel

        self.image = pygame.image.load('assets/visual/obstacles/' + self.object_type + '.png')

        obstacles_group.add(self)

    def update(self):
        self.x -= self.x_vel
        self.y -= self.y_vel

        if self.x < 0:
            self.x = WINDOW_X + self.image.get_width()

        WINDOW.blit(self.image, (self.x, self.y))

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

effect_group = pygame.sprite.Group()
background_effect_group = pygame.sprite.Group()
rocket_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
obstacles_group = pygame.sprite.Group()

player = Rocket(1, 250, 250, 5, 15, 1)

enemy = Rocket(0, 100, 100, 4, 10, 1, flipped=True)

# star = background_star_animation
# rocket_fire = rocket_flame_animation
# explosion = explosion_animation

for each_star in range(40):
    rx = random.randint(10, WINDOW_X - 10)
    ry = random.randint(10, WINDOW_X - 10)
    variant = 'background_star_animation'
    if each_star % 2 == 1: # every odd number will return 1
        variant = 'background_star_animation/blue'
    each_star = BackgroundEffect(variant, rx, ry, size=1, looping=True, loop_with_reverse=True)

test_tree = Obstacle('tree', 1200, 500)

clock = pygame.time.Clock() # set clock for fps

run = True # game loop = True
while run: # while game is looping...

    WINDOW.fill(BLACK)

    effect_group.update()
    background_effect_group.update()
    rocket_group.update()
    player.move()
    enemy.move()
    bullet_group.update()
    obstacles_group.update()
    # this for loop is not compatible with more than 2 rockets on the screen
    
    clock.tick(FPS) # ensures loop never goes above fps variable

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN: #and len(player.active_bullet_list) < BULLETS_LIMIT: # True if key is held down and list of bullets has not reached max
            if event.key == pygame.K_SPACE:
                player.shoot()
                print("Bullet shot!")

            if event.key == pygame.K_BACKSPACE:
                enemy.shoot()

            if event.key == pygame.K_n:
                rx = random.randint(20, WINDOW_X - 20)
                ry = random.randint(20, WINDOW_Y - 20)

                flip_chance = random.choice([0, 1])

                if flip_chance == 0:
                    flip_chance = True
                else:
                    flip_chance = False    
                
                drone = Rocket(0, rx, ry, size=2, flipped=flip_chance)

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
        

    if keys_pressed[pygame.K_d] and enemy.x + enemy.image.get_width() < WINDOW_X:
        enemy.moving_right = True
    else:
        enemy.moving_right = False

    if keys_pressed[pygame.K_a] and enemy.x > 0:
        enemy.moving_left = True
    else:
        enemy.moving_left = False

    if keys_pressed[pygame.K_s] and enemy.y + enemy.image.get_height() < WINDOW_Y:
        enemy.moving_down = True
    else:
        enemy.moving_down = False

    if keys_pressed[pygame.K_w] and player.y > 0:
        enemy.moving_up = True
    else:
        enemy.moving_up = False

    mouse_cursor_x = pygame.mouse.get_pos()[0]
    mouse_cursor_y = pygame.mouse.get_pos()[1]

    pygame.display.update() # update the display every frame

pygame.quit()

if __name__ == "__main__":
    run = True
else:
    run = False