import pygame
import os
import time
import math
from setup import*

setup = Setup()
pygame.init()
Screen_height = setup.get("Screen_height")
Screen_width = setup.get("Screen_width")

size = Screen_width, Screen_height
screen = pygame.display.set_mode(size)
game_folder = os.path.dirname(__file__)
path_folder = os.path.join(game_folder,"alphabet")


class Letter(pygame.sprite.Sprite):
    
    def __init__(self,x,y, image,sin_counter,jumping, speed,size):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.sincounter = sin_counter
        self.jumping = jumping
        self.speed = speed
    
    def update(self):

        if self.jumping:
            self.rect.x = self.rect.x  - self.speed
            add =  3*math.sin( (self.sincounter* (2*math.pi)/10)  /10   )
            self.rect.y = self.rect.y + add + 0.5        
            self.sincounter +=1
            if self.rect.x < -40:
                self.rect.x = Screen_width + 10
            
        else:
            self.rect.x = self.rect.x - self.speed
            if self.rect.x < -1500:
                self.rect.x = Screen_width + 10
            
def make_scroll(text,y_pos, jumping, speed, size):
            return_group  = pygame.sprite.Group()
            space = 0 
            for i in range (0, len(text)-1):

                letter = text[i]
                if speed == 0:
                    x = Screen_width/2 -7*size +(size+1)*i
                else:
                    x = Screen_width +(size+1)*i
                y = y_pos  
                
                if letter != ' ':
                    file_name = str(letter) + ".png"
                else:
                    file_name ="space.png"
                
                im = pygame.image.load(os.path.join(path_folder, file_name))
                
                sprite = Letter(x+space,y, im, i, jumping, speed, size) 
                return_group.add(sprite)
                
            return return_group

