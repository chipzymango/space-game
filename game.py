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

game_icon = pygame.image.load('assets/visual/game/game_icon.png')

# we add a surface image as parameter for program icon
pygame.display.set_icon(game_icon)

LARGE_FONT = pygame.font.Font('assets/fonts/dpcomic.ttf', 45)
DEFAULT_FONT = pygame.font.Font('assets/fonts/dpcomic.ttf', 30) # defining font to use in game score and health
SMALL_FONT = pygame.font.Font('assets/fonts/dpcomic.ttf', 15)

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

FPS = 60

BULLETS_LIMIT = 3

# initializing events
PLAYER_WAS_HIT_EVENT = pygame.USEREVENT + 1 # create a new event for when player gets hit by enemy
PLAYER_BULLET_HIT_EVENT = pygame.USEREVENT + 2 # create new element for when a bullet hits an enemy

# initializing sound effects
SHOOT_SOUND = pygame.mixer.Sound("assets/sounds/shooting_sfx.wav")
NEW_LIFE_SOUND = pygame.mixer.Sound("assets/sounds/1up_sfx.wav")
ROCKET_EXPLOSION_SOUND = pygame.mixer.Sound("assets/sounds/player_lost.wav")
BUTTON_CLICKED = pygame.mixer.Sound("assets/sounds/buttonclick.wav")
BUTTON_CLICKED_BACK = pygame.mixer.Sound("assets/sounds/buttonclickback.wav")

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

        if self.rocket_type == 0 or self.rocket_type == 1:
            if not self.flipped:
                self.rocket_engine_fire_effect = Effect('rocket_flame_animation', self.x - self.image.get_width() / 2, self.y + self.image.get_height() / 2, size=self.size, looping=True, flipped=False, host=self)
            else:
                self.rocket_engine_fire_effect = Effect('rocket_flame_animation', self.x + self.image.get_width(), self.y + self.image.get_height() / 2, size=self.size, looping=True, flipped=True, host=self)
            
        elif self.rocket_type == 2:
            if not self.flipped:
                self.rocket_engine_fire_effect = Effect('rocket_flame_animation', self.x - self.image.get_width() / 2, self.y + self.image.get_height() / 2 + 3 * self.size, size=self.size, looping=True, flipped=False, host=self)
            else:
                self.rocket_engine_fire_effect = Effect('rocket_flame_animation', self.x + self.image.get_width(), self.y + self.image.get_height() / 2 + 3 * self.size, size=self.size, looping=True, flipped=True, host=self)
        
        elif self.rocket_type == 3:
            if not self.flipped:
                self.rocket_engine_fire_effect = Effect('rocket_flame_animation', self.x - self.image.get_width() / 2, self.y + self.image.get_height() / 2  * self.size, size=self.size - 1, looping=True, flipped=False, host=self)
            else:
                self.rocket_engine_fire_effect = Effect('rocket_flame_animation', self.x + self.image.get_width(), self.y + self.image.get_height() / 2 * self.size, size=self.size - 1, looping=True, flipped=True, host=self)



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
                self.bullet = Bullet(self.unique_id, self.x + self.image.get_width(), self.y + self.image.get_height() / 2 - 1 * self.size, size=self.size, speed=self.speed, flipped=self.flipped)
                self.active_bullets.append(self.bullet)

            else:
                self.bullet = Bullet(self.unique_id, self.x, self.y + self.image.get_height() / 2 - 1 * self.size, size=self.size, speed=self.speed, flipped=self.flipped)
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
        self.speed = speed * 4
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
        
        # if bullet has hit the game border
        if self.x > WINDOW_X or self.x < 0:
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
    def __init__(self, effect_type, x, y, size=3, cooldown=80, looping=False, loop_with_reverse=False, flipped=True, host=None):
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
        self.flipped = flipped
        self.path = os.listdir('assets/visual/effects/' + str(self.effect_type))
        self.host = host

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

        print("the host of this Effect is", self.host)
        
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

        if self.flipped:
            self.current_image = pygame.transform.rotate(self.current_image, 180)
        
        # check if this effect has a host / source (for example a rocket)
        if self.host != None:
            if not self.host.alive:
                self.kill()

            # position the effect coordinates corresponding to the rocket variant
            if self.host.rocket_type == 0 or self.host.rocket_type == 1:
                if not self.host.flipped:
                    self.x = self.host.x - self.host.image.get_width() / 2 
                    self.y = self.host.y + 1 * self.size
                else:
                    self.x = self.host.x + self.host.image.get_width() - 1 * self.size
                    self.y = self.host.y + 2 * self.size
                
            elif self.host.rocket_type == 2:
                if not self.host.flipped:
                    self.x = self.host.x - self.host.image.get_width() / 2
                    self.y = self.host.y + 4 * self.size
                else:
                    self.x = self.host.x + self.host.image.get_width() - 1 * self.size
                    self.y = self.host.y + 5 * self.size

            elif self.host.rocket_type == 3:
                if not self.host.flipped:
                    self.x = self.host.x - self.host.image.get_width() / 2 + 1 * self.size
                    self.y = self.host.y + 4 * self.size
                else:
                    self.x = self.host.x + self.host.image.get_width()
                    self.y = self.host.y + 5 * self.size

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

def screen_transition_in(new_screen_loop, transition_speed=1, transition_type='horizontal', reverse=False, mode=1):
    if transition_type == 'horizontal':
        # create a "transition element" which
        # will add to the transition effect
        if reverse:
            transition_element = pygame.Rect(WINDOW_X, 0, WINDOW_X, WINDOW_Y)
        else:
            transition_element = pygame.Rect(0 - WINDOW_X, 0, WINDOW_X, WINDOW_Y)

        running = True
        while running:
            clock.tick(FPS)
            # update the transition element each frame
            if reverse:
                transition_element.x -= 20 * transition_speed
            else:
                transition_element.x += 20 * transition_speed

            pygame.draw.rect(WINDOW, BLACK, transition_element)
            # stop running this screen transition loop
            # if certain conditions are met
            if reverse:
                if transition_element.x < 0:
                    running = False
            else:
                if transition_element.x + WINDOW_X >= WINDOW_X:
                    running = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            
            pygame.display.update() # update the display every frame

    elif transition_type == 'fade':
        transition_element = pygame.Surface((1200, 600))
        transition_element.convert()
        transition_element.fill(ORANGE)
        alpha_strength = 0
        running = True
        while running:
            clock.tick(FPS)
            transition_element.fill(BLACK)
            alpha_strength += 1
            transition_element.set_alpha(alpha_strength)

            if alpha_strength >= 100:
                running = False

            WINDOW.blit(transition_element, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            
            pygame.display.update()

    screen_transition_out(new_screen_loop ,transition_element, transition_speed, transition_type, reverse, mode)

def screen_transition_out(new_screen_loop, transition_element, transition_speed=1, transition_type='horizontal', reverse=False, mode=1):
    if transition_type == 'horizontal':
        running = True
        while running:
            clock.tick(FPS)
            if new_screen_loop == menu_screen_loop or new_screen_loop == options_screen_loop:
                WINDOW.fill(MENU_GRAY)
            elif new_screen_loop == game_screen_loop:
                WINDOW.fill(SPACE_BLACK)

            if reverse:
                transition_element.x -= 20 * transition_speed
            else:
                transition_element.x += 20 * transition_speed

            pygame.draw.rect(WINDOW, BLACK, transition_element)
            if reverse:
                if transition_element.x <= 0 - WINDOW_X:
                    running = False

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
            else:
                if transition_element.x >= WINDOW_X:
                    running = False

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

            pygame.display.update() # update the display every frame

    elif transition_type == 'fade':
        alpha_strength = 255

        running = True
        while running:

            if new_screen_loop == menu_screen_loop or new_screen_loop == options_screen_loop:
                WINDOW.fill(MENU_GRAY)
            elif new_screen_loop == game_screen_loop:
                WINDOW.fill(SPACE_BLACK)

            clock.tick(FPS)
            transition_element.fill(BLACK)
            transition_element.set_alpha(alpha_strength)

            alpha_strength -= 5

            if alpha_strength <= 0:
                running = False
            
            WINDOW.blit(transition_element, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            
            pygame.display.update()

    # this is to prevent unexpected keyword argument
    if new_screen_loop == game_screen_loop:
        print("new screen is game screen")
        new_screen_loop(mode)
    else:
        print("new screen")
        new_screen_loop()

def game_screen_loop(mode=1):
    # set / reset game entities (to avoid duplicates)
    rocket_group.empty()
    bullet_group.empty()
    effect_group.empty()
    background_effect_group.empty()
    obstacles_group.empty()
    total_rockets_group.empty()
    total_obstacles_group.empty()

    training_menu_active = False
    pause_menu_active = False

    player = Rocket(200, 400, 1, speed=2, size=3)
    enemy = Rocket(100, 100, 0, 3, 10, 2, flipped=True)

    for each_star in range(40):
        rx = random.randint(10, WINDOW_X - 10)
        ry = random.randint(10, WINDOW_X - 10)
        variant = 'background_star_animation'
        if each_star % 2 == 1: # every odd number will return 1
            variant = 'background_star_animation/blue'
        each_star = BackgroundEffect(variant, rx, ry, size=1, looping=True, loop_with_reverse=True)
    test_tree = Obstacle(1200, 500)

    running = True
    while running:
        clock.tick(FPS)
        WINDOW.fill(SPACE_BLACK)
        background_effect_group.update()
        rocket_group.update()
        bullet_group.update()
        effect_group.update()
        obstacles_group.update()
        player.move()
        enemy.move()

        if training_menu_active:
            # initialize here (code that runs only once every press)
            black_overlay_surface = pygame.Surface((200, WINDOW_Y)).convert()
            black_overlay_surface.fill(GRAY)
            black_overlay_surface.set_alpha(200)


            elements_surface = pygame.Surface((black_overlay_surface.get_width() - 10, black_overlay_surface.get_height() - 10))
            elements_surface.fill(WHITE)
            elements_surface.set_alpha(150)
            pause_text = DEFAULT_FONT.render("Pause menu", 1, BLACK)
            exit_button_text = DEFAULT_FONT.render("Exit game", 1, DARK_RED)
            exit_button = pygame.Rect(elements_surface.get_width() / 2 - 150/2, black_overlay_surface.get_height() - 80, 150, 50)
            pygame.draw.rect(elements_surface, LIGHT_RED, exit_button)
            elements_surface.blit(pause_text, (elements_surface.get_width() / 2 - pause_text.get_width() / 2, exit_button.height / 2))
            elements_surface.blit(exit_button_text, (exit_button.x + pause_text.get_width() / 2 - exit_button_text.get_width() / 2, exit_button.y + pause_text.get_height() / 2))

            # This surface below is blit outside the loop
            # because the surface does not fill itself each frame
            # this is to prevent repeatedly drawing new opacity onto the 
            # original window surface each frame which eventually
            # would end up completely covering the window surface.
            WINDOW.blit(black_overlay_surface, (0, 0))
            WINDOW.blit(elements_surface, (5, 5))

            while training_menu_active:
                clock.tick(FPS)
                mouse_x, mouse_y = pygame.mouse.get_pos()


                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                    if event.type == KEYDOWN:
                        if event.key == K_p:
                            training_menu_active = False

                    if exit_button.collidepoint(mouse_x, mouse_y):
                        exit_button_color = LIGHT_RED
                        if event.type == MOUSEBUTTONUP:
                            if event.button == 1:
                                exit_button_color = WHITE
                                screen_transition_in(menu_screen_loop)

                    else:
                        exit_button_color = GRAY


                pygame.display.update()

        # if game is paused
        if pause_menu_active:
            black_overlay_surface = pygame.Surface((WINDOW_X, WINDOW_Y)).convert()
            black_overlay_surface.fill(BLACK)
            black_overlay_surface.set_alpha(150)
            pause_text = DEFAULT_FONT.render("Pause menu", 1, BLACK)

            elements_surface = pygame.Surface((WINDOW_X/4, WINDOW_Y/4)).convert()
            elements_surface.fill(WHITE)
            exit_button = pygame.Rect(25,125, 100, 20)
            
            WINDOW.blit(black_overlay_surface, (0, 0))

            while pause_menu_active:
                clock.tick(FPS)
                elements_surface.blit(pause_text, (elements_surface.get_width() / 2 - pause_text.get_width() / 2, 10))
                pygame.draw.rect(elements_surface, ORANGE, exit_button)
                WINDOW.blit(elements_surface, (WINDOW_X/2 - elements_surface.get_width() / 2, WINDOW_Y/2))

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                    if event.type == KEYDOWN:
                        if event.key == K_p:
                            pause_menu_active = False

                    if event.type == MOUSEBUTTONUP:
                        if event.button == 1:
                            print("Clicked button!")
                            print(exit_button.x, exit_button.y, pygame.mouse.get_pos())
                            if exit_button.collidepoint(pygame.mouse.get_pos()):
                               print("Clicked button!")
                
                pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

                if event.key == pygame.K_ESCAPE:
                    screen_transition_in(menu_screen_loop)

                if event.key == pygame.K_p:
                    if mode == 0:
                        training_menu_active = True
                        print("Training")
                    elif mode == 1:
                        pause_menu_active = True
                        print("Survival")

                if event.key == pygame.K_SPACE:
                    player.shoot()
                if event.key == pygame.K_RETURN:
                    enemy.shoot()

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

        if keys_pressed[pygame.K_m]:
            rx_vel = random.randint(1, 10)
            r_size = random.randint(1, 3)
            ry = random.randint(40, WINDOW_Y - 40)
            rtype = random.choice([0, 1])

            if rtype == 0:
                obst_type = 'tree'
            elif rtype == 1:
                obst_type = 'stone'

            obst = Obstacle(WINDOW_X + 50, ry, x_vel=rx_vel, size=r_size, object_type=obst_type)

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
                for each_rocket in rocket_group:
                    each_rocket.shoot()

        pygame.display.update() # update the display every frame

def menu_screen_loop(mode=0):
    running = True

    background_surface = pygame.Surface((WINDOW_X, WINDOW_Y)).convert()

    # menu background rockets
    rocket_img1 = pygame.image.load('assets/visual/rockets/rocket_0.png').convert()
    rocket_img1.set_colorkey(WHITE)
    rocket_img1 = pygame.transform.scale(rocket_img1, (rocket_img1.get_width()*10, rocket_img1.get_height()*10 ))
    rocket_img1 = pygame.transform.rotate(rocket_img1, 75)

    rocket_img2 = pygame.image.load('assets/visual/rockets/rocket_3.png').convert()
    rocket_img2.set_colorkey(WHITE)
    rocket_img2 = pygame.transform.scale(rocket_img2, (rocket_img2.get_width()*8, rocket_img2.get_height()*8 ))
    rocket_img2 = pygame.transform.rotate(rocket_img2, -50)

    title_image = pygame.image.load('assets/visual/menu/game_logo2.png').convert()
    start_button = pygame.Rect(400, 500, 150, 50)
    options_button = pygame.Rect(600, 500, 150, 50)
    start_button_text = DEFAULT_FONT.render("Start", 1, BLACK)
    options_button_text = DEFAULT_FONT.render("Options", 1, BLACK)

    
    while running:
        clock.tick(FPS)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        background_surface.fill(WHITE)
        pygame.draw.circle(background_surface, YELLOW, (120, 350), 90)
        pygame.draw.circle(background_surface, ORANGE, (1120, 110), 80)
        background_surface.set_alpha(100)
        background_surface.blit(rocket_img1, (80, 300))
        background_surface.blit(rocket_img2, (1000, 70))
        #background_surface.blit(circle, (70, 300))
        WINDOW.fill(MENU_GRAY)
        WINDOW.blit(background_surface, (0, 0))

        pygame.draw.rect(WINDOW, YELLOW, start_button)
        pygame.draw.rect(WINDOW, YELLOW, options_button)
        WINDOW.blit(title_image, (250, 50) )
        WINDOW.blit(start_button_text, (start_button.x + 80 / 2, start_button.y + 15) )
        WINDOW.blit(options_button_text, (options_button.x + 80 / 2, options_button.y + 15) )


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == MOUSEBUTTONUP:
                if start_button.collidepoint(mouse_x, mouse_y):
                    screen_transition_in(game_screen_loop, transition_type='horizontal', mode=1)

                if options_button.collidepoint(mouse_x, mouse_y):
                    screen_transition_in(options_screen_loop, transition_type='fade')

            if event.type == KEYDOWN:
                if event.key == pygame.K_0:
                    screen_transition_in(game_screen_loop, transition_type='horizontal', mode=0)


        pygame.display.update() # update the display every frame
    
def options_screen_loop(mode=0):
    running = True
    while running:
        clock.tick(FPS)

        WINDOW.fill(MENU_GRAY)

        back_button_text = DEFAULT_FONT.render("Back", 1, BLACK)
        scale_window_button_text = DEFAULT_FONT.render("Scale window size", 1, BLACK)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        back_button = pygame.Rect(400, 500, 150, 50)
        scale_window_button = pygame.Rect(600, 500, 275, 50)

        pygame.draw.rect(WINDOW, YELLOW, back_button)
        pygame.draw.rect(WINDOW, ORANGE, scale_window_button)

        WINDOW.blit(back_button_text, (back_button.x + 80 / 2, back_button.y + 15))
        WINDOW.blit(scale_window_button_text, (scale_window_button.x + 80 / 2, scale_window_button.y + 15))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == MOUSEBUTTONUP:
                if back_button.collidepoint(mouse_x, mouse_y):
                    screen_transition_in(menu_screen_loop, transition_type='fade')
                    
        pygame.display.update() # update the display every frame

screen_transition_in(menu_screen_loop, transition_type='fade')

pygame.quit()
exit()

if __name__ == "__main__":
    run = True
else:
    run = False
