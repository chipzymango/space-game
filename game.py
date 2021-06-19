from typing import cast
import pygame
from pygame import init, key
from pygame import mouse
from pygame.locals import *
import random
import os

# initialize all pygame modules
pygame.init()

WINDOW_X = 1200
WINDOW_Y = 600

WINDOW = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
pygame.display.set_caption("Game")

GUI_FONT = pygame.font.SysFont('consolas', 20) # defining font to use in game score and health
GAME_OVER_FONT = pygame.font.SysFont('consolas', 30) # for game over font

BLACK = (0, 0, 0)
SPACE_BLACK = (15, 15, 15)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
INGAME_BG = (225, 225, 225)
DARK_RED = (175, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 126, 0)

FPS = 60

BULLETS_LIMIT = 3

PLAYER_WAS_HIT_EVENT = pygame.USEREVENT + 1 # create a new event for when player gets hit by enemy
PLAYER_BULLET_HIT_EVENT = pygame.USEREVENT + 2 # create new element for when a bullet hits an enemy

SHOOT_SOUND = pygame.mixer.Sound("assets/sounds/shooting_sfx.wav")
NEW_LIFE_SOUND = pygame.mixer.Sound("assets/sounds/1up_sfx.wav")
ROCKET_EXPLOSION_SOUND = pygame.mixer.Sound("assets/sounds/player_lost.wav")

# initializing groups
effect_group = pygame.sprite.Group()
background_effect_group = pygame.sprite.Group()
rocket_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
obstacles_group = pygame.sprite.Group()
total_rockets_group = pygame.sprite.Group()
total_obstacles_group = pygame.sprite.Group()
buttons_group = pygame.sprite.Group()

mouse_key_pressed = pygame.mouse.get_pressed()

clock = pygame.time.Clock() # set clock for fps

render_main_menu = True
render_in_game = False

# we use this class every time we want
# to add a new rocket to the screen
class Rocket(pygame.sprite.Sprite):
    # initialize the rocket's properties 
    # these variables are created
    # immediately as the class is called
    def __init__(self, x, y, rocket_type=0, size=1, health=10, speed=1, flipped=False, auto_group=True):
        pygame.sprite.Sprite.__init__(self)
        self.rocket_type = rocket_type
        self.image = pygame.image.load('assets/visual/rockets/rocket_' + str(self.rocket_type) + '.png').convert()
        self.x = x
        self.y = y
        self.dx = 0 # delta x
        self.dy = 0 # delta y
        self.size = size
        self.speed = speed
        self.accel = self.speed / 20
        self.max_xvelocity = self.speed
        self.max_yvelocity = self.speed / 2
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

        unique_id = 0

        for each_rocket in total_rockets_group:
            unique_id += 1

        self.unique_id = unique_id
    
        if self.autogroup:
            rocket_group.add(self)

        total_rockets_group.add(self)

        print("New rocket created")

        # store the instance's bullets
        self.active_bullets = []

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

        # make white pixels transparent
        self.image.set_colorkey(WHITE)

        WINDOW.blit(self.image, (self.x, self.y))


    def move(self):

        if self.alive:
            # increase or decrease x coordinate by acceleration
            # until it reaches max_velocity for the rocket
            if self.moving_right:
                if self.dx >= self.max_xvelocity:
                    self.dx == self.max_xvelocity
                else:
                    self.dx += self.accel
            else:
                if self.dx > 0:
                    self.dx -= self.accel

                    
            if self.moving_left:
                if self.dx <= -self.max_xvelocity:
                    self.dx = -self.max_xvelocity
                else:
                    self.dx += -self.accel
            else:
                if self.dx < 0:
                    self.dx += self.accel


            if self.moving_down:
                if self.dy >= self.max_yvelocity:
                    self.dy = self.max_yvelocity
                else:
                    self.dy += self.accel
            else:
                if self.dy > 0:
                    self.dy -= self.accel


            if self.moving_up:
                if self.dy <= -self.max_yvelocity:
                    self.dy = -self.max_yvelocity
                else:
                    self.dy += -self.accel
            else:
                if self.dy < 0:
                    self.dy += self.accel

        # round up the numbers to prevent inaccuracy
        self.dx = round(self.dx, 2)
        self.dy = round(self.dy, 2)

         # increment / decrement rectangle's
         # x coord. by dx and its y by dy
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    def shoot(self):
        
        # check if rocket is flipped to ensure
        # bullet spawns in the right position
        if self.alive:
            if not self.flipped:
                self.bullet = Bullet(self.unique_id, self.x + self.image.get_width(), self.y + self.image.get_height() / 2, size=self.size, speed=self.speed * 4, flipped=self.flipped)
                self.active_bullets.append(self.bullet)

            else:
                self.bullet = Bullet(self.unique_id, self.x, self.y + self.image.get_height() / 2, size=self.size, speed=self.speed * 4, flipped=self.flipped)
                self.active_bullets.append(self.bullet)
            
        else:
            print("rocket " + str(self.unique_id) + " is already dead")

class Bullet(pygame.sprite.Sprite):
    def __init__(self, unique_id, x, y, size=1, speed=1, flipped=False):
        pygame.sprite.Sprite.__init__(self)
        self.unique_id = unique_id
        self.image = pygame.image.load('assets/visual/bullets/0.png').convert()
        self.rocket_flipped = flipped
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.size, self.image.get_height() * self.size) )
        self.rect = self.image.get_rect()
        self.effect_startup_timer = pygame.time.get_ticks()
        bullet_group.add(self)
        SHOOT_SOUND.play()
        print("Bullet shot!")

    def update(self):
        self.rect = self.image.get_rect()
        self.rect.left = self.x
        self.rect.top = self.y

        if self.rocket_flipped:
            self.x -= 5
        else:
            self.x += 5
        
        if self.x > WINDOW_X or self.x < 0:
            print("Bullet " + str(self.unique_id) + " reached border, deleting.")
            self.kill()

        self.check_collisions()

        WINDOW.blit(self.image, (self.x, self.y))

    def check_collisions(self):

            # check if bullet collides with this rocket
            if pygame.sprite.spritecollide(self, rocket_group, False):

                # for each bullet in bullet group
                for each_group_sprite in pygame.sprite.spritecollide(self, rocket_group, False):

                    # if this rocket collides with its own bullet with the same id
                    if each_group_sprite.unique_id == self.unique_id:
                        pass
                    else:
                        print("bullet " + str(self.unique_id) + " has collided with rocket " + str(each_group_sprite.unique_id))
                        bullet_group.remove(self)
                        rocket_group.remove(each_group_sprite)
                        each_group_sprite.alive = False
                        explosion_size = each_group_sprite.size
                        explosion = Effect('explosion_animation', each_group_sprite.x, each_group_sprite.y, size=explosion_size)
                        ROCKET_EXPLOSION_SOUND.play()
                        self.kill()

            if pygame.sprite.spritecollide(self, obstacles_group, False):
                print(pygame.sprite.spritecollide(self, obstacles_group, False))

                # for each bullet in bullet group
                for each_group_sprite in pygame.sprite.spritecollide(self, obstacles_group, False):
                    
                    # if this rocket collides with its own bullet with the same id
                    print("bullet " + str(self.unique_id) + " has collided with obstacle " + str(each_group_sprite.unique_id))
                    bullet_group.remove(self)
                    obstacles_group.remove(each_group_sprite)
                    each_group_sprite.alive = False
                    explosion_size = each_group_sprite.size
                    explosion = Effect('explosion_animation', each_group_sprite.x, each_group_sprite.y, size=explosion_size * 3)
                    ROCKET_EXPLOSION_SOUND.play()
                    self.kill()

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
                current_image = pygame.image.load('assets/visual/effects/' + self.effect_type + '/' + str(i)).convert()
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
                current_image = pygame.image.load('assets/visual/background_effects/' + self.effect_type + '/' + str(i)).convert()
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
    def __init__(self, x, y, object_type='tree', size=1, x_vel=3, y_vel=0):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.object_type = object_type
        self.size = size
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.image = pygame.image.load('assets/visual/obstacles/' + self.object_type + '.png').convert()
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.size, self.image.get_height() * self.size))
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        obstacles_group.add(self)
        total_obstacles_group.add(self)

        unique_id = 0

        for each_obstacle in total_obstacles_group:
            unique_id += 1

        self.unique_id = unique_id

    def update(self):
        self.x -= self.x_vel
        self.y -= self.y_vel

        self.rect.left = self.x
        self.rect.top = self.y

        if self.x < 0:
            self.x = WINDOW_X + self.image.get_width()

        WINDOW.blit(self.image, (self.x, self.y))
        
class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=ORANGE, text='button', font='consolas', font_size=15):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.default_color = color
        self.text = text
        self.font = pygame.font.SysFont(font, font_size) # defining font to use for buttons
        self.button_text = self.font.render(self.text, 1, BLACK)
        self.button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.clicked = False

        buttons_group.add(self)

    def update(self):

        global render_main_menu
        global render_in_game

        mouse_key_pressed = pygame.mouse.get_pressed()

        if self.button_rect.colliderect(game_mouse_cursor_rect):
            self.color = WHITE
            if mouse_key_pressed[0]:
                self.color = YELLOW
        else:
            self.color = self.default_color

        pygame.draw.rect(WINDOW, self.color, self.button_rect)
        WINDOW.blit(self.button_text, (self.x + self.button_rect.width / 3, self.y + self.button_rect.height / 3 ))

menu_button = Button(WINDOW_X / 2.5, WINDOW_Y - 100, 150, 50, text="start")
game_button = Button(WINDOW_X - 100, 20, 80, 25, color=YELLOW, text="menu", font_size=14)
reset_button = Button(WINDOW_X - 200, 20, 80, 25, color=ORANGE, text="reset", font_size=14)

title_image = pygame.image.load('assets/visual/menu/game_logo2.png').convert()
game_mouse_cursor_image = pygame.image.load("assets/visual/menu/mouse.png").convert()
game_mouse_cursor_image = pygame.transform.scale(game_mouse_cursor_image, (game_mouse_cursor_image.get_width() * 2, game_mouse_cursor_image.get_height() * 2))
game_mouse_cursor_image.set_colorkey((255,255,255))
game_mouse_cursor_rect = game_mouse_cursor_image.get_rect()


player_start_x, player_start_y = 500, 400
# set / initialize game entities
player = Rocket(player_start_x, player_start_y, 1, speed=3, size=3)
enemy = Rocket(100, 100, 0, 4, 10, 1, flipped=True)

for each_star in range(40):
    rx = random.randint(10, WINDOW_X - 10)
    ry = random.randint(10, WINDOW_X - 10)
    variant = 'background_star_animation'
    if each_star % 2 == 1: # every odd number will return 1
        variant = 'background_star_animation/blue'
    each_star = BackgroundEffect(variant, rx, ry, size=1, looping=True, loop_with_reverse=True)

test_tree = Obstacle(1200, 500)

def initialize_game():
    
    # kill all previous entities / sprites
    rocket_group.empty()
    bullet_group.empty()
    effect_group.empty()
    background_effect_group.empty()
    obstacles_group.empty()
    total_rockets_group.empty()
    total_obstacles_group.empty()

    WINDOW.fill(SPACE_BLACK)

    # simply re-add player to rocket group since
    # player is still an instance of the rocket class
    # (no need to recreate player instance)
    rocket_group.add(player)
    rocket_group.add(enemy)
    
    # reset players position back to original positions
    player.x, player.y = player_start_x, player_start_y
    player.alive = True
    enemy.alive = True
    player.dx = 0
    player.dy = 0

    for each_star in range(40):
        rx = random.randint(10, WINDOW_X - 10)
        ry = random.randint(10, WINDOW_X - 10)
        variant = 'background_star_animation'
        if each_star % 2 == 1: # every odd number will return 1
            variant = 'background_star_animation/blue'
        each_star = BackgroundEffect(variant, rx, ry, size=1, looping=True, loop_with_reverse=True)

    test_tree = Obstacle(1200, 500)
    
hide_mouse = False
reset_game = False

run = True # game loop = True
while run: # while game is looping...
    print(player.dx)
    # this for loop is not compatible with more than 2 rockets on the screen
    clock.tick(FPS) # ensures loop never goes above fps variable

    real_mouse_cursor_x = pygame.mouse.get_pos()[0]
    real_mouse_cursor_y = pygame.mouse.get_pos()[1]
    game_mouse_cursor_rect.x = real_mouse_cursor_x
    game_mouse_cursor_rect.y = real_mouse_cursor_y

    # reinitialize game entities
    if reset_game:
        initialize_game()
        reset_game = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONUP:

            # check if mouse button is clicked on button
            if menu_button.button_rect.colliderect(game_mouse_cursor_rect):
                if event.button == 1:
                    menu_button.clicked = True
                    hide_mouse = True
            
            if game_button.button_rect.colliderect(game_mouse_cursor_rect):
                if event.button == 1:
                    game_button.clicked = True

            if reset_button.button_rect.colliderect(game_mouse_cursor_rect):
                    if event.button == 1:
                        reset_button.clicked = True

        # hide / show mouse in main menu with 'h' button
        if render_main_menu:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    if not hide_mouse:
                        hide_mouse = True
                    else:
                        hide_mouse = False

        # handle rocket shooting inputs
        elif render_in_game:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()

                if event.key == pygame.K_BACKSPACE:
                    enemy.shoot()

                if event.key == pygame.K_h:
                    if not hide_mouse:
                        hide_mouse = True
                    else:
                        hide_mouse = False

    # - render the main menu screen -
    if render_main_menu:
        WINDOW.fill(GRAY)
        WINDOW.blit(title_image, (250, 50) )

        # updating the button each frame
        # so it can detect clicks
        menu_button.update()

        if not hide_mouse:
            WINDOW.blit(game_mouse_cursor_image, (game_mouse_cursor_rect.x, game_mouse_cursor_rect.y))
            pygame.mouse.set_visible(False)

    # - render the game screen -
    elif render_in_game:

        WINDOW.fill(SPACE_BLACK)
        background_effect_group.update()
        rocket_group.update()
        obstacles_group.update()
        bullet_group.update()
        effect_group.update()

        player.move()
        enemy.move()

        game_button.update()
        reset_button.update()
        
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

        if keys_pressed[pygame.K_m]:
            rx_vel = random.randint(1, 10)
            r_size = random.randint(1, 3)
            ry = random.randint(40, WINDOW_Y - 40)

            obst = Obstacle(WINDOW_X + 50, ry, x_vel=rx_vel, size=r_size)

        if keys_pressed[pygame.K_n]:
            rx = random.randint(20, WINDOW_X - 20)
            ry = random.randint(20, WINDOW_Y - 20)

            flip_chance = random.choice([0, 1])

            if flip_chance == 0:
                flip_chance = True
            else:
                flip_chance = False

            drone = Rocket(rx, ry, size=2, flipped=flip_chance)
            
            if keys_pressed[pygame.K_LSHIFT]:
                drone.shoot()

            if not hide_mouse:
                WINDOW.blit(game_mouse_cursor_image, (game_mouse_cursor_rect.x, game_mouse_cursor_rect.y))
                pygame.mouse.set_visible(False)

    # check which buttons were clicked
    if menu_button.clicked:
        render_main_menu = False
        render_in_game = True

        # falsify button click so it can be used again        
        menu_button.clicked = False

        reset_game = True
        hide_mouse = False

    if game_button.clicked:
        render_in_game = False
        render_main_menu = True

        game_button.clicked = False

    if reset_button.clicked:
        reset_game = True
        render_in_game = True

        reset_button.clicked = False

    # hide / show mouse cursor
    if not hide_mouse:
        WINDOW.blit(game_mouse_cursor_image, (game_mouse_cursor_rect.x, game_mouse_cursor_rect.y))
        pygame.mouse.set_visible(False)

    pygame.display.update() # update the display every frame

pygame.quit()

if __name__ == "__main__":
    run = True
else:
    run = False