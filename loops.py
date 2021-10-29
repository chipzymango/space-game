import pygame

from config import *

from classes import Rocket, Bullet, Effect, BackgroundEffect, Obstacle, Button, MouseCursor
from groups import *
from sounds import *
from fonts import *

#print(Rocket)
def game_screen_loop(mode=1):
    from transitions import screen_transition_in, screen_transition_out
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

            mouse_active = True

            while training_menu_active:
                clock.tick(FPS)

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
        else:
            mouse_active = False

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

            mouse_active = False

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

        else:
            mouse_active = False

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
    from transitions import screen_transition_in, screen_transition_out
    from config import menu_mouse_cursor

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

    title_image = pygame.image.load('assets/visual/menu/game_logo3.png').convert()
    start_button = Button(400, 500, 150, 50, LIGHT_YELLOW, text="Button1")
    options_button = Button(600, 500, 150, 50, RED, text="Button2")

    while running:
        clock.tick(FPS)
        background_surface.fill(WHITE)

        pygame.draw.circle(background_surface, YELLOW, (120, 350), 90)
        pygame.draw.circle(background_surface, ORANGE, (1120, 110), 80)
        background_surface.set_alpha(100)
        background_surface.blit(rocket_img1, (80, 300))
        background_surface.blit(rocket_img2, (1000, 70))

        WINDOW.fill(MENU_GRAY)
        WINDOW.blit(background_surface, (0, 0))
        WINDOW.blit(title_image, (250, 50) )
        
        start_button.update()
        options_button.update()

        # update the mouse image
        mouse_cursor_group.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == MOUSEBUTTONDOWN:
                if event.button == pygame.K_0:
                    screen_transition_in(game_screen_loop, transition_type='horizontal', mode=0)


            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                
                    #screen_transition_in(menu_screen_loop)
                    if start_button.rect.collidepoint(menu_mouse_cursor.x, menu_mouse_cursor.y):
                        screen_transition_in(game_screen_loop, transition_type='horizontal', mode=1)##

                    if options_button.rect.collidepoint(menu_mouse_cursor.x, menu_mouse_cursor.y):
                        screen_transition_in(options_screen_loop, transition_type='fade')##


        pygame.display.update() # update the display every frame
    
def options_screen_loop(mode=0):
    from transitions import screen_transition_in, screen_transition_out
    from config import menu_mouse_cursor

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

        mouse_cursor_group.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == MOUSEBUTTONUP:
                if back_button.collidepoint(mouse_x, mouse_y):
                    screen_transition_in(menu_screen_loop, transition_type='fade')
                    
        pygame.display.update() # update the display every frame


