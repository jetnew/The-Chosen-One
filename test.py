import pygame
import sys
from time import sleep
import random

# COLORS
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
purple = (255, 0, 255)

class Env:
    def __init__(self, 
                 game_dims=(1000, 800)):
        
        pygame.init()
        self.play = True
        
        # GAME DIMENSIONS
        self.game_dims = game_dims

        # GRAVITY
        self.gravityPull = 0.5
        self.gravityCurrent = 0
        self.xCurrent = 0

        # JUMPS
        self.jumps = 0
        self.maxJumps = 2

        self.ypos = 100
        self.xpos = 400

        self.touchingObst = 0

        self.startingXPos = [100, 100, 100, 100]
        self.startingYPos = [200, 200, 100, 100]

        self.level1Door = [800, 000, 100, 900]
        self.level = 1
        self.upperLevel = 0
    
    # CONTROL MOVEMENTS
    def execute(self):
        action = None
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    action = 2
                if event.key == pygame.K_LEFT and self.touchingObst == 0:
                    action = 0
                if event.key == pygame.K_RIGHT and self.touchingObst == 0:
                    action = 1
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    quit()
                    action = -1
        return action
    def jump(self):
        if self.jumps < self.maxJumps:
            self.gravityCurrent = -10
            self.jumps = self.jumps + 1
    def left(self):
        if self.touchingObst == 0:
            self.xCurrent = -10
    def right(self):
        if self.touchingObst == 0:
            self.xCurrent = 10
            
    def test_agent(self):
        run = True
        while run:
            sleep(0.001)
            action = self.execute()
            if action == -1:
                break
            self.step(action)

    def step(self, action):
        if action == 0:
            self.left()
        elif action == 1:
            self.right()
        elif action == 2:
            self.jump()
        
        # CONTROL GRAVITY
        self.gravityCurrent = self.gravityCurrent + self.gravityPull

        # RATE OF DECREASE OF LEFT/RIGHT MOVEMENTS
        if self.xCurrent > 0:
            self.xCurrent = self.xCurrent - 0.5
        if self.xCurrent < 0:
            self.xCurrent = self.xCurrent + 0.5

        # UPDATE XY COORDINATES
        self.ypos = self.ypos + self.gravityCurrent
        self.xpos = self.xpos + self.xCurrent

        # BOUNDARIES
        if self.upperLevel == 0:
            if self.xpos > 950:
                self.xpos = 950
            if self.xpos < 000:
                self.xpos = 000
            if self.ypos > 750:
                self.ypos = 751
                self.gravityCurrent = 0
                self.jumps = 0


        gameDisplay = pygame.display.set_mode(self.game_dims, 0, 32)
        gameDisplay.fill(white)
        pygame.draw.rect(gameDisplay, red, (self.xpos, self.ypos, 50, 50))
        pygame.font.init()

        # pygame.draw.rect(gameDisplay, green, level1Door)
        myFont = pygame.font.SysFont('Futura PT Light', 60)
        textsurface = myFont.render('The Chosen One', False, black)
        gameDisplay.blit(textsurface, (200,200))
        pygame.display.update()
        
    def getGameState(self):
        values = [
            self.gravityCurrent,
            self.xCurrent,
            self.jumps,
            self.ypos,
            self.xpos,
            self.touchingObst,
        ]
        return values
    
    def reset(self):
        """Resets the game. Returns (reward, state, done)."""
        self.__init__()
        return (1, self.getGameState(), False)

env = Env()
env.test_game()
