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
BULLET_WIDTH = 20
BULLET_HEIGHT = 10
GRENDADE_SIZE = 10
WEAPON_SIZE = 20

class Entity:
    def __init__(self, name, xy, angle, speed, height, width, game_dims=(1000,800)):
        self.name = name
        self.x, self.y = xy
        self.height = height
        self.width = width
        self.speed = speed
        self.dimx, self.dimy = game_dims

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

        exit_boundary = self.x > self.dimx-50 or self.x < 000 or self.y > self.dimy-50 or self.y < 0

        return has_hit_x and has_hit_y or exit_boundary
    def __repr__(self):
        return self.name + str((self.x,self.y))


class Agent:
    def __init__(self, xy=(400,100), game_dims=(1000,800), show=False):
        self.jumps = 0
        self.maxJumps = 2
        self.xpos, self.ypos = xy
        self.gravityPull = 0.5
        self.gravityCurrent = 0
        self.xCurrent = 0
        self.touchingObst = 0
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
        if agent_action == 0:
            self.left()
        elif agent_action == 1:
            self.right()
        elif agent_action == 2:
            self.jump()
        self.update()

class Env:
    def __init__(self, game_dims=(1000, 800),show=False):
        self.agent = Agent((400,100), show=show, game_dims=game_dims)
        self.dimx, self.dimy = game_dims
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
        self.entity_limit = 5
        self.entity_free_keys = [0,1,2,3,4]
        self.entity_dict = {}
    def get_free_key(self):
        if len(self.entity_free_keys) > 0:
            return self.entity_free_keys.pop(0)
        else:
            return None
    
    # CONTROL MOVEMENTS
    Mouse_x = -200
    Mouse_y = -200
    MMouse_x = -200
    MMouse_y = -200
    bullet_quantity = 0
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
                if event.key == pygame.K_ESCAPE:
                    agent_action = -1
            if event.type == pygame.QUIT:
                pygame.display.quit()
                quit()
                agent_action = -1
            if event.type == pygame.MOUSEMOTION:
                self.MMouse_x, self.MMouse_y = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.Mouse_x, self.Mouse_y = pygame.mouse.get_pos()
                print('mouse finally down')
            elif event.type == pygame.MOUSEBUTTONUP:
                MyClock = pygame.time.Clock()
                MyClock.tick(60)
                print('mouse finally up')
                self.bullet_quantity += 1
                print(self.bullet_quantity)
            
        action = (agent_action, weapon_action)

        return action


    def create_entity(self, weapon_action):
        wep_type, wep_xy, angle = weapon_action
        
        if self.delay != 0:
            self.delay -= 1
        wep_type = 1
        if wep_type == 1 and self.delay == 0:
            ent = Entity(wep_type, wep_xy, angle, 10, BULLET_HEIGHT, BULLET_WIDTH)
            ent_key = self.get_free_key()
            if ent_key != None:
                self.entity_dict[ent_key] = ent
            # self.entity_list.append(ent)
            self.delay = 20
        if wep_type == 2 and self.delay == 0:
            ent = Entity(wep_type, wep_xy, random.randint(5,12), random.randint(5,50), GRENDADE_SIZE, GRENDADE_SIZE)
            self.entity_list.append(ent)
            self.delay = 20
    def update_entities(self):
        # UPDATE ENTITIES
        collided = []
        for key, ent in self.entity_dict.items():
            collide = ent.update((self.agent.xpos, self.agent.ypos))
            if not collide:
                if self.show:
                    pygame.draw.rect(self.gameDisplay, blue, (ent.x, ent.y, ent.width, ent.height))
            else:
                self.agent.agent_reward = -20
                self.generator_reward = 20
                collided.append(key)
        for ent_key in collided:
            self.entity_free_keys.append(ent_key)
            del self.entity_dict[ent_key]
    def display_game(self):
        if self.show:
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
    global bullet_entity
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
        
        bullet_entity = self.create_gun(self.Mouse_x, self.Mouse_y, self.agent.xpos) #create gun on click
        
        if self.bullet_quantity > 0:
            # CREATE WEAPON ENTITY
            self.create_entity(bullet_entity)
            self.bullet_quantity -= 0.2
        
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
        
    def create_gun(self, x , y, nX):
        def rot_center(image, angle):
            """rotate an image while keeping its center and size"""
            orig_rect = image.get_rect()
            rot_image = pygame.transform.rotate(image, angle)
            rot_rect = orig_rect.copy()
            rot_rect.center = rot_image.get_rect().center
            rot_image = rot_image.subsurface(rot_rect).copy()
            return rot_image

        gun = pygame.image.load('assets/assaultrifle2.png')
        gunRect = gun.get_size()
        gunScaled = pygame.transform.scale(gun, (180 , 180))
        imagePosX = x - (gunRect[0]/2) + 0
        if(nX > imagePosX):
            imagePosX += 181
        imagePosY = y - (gunRect[1]/2) + 90
        scaleBy = 1
        dx = imagePosX - self.MMouse_x + 90
        dy = imagePosY - self.MMouse_y + 90
        rads = math.atan2(-dy,dx)
        degs = math.degrees(rads)
        #gunScaled = pygame.transform.rotozoom(gunScaled, degs , scaleBy)
        rot_img = rot_center(gunScaled, degs)
        if self.show:
            self.gameDisplay.blit(rot_img, (imagePosX, imagePosY)) #create image and center on mouse click
        #pygame.display.update()
        return (1, (imagePosX + 90,imagePosY+90), -degs)
    
    def reset(self):
        """Resets the game. Returns (reward, state, done)."""
        self.__init__(game_dims=self.game_dims, show=self.show)
        return self.getGameState()
    
    def test_step(self):
        run = True
        while run:
            sleep(0.001)

            # Create Gun at random place and angles
            #agent_action = random.randint(0,2)
            agent_action = self.execute()
            if agent_action == -1:
                break
            wep_type = random.randint(0,2)
            wep_xy = (50, 700)
            wep_x, wep_y = wep_xy
            angle = 0
            generator_action = (wep_type, wep_x, wep_y, angle)
            action = (agent_action, generator_action)
            self.step(action)

env = Env(show=True)
env.test_step()
