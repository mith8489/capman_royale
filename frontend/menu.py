import pygame
import os
import time
import math
from setup import *

game_folder = os.path.dirname (__file__)
spr_folder = os.path.join(game_folder,"menu_items")
pygame.init()

#The pointer - scales to 32*32
# _image = sprite image
# _step = distance while stepping up/down
# _no_steps = number of menu choices
# _anime = needed in animation
# sefl_sin_counter = needed in animation
class Menu_pointer(pygame.sprite.Sprite):
    
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image.convert()
        self.image = pygame.transform.scale(self.image, (setup.get("menu_pointer_size"), setup.get("menu_pointer_size")))
        self.rect= self.image.get_rect()
        self.image.set_colorkey((0,0,0))
        self._step = 0
        self._n_o_steps = 0
        
        self._anime_add = 0
        self._sin_counter = 0
        
        
        #sets step_size and number of steps. 
    def _set_step(self,step_size,n_o_steps):
        self._step = step_size
        self._n_o_steps = n_o_steps
        
        #x,y coordcoinates
    def _place(self,x,y):
            self.rect.x = x
            self.rect.y = y+15 
            self._anime_add = 0
         #moving down   
    def step_down(self,y):
        self._place( self.rect.x,y+15)
        self._get_anime_add = 0
         #moving up       
    def _step_up(self,y ):
        self._place( self.rect.x, y+15 )
        self._anime_add = 0

        #counts_sin value for animation
    def _update_add(self):
        self._anime_add = setup.get("menu_pointer_amplitude")*math.sin(self._sin_counter/setup.get("menu_pointer_period"))
        self._sin_counter = self._sin_counter +0.5
        if self._sin_counter > 1000:
            self._sin_counter = 0
        
#MenuItems

#Inits the menu -sprites
# image = sprite image
# func = function to call when chosen
class Menu_item (pygame.sprite.Sprite):
    def __init__(self,image, func):
        
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect= self.image.get_rect()
        self._func = func
       
        #x,y coordinates
    def _place(self,x,y):
            self.rect.x = x
            self.rect.y = y

#menuClass
#Makes a menu out of a menuObject

class Menu():
    #Creates the spriteGroup
    #of menu-items.
    def _make_group(self, menu_settings, x, y):
        try:
            return_group = pygame.sprite.Group()
            j = 0
            l = len(menu_settings)-1
            setup = menu_settings[0]
            top_x = setup["top_position"]
            distance = setup["distance"]
            for i in range (1, len(menu_settings)):
                tupel = (im, func) = menu_settings[i]
                image = pygame.image.load(os.path.join(spr_folder, im))
                convert_value = eval(self._global_setup.get("menu_block"))
                
                image = pygame.transform.scale(image,(convert_value))
                sprite = Menu_item(image, func)
                sprite._place(x/2, top_x+j*distance)
                self._pointer_y.append(top_x+j*distance)
                self._functions.append(func)
                j+=1
                return_group.add(sprite)
        except Exception, e:
            print ("Can't find file")
            print (e)
            quit()
        
        return return_group

    
    #Creates the pointer_group
    #image = given image
    #x,y = coordinates
    # n_o_choices  = the number of options in the menu
    def _make_pointer(self,image,x,y,n_o_choices):
        try:
            pointerimage = pygame.image.load(os.path.join(spr_folder, image))
            pointer_group = pygame.sprite.Group()
            p_left =  Menu_pointer(pointerimage)
            p_right = Menu_pointer(pointerimage)
        except Exception, e:
            print ("Can't find file")
            print(e)
            quit()
        p_left._place(x/2-(self._global_setup.get("menu_pointer_size")), self._pointer_y[self._pointer_pos] )
        p_right._place(x/2+(self._global_setup.get("menu_block_xsize")),self._pointer_y[self._pointer_pos] )
        pointer_group.add(p_left)
        pointer_group.add(p_right)
        return pointer_group
    #init Menu
    #takes a menu_setting and parses it to a working menu:
    
    def __init__(self, menu_settings):
        self._pointer_y = []
        self._functions = []
        self._active = True
        self._visible = True
        self._pointer_pos = 0
        self._setup = menu_settings[0]
        self._global_setup = setup
        self._top_y = self._setup["screen_height"]
        self._top_x = self._setup["screen_width"]
        self._menu_group = self._make_group(menu_settings, self._top_x, self._top_y)
        self._pointer_group = self._make_pointer(self._setup["pointer"],self._top_x, self._top_y+ self._setup["distance"]+15  , len(self._menu_group))
        self.timer = 0
        

        self._up = self._global_setup.get("up_key")
                
    def _switch_off (self) :

        self._visible = False
        self._active = False
        
    def _switch_on(self):
        self._visible =True
        self._active = True

    
    def _activate (self):
        self._active = True
    def _deactivate (self):
        self._active = False
        
     #shows the menu in the given screen            
    def _show(self,screen):
        if self._visible:
            self._menu_group.draw(screen)
            for spr in self._pointer_group:
                spr.rect.y += spr._anime_add
            self._pointer_group.draw(screen)
            for spr in self._pointer_group:
                spr.rect.y -= spr._anime_add-1 ##WTF!
                spr._update_add()

        #moves the cursor one step down
    def _move_cursor_down(self):
        if self._pointer_pos == len(self._pointer_y)-1:
            return
        else:
            self._pointer_pos +=1
            
            for spr in self._pointer_group:
                spr.step_down(self._pointer_y[self._pointer_pos])
        #move the cursor one step up.
    def _move_cursor_up(self):
         
         if self._pointer_pos == 0:
            return
         else:
            self._pointer_pos -=1
            for spr in self._pointer_group:
                spr._step_up(self._pointer_y[self._pointer_pos])
            #runs the function pointed at
    def _run_function(self):
        function =  self._functions[self._pointer_pos]
        function()
        #checks for keys.
        #timer = speed 
    def _check_Move(self ,event):
            if event.type == pygame.KEYDOWN:
                if self._active:
                    
                    if  event.key == eval(self._global_setup.get("up_key")):
                        self._move_cursor_up()
                    
                    if  event.key==  eval(self._global_setup.get("down_key")):
                        
                        self._move_cursor_down()
           
                    if event.key ==  eval(self._global_setup.get("menu_action_key")):
                        self._run_function()
          
                
