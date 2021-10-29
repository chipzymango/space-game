import pygame
from config import *
from loops import game_screen_loop, menu_screen_loop, options_screen_loop

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