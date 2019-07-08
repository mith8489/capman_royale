import pygame
import threading
import os
import time
from title_animation import *
from text_scroll import *
pygame.init()


#
#Creates a single thread running in the backgrund
#updating the animations for titlescreen.
#
class AnimeThread(object):

    def __init__(self,speed, scroll, scroll2, star_group):

        self.speed = speed

        self._thread = threading.Thread(target=self.run, args=())
        self._thread.daemon = True
        self._scroll = scroll
        self._scroll2 = scroll2
        self._star = star_group
        self._active = True
        self._thread.start()
    #Updating scroll + stars concurrent.
    def run(self):

        while self._active:
            self._scroll.update()
            self._scroll2.update()
            self._star.update()
            time.sleep(self.speed)
        self._thread.join()

    
    def end_thread(self):
        self_active = False
        





