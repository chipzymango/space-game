import pygame
from config import *
from groups import *

# we use this class to add rockets
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
            print("The rocket died.")

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

        print("New rocket hasbeen created")

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

        movement(self)

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
            print("Rocket " + str(self.unique_id) + " is already dead")

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

class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=LIGHT_YELLOW, text="", border_thickness=1, border_color=BLACK):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.width = width
        self.color = color
        self.default_color = color
        self.height = height
        self.text = text
        self.border_thickness = border_thickness
        self.border_color = border_color

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.inner_rect = pygame.Rect(self.rect.x + self.border_thickness, self.rect.y + self.border_thickness, self.width - (border_thickness * 2) , self.height - (border_thickness * 2) )

        if bool(self.text): # in Python, empty string means False in boolean
            self.rendered_text = DEFAULT_FONT.render(self.text, 1, BLACK)
            self.rendered_text_width = self.rendered_text.get_width()
            self.rendered_text_height = self.rendered_text.get_height()

    def move(self):
        keys_pressed = pygame.key.get_pressed()
    
        if keys_pressed[pygame.K_RIGHT] and self.x + self.image.get_width() < WINDOW_X:
            self.moving_right = True
        else:
            self.moving_right = False

        if keys_pressed[pygame.K_LEFT] and self.x > 0:
            self.moving_left = True
        else:
            self.moving_left = False

        if keys_pressed[pygame.K_DOWN] and self.y + self.image.get_height() < WINDOW_Y:
            self.moving_down = True
        else:
            self.moving_down = False

        if keys_pressed[pygame.K_UP] and self.y > 0:
            self.moving_up = True
        else:
            self.moving_up = False

    def update(self):
        pygame.draw.rect(WINDOW, self.border_color, self.rect)
        pygame.draw.rect(WINDOW, self.color, self.inner_rect)

        # if there is text, draw it
        if self.text:
            self.rendered_text = DEFAULT_FONT.render(self.text, 1, BLACK)
            WINDOW.blit(self.rendered_text, (self.x + self.rendered_text_width / 2, self.y + self.rendered_text_height / 2))

        for each_mouse in mouse_cursor_group:
            if self.rect.collidepoint((each_mouse.x, each_mouse.y)):
                self.color = YELLOW
            else:
                self.color = self.default_color

        #if self.mo

class MouseCursor(pygame.sprite.Sprite):
    def __init__(self, start_x=WINDOW_X/2, start_y=WINDOW_Y/2, size=1, visibility=True):
        pygame.sprite.Sprite.__init__(self)
        self.x = start_x
        self.y = start_y
        self.size = size + 1
        self.image = pygame.image.load('assets/visual/menu/mouse.png')
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.size, self.image.get_height() * self.size) )
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        mouse_cursor_group.add(self)
        self.visibility = visibility

    def update(self):
        if self.visibility:
            self.x, self.y = pygame.mouse.get_pos()
            pygame.mouse.set_visible(False)
            WINDOW.blit(self.image, (self.x, self.y))
        else:
            pygame.mouse.set_visible(True)

def movement(self):
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

from fonts import *
from sounds import *
from loops import *