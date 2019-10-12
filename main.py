import pygame
import sys
from time import sleep
import random
import math

# COLORS
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
purple = (255, 0, 255)

# SIZES
AGENT_SIZE = 50
BULLET_WIDTH = 20
BULLET_HEIGHT = 10
GRENDADE_SIZE = 10

class Entity:
    def __init__(self, name, xy, angle, speed, height, width):
        self.name = name
        self.x, self.y = xy
        self.height = height
        self.width = width
        self.speed = speed

        if name == 1:
            self.angle = math.radians(angle)  # -1 to 1 
            self.dx = self.speed * math.cos(self.angle)
            self.dy = self.speed * math.sin(self.angle)
            self.counter = 0
        elif name == 2:
            self.angle = angle
            self.counter = 12
        
    def update(self, agent_xy):
        if self.name == 1:
            self.x += self.dx
            self.y += self.dy
        elif self.name == 2:
            if self.counter >= 2:
                self.x += self.speed
                self.y -= (self.angle * abs(self.angle)) * 1
                self.angle -= 1
                self.counter -= 1
            elif self.counter >= 0:
                self.x -= 4
                self.y -= 4
                self.height += 8
                self.width += 8
                self.counter -= 1
            else:
                self.x = -100
                self.y = -100

        agent_x, agent_y = agent_xy

        has_hit_x = self.x >= agent_x - self.width and self.x <= agent_x + AGENT_SIZE
        has_hit_y = self.y >= agent_y - self.height and self.y <= agent_y + AGENT_SIZE

        return has_hit_x and has_hit_y
    def __repr__(self):
        return self.name + str((self.x,self.y))


class Agent:
    def __init__(self, xy=(400,100)):
        self.jumps = 0
        self.maxJumps = 2
        self.xpos, self.ypos = xy
        self.touchingObst = 0
        self.gravityPull = 0.5
        self.gravityCurrent = 0
        self.xCurrent = 0
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
    def update(self):
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
        if self.xpos > 950:
            self.xpos = 950
        if self.xpos < 000:
            self.xpos = 000
        if self.ypos > 750:
            self.ypos = 751
            self.gravityCurrent = 0
            self.jumps = 0
            
    def display(self, gameDisplay):
        self.update()
        pygame.draw.rect(gameDisplay, red, (self.xpos, self.ypos, AGENT_SIZE, AGENT_SIZE))
    def act(self, agent_action):
        if agent_action == 0:
            self.left()
        elif agent_action == 1:
            self.right()
        elif agent_action == 2:
            self.jump()
            

class Env:
    def __init__(self, game_dims=(1000, 800)):
        self.agent = Agent((400,100))
        
        pygame.init()
        self.play = True
        
        # GAME DIMENSIONS
        self.game_dims = game_dims
        
        # DELAY FOR WEAPON ENTITIES
        self.delay = 0
        self.entity_list = []
    
    # CONTROL MOVEMENTS
    def execute(self):
        agent_action = None
        weapon_action = (0,0,0)
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    agent_action = 2
                if event.key == pygame.K_LEFT and self.agent.touchingObst == 0:
                    agent_action = 0
                if event.key == pygame.K_RIGHT and self.agent.touchingObst == 0:
                    agent_action = 1
            if event.type == pygame.QUIT:
                pygame.display.quit()
                agent_action = -1
                
        action = (agent_action, weapon_action)
        return action
            
    def test_agent(self):
        """FOR TESTING OF AGENT ACTIONS ONLY"""
        run = True
        while run:
            sleep(0.01)
            action = self.execute()
            if action == -1:
                break
            self.step(action)
            
    def create_entity(self, weapon_action):
        wep_type, wep_xy, angle = weapon_action
        if self.delay != 0:
            self.delay -= 1
        if wep_type == 1 and self.delay == 0:
            ent = Entity(wep_type, wep_xy, angle, 10, BULLET_HEIGHT, BULLET_WIDTH)
            self.entity_list.append(ent)
            self.delay = 20
        if wep_type == 2 and self.delay == 0:
            ent = Entity(wep_type, wep_xy, random.randint(5,12), random.randint(5,50), GRENDADE_SIZE, GRENDADE_SIZE)
            self.entity_list.append(ent)
            self.delay = 20
    def update_entities(self):
        # UPDATE ENTITIES
        collided = []
        for ent in self.entity_list:
            collide = ent.update((self.agent.xpos, self.agent.ypos))
            if not collide:
                pygame.draw.rect(self.gameDisplay, blue, (ent.x, ent.y, ent.width, ent.height))
            else:
                collided.append(ent)
        for ent in collided:
            self.entity_list.remove(ent)
    def display_game(self):
        self.gameDisplay = pygame.display.set_mode(self.game_dims, 0, 32)
        self.gameDisplay.fill(white)
    def display_background(self):
        # DISPLAY BACKGROUND
        pygame.font.init()
        myFont = pygame.font.SysFont('Futura PT Light', 60)
        textsurface = myFont.render('The Chosen One', False, black)
        self.gameDisplay.blit(textsurface, (200,200))
        pygame.display.update()

    def step(self, action):
        # DISPLAY GAME
        self.display_game()
        
        agent_action, weapon_action = action
        
        # MOVE THE AGENT
        self.agent.act(agent_action)
        self.agent.display(self.gameDisplay)
        
        # CREATE WEAPON ENTITY
        self.create_entity(weapon_action)
        
        # UPDATE ENTITIES
        self.update_entities()            
        
        # DISPLAY BACKGROUND
        self.display_background()
        
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

    def test_step(self):
        # Create Gun at random place and angles
        agent_action = random.randint(0,2)

        wep_type = agent_action
        wep_xy = (50, 700)
        angle = 0

        generator_action = (wep_type, wep_xy, angle)
        action = (agent_action, generator_action)
        self.step(action)

env = Env()

for i in range(1000):
    env.test_step()