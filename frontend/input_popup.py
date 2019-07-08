import pygame
import time
from setup import *
pygame.init()

Screen_height = setup.get("Screen_height")
Screen_width = setup.get("Screen_width")
screen = pygame.display.set_mode((Screen_width, Screen_height))
font = pygame.font.Font(setup.get ("input_font") , setup.get("input_font_size"))
#the input field. 
class Input_window():
    def __init__(self):
       
         self._font = pygame.font.Font(setup.get ("input_font") , setup.get("input_font_size"))
         self._name_input_field = pygame.Rect(312, 359, 400, 50)
     
         self._name_text = ""
         self._enabled = False
         
    def enable(self):
        self._enabled = True
        
    def disable(self) :
        self._enabled = False
        
    def isEnabled(self):
        return self._enabled
    #Draw the field on the screen. 
    def Render(self, screen, name, message):

        
        text = font.render(message, True, (255, 255, 255), (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (512, 300)

        pygame.draw.rect(screen, (255,255,255), (307, 354, 410, 60))

        input_text_surface = font.render(name, True, (45, 25, 98))
        input_text_rect = input_text_surface.get_rect()
        input_text_rect.x = 312
        input_text_rect.y = 373

        screen.blit(text, textRect)
        screen.blit(input_text_surface, input_text_rect)
        #reads the text written
    def getText(self,event):
       
        end = False
                
        pressed_keys = pygame.key.get_pressed()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.disable()
               
                time.sleep(0.1)
                return self._name_text
                 
            elif event.key == pygame.K_BACKSPACE:
                self._name_text = self._name_text[:-1]
            elif len(self._name_text) < setup.get("input_ip_length"):
                    self._name_text += event.unicode
        return self._name_text
                    
    
