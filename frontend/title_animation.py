
import pygame
import os
import random
import time
from setup import *

setup = Setup()

pygame.init()
Screen_height = setup.get("Screen_height")

Screen_width = setup.get("Screen_width")

game_folder = os.path.dirname(__file__)
path_folder = os.path.join(game_folder,"stars")
from setup import *


class Star(pygame.sprite.Sprite):
    
    def __init__(self,x,y, speed, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image.convert()
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


        
    def update(self): 
        
        #self.rect.x = self.rect.x+self.speed
        self.rect.y = self.rect.y + self.speed
        if self.rect.y >Screen_width:
               self.rect.y = 0
               self.rect.x = random.randint(0, Screen_width)
                
# creates n_o_stars stasprites
# with random positions, random images and random speeds
# returns a spritegroup
            
def create_stars(n_o_stars):
    return_group = pygame.sprite.Group()
                    
    for i in range (0, n_o_stars):
        
        nr = random.randint(1,setup.get("number_of_starsprites"))
        st = str(nr) +".png"
      
        spr_image = pygame.image.load(os.path.join(path_folder, st))
        
        x_pos = random.randint(0, Screen_width)
        y_pos = random.randint(0, Screen_height)
       
      
        speed = random.randint(setup.get("stars_min_speed"),setup.get("stars_max_speed"))
        
        spr = Star(x_pos, y_pos, speed, spr_image)
                   
        return_group.add(spr)
        
    

    return return_group
