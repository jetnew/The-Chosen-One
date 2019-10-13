import pygame
import sys
from time import sleep
import random
import math
import numpy as np
from gym import spaces

# COLORS
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
purple = (255, 0, 255)

# SIZES
AGENT_SIZE = 50
WEAPON_SIZE = 20

class Entity:
    def __init__(self, name, xy, angle, speed, game_dims=(1000,800)):
        self.name = name
        self.x, self.y = xy
        self.speed = speed
        self.angle = math.radians(-angle)  # -1 to 1 
        self.dx = self.speed * math.cos(self.angle)
        self.dy = self.speed * math.sin(self.angle)
        self.dimx, self.dimy = game_dims
        
    def update(self, agent_xy):
        self.x += self.dx
        self.y += self.dy

        agent_x, agent_y = agent_xy

        has_hit_x = self.x >= agent_x - WEAPON_SIZE and self.x <= agent_x + AGENT_SIZE
        has_hit_y = self.y >= agent_y - WEAPON_SIZE and self.y <= agent_y + AGENT_SIZE
        
        exit_boundary = self.x > self.dimx-50 or self.x < 000 or self.y > self.dimy-50 or self.y < 0

        return has_hit_x and has_hit_y or exit_boundary
    
    def __repr__(self):
        return self.name + str((self.x,self.y))


class Agent:
    def __init__(self, xy=(400,100), game_dims=(1000,800), show=False):
        self.jumps = 0
        self.maxJumps = 2
        self.xpos, self.ypos = xy
        self.touchingObst = 0
        self.gravityPull = 0.5
        self.gravityCurrent = 0
        self.xCurrent = 0
        self.show = show
        self.dimx, self.dimy = game_dims
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
        if self.xpos > self.dimx-50:
            self.xpos = self.dimx-50
        if self.xpos < 000:
            self.xpos = 000
        if self.ypos > self.dimy-50:
            self.ypos = self.dimy-50+1
            self.gravityCurrent = 0
            self.jumps = 0
            
    def display(self, gameDisplay):
        if self.show:
            pygame.draw.rect(gameDisplay, red, (self.xpos, self.ypos, AGENT_SIZE, AGENT_SIZE))
    def act(self, agent_action):
        # print(agent_action)
        if agent_action == 0:
            self.left()
        elif agent_action == 1:
            self.right()
        elif agent_action == 2:
            self.jump()
        self.update()
            

class Env:
    def __init__(self, 
                 game_dims=(1000, 800),
                 show=False):
        self.dimx, self.dimy = game_dims
        self.agent = Agent((400,100), show=show, game_dims=game_dims)
        self.set_default_rewards()
        self.observation_space = 5
        self.show = show
        pygame.init()
        self.play = True
        
        # GAME DIMENSIONS
        self.game_dims = game_dims
        self.generator_action_space = spaces.Box(np.array([0,0,0,0]), np.array([2,self.dimx,self.dimy,360]), dtype=np.float32)
        self.agent_action_space = spaces.Discrete(3)
        min_obs = np.array([0]*5 + [0,0,5,0]*5)
        max_obs = np.array([2,self.dimx,self.dimy,1,self.dimy*2] + [self.dimx,self.dimy,50,360]*5)
        self.observation_space = spaces.Box(min_obs, max_obs, dtype=np.float32)
        
        # DELAY FOR WEAPON ENTITIES
        self.delay = 0
#         self.entity_list = []
        
        self.entity_limit = 5
        self.entity_free_keys = [0,1,2,3,4]
        self.entity_dict = {}
    def get_free_key(self):
        if len(self.entity_free_keys) > 0:
            return self.entity_free_keys.pop(0)
        else:
            return None
    
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
        # print(weapon_action)
        wep_type, wep_x, wep_y, angle = weapon_action
        wep_xy = (wep_x, wep_y)
#         print(wep_xy)
        if self.delay != 0:
            self.delay -= 1
#         wep_type = 1
        if wep_type == 1 and self.delay == 0:
            ent = Entity(str(wep_type), wep_xy, angle, 10)
            ent_key = self.get_free_key()
            if ent_key != None:
                self.entity_dict[ent_key] = ent
            self.delay = 20  # DELAY BEFORE THE NEXT ATTACK
    def update_entities(self):
        # UPDATE ENTITIES
        collided = []
        for key, ent in self.entity_dict.items():
            collide = ent.update((self.agent.xpos, self.agent.ypos))
            if not collide:
                if self.show:
#                     print(ent.x, ent.y)
                    pygame.draw.rect(self.gameDisplay, blue, (ent.x, ent.y, WEAPON_SIZE, WEAPON_SIZE))
            else:
                self.agent.agent_reward = -20
                self.generator_reward = 20
                collided.append(key)
        
        for ent_key in collided:
            self.entity_free_keys.append(ent_key)
            del self.entity_dict[ent_key]
    def display_game(self):
        if self.show:
#             print(self.game_dims)
            self.gameDisplay = pygame.display.set_mode(self.game_dims, 0, 32)
            self.gameDisplay.fill(white)
    def display_background(self):
        # DISPLAY BACKGROUND
        if self.show:
            pygame.font.init()
            myFont = pygame.font.SysFont('Futura PT Light', 60)
            textsurface = myFont.render('The Chosen One', False, black)
            self.gameDisplay.blit(textsurface, (200,200))
            pygame.display.update()
    def set_default_rewards(self):
        self.agent.agent_reward = 1
        self.generator_reward = -1

    def step(self, action):
        # SET DEFAULT REWARDS FOR AGENT AND GENERATOR
        self.set_default_rewards()
        
        # DISPLAY GAME
        self.display_game()
        
        agent_action, weapon_action = action
        
        # MOVE THE AGENT
        self.agent.act(agent_action)
        if self.show:
            self.agent.display(self.gameDisplay)
        
        # CREATE WEAPON ENTITY
        self.create_entity(weapon_action)
        
        # UPDATE ENTITIES
        self.update_entities()
        
        # DISPLAY BACKGROUND
        self.display_background()
        
        """RETURNS:
        reward - (agent_reward, generator_reward)
        state - getGameState()
        done - CURRENT: DEFAULT: False
        done - TODO: whether game is completed, e.g. HP <= 0
        """
        reward = (self.agent.agent_reward, self.generator_reward)
        state = self.getGameState()
        
        return (reward, state, False)
        
    def getGameState(self):
        a = self.agent
        agent_values = np.array([
            a.jumps,
            a.xpos//1000,
            a.ypos//1000,
            a.touchingObst,
            a.gravityCurrent,
            # TODO: height, width, dy, dx, direction, bounding box
        ])
        entity_values = np.array([])
        for i in range(5):
            if i in self.entity_dict:
                e = self.entity_dict[i]
                vals = [e.x//1000, e.y//1000, e.speed, e.angle]
            else:
                vals = [0,0,0,0]
            entity_values = np.append(entity_values, vals)

        values = np.append(agent_values, entity_values)
        return values
    
    def reset(self):
        """Resets the game. Returns (reward, state, done)."""
        self.__init__(game_dims=self.game_dims, show=self.show)
        return self.getGameState()

    def test_step(self):
        # Create Gun at random place and angles
        agent_action = random.randint(0,2)

        wep_type = 1  # gun
        wep_xy = (50, 700)  # coordinate appears at
        angle = 0

        generator_action = (wep_type, wep_xy, angle)
        action = (agent_action, generator_action)
        self.step(action)
