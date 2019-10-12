import pygame
import sys
from time import sleep

pygame.init()

play = True

# GAME DIMENSIONS
game_dims = (1000, 800)

# COLORS
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
purple = (255, 0, 255)

# GRAVITY
gravityPull = 0.5
gravityCurrent = 0
xCurrent = 0

# JUMPS
jumps = 0
maxJumps = 2

ypos = 100
xpos = 400

touchingObst = 0

startingXPos = [100, 100, 100, 100]
startingYPos = [200, 200, 100, 100]

level1Door = [800, 000, 100, 900]

level = 1

upperLevel = 0

while True:
    # CONTROL MOVEMENTS
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if jumps < maxJumps:
                    gravityCurrent = -10
                    jumps = jumps + 1
            if event.key == pygame.K_LEFT and touchingObst == 0:
                xCurrent = -10
            if event.key == pygame.K_RIGHT and touchingObst == 0:
                xCurrent = 10
        if event.type == pygame.QUIT:
            pygame.display.quit()
            quit()
            
    # CONTROL GRAVITY
    gravityCurrent = gravityCurrent + gravityPull
    
    # RATE OF DECREASE OF LEFT/RIGHT MOVEMENTS
    if xCurrent > 0:
        xCurrent = xCurrent - 0.5
    if xCurrent < 0:
        xCurrent = xCurrent + 0.5
        
    # UPDATE XY COORDINATES
    ypos = ypos + gravityCurrent
    xpos = xpos + xCurrent
    
    # BOUNDARIES
    if upperLevel == 0:
        if xpos > 950:
            xpos = 950
        if xpos < 000:
            xpos = 000
        if ypos > 750:
            ypos = 751
            gravityCurrent = 0
            jumps = 0


    gameDisplay = pygame.display.set_mode(game_dims, 0, 32)
    gameDisplay.fill(white)
    pygame.draw.rect(gameDisplay, red, (xpos, ypos, 50, 50))
    pygame.font.init()
    
    if level == 1:
#         pygame.draw.rect(gameDisplay, green, level1Door)
        myFont = pygame.font.SysFont('Futura PT Light', 60)
        textsurface = myFont.render('The Chosen One', False, black)
        gameDisplay.blit(textsurface, (200,200))
    pygame.display.update()
    sleep(0.01)