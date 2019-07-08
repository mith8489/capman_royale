import json
import pygame
pygame.init()



class Setup ():
    
    def load_setup(self):
        with open('config.json') as json_data_file:
            conf = json.load(json_data_file)
           
        return conf
 
    def __init__(self):
        self.setup = self.load_setup()

               
    def get(self, askedFor):
        return self.setup[askedFor]

setup = Setup()
