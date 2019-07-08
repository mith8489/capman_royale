import time
import sys, pygame
import math
import os


pygame.init()
SIZE = WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode(SIZE)
game_folder = os.path.dirname(__file__)
map_folder = os.path.join(game_folder,"maps")
MAP_HEIGHT= 24
MAP_WIDTH = 32

class Wall (pygame.sprite.Sprite):
    def __init__(self,x,y,graphic):
        
        l = int(math.ceil(WIDTH/(MAP_WIDTH)))
        b = int(math.ceil(HEIGHT/MAP_HEIGHT))
        pygame.sprite.Sprite.__init__(self)
        self.image = graphic
#        self.image = pygame.transform.scale(self.image, (l, b))
        self.color = 10;
        self.rect= self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.color_direction = 0
        

# Read a txt-file with given name and parse it to a matrix        
def read_map(file_name):
    try:
        returnMatrix =[]
        game_map = open(os.path.join(map_folder, file_name))
        line = game_map.readline()
        returnMatrix.append(line) 
        while line != '':
            line = game_map.readline()
            returnMatrix.append(line)
        return (returnMatrix)
    except Exception, e:
        print ("Can't find map_file :" +file_name)
        print (e)
        quit()
        

#convert the a map-matrix to spritegroup.

def make_map_sprites(game_map):
    try:
        graph_file = game_map[MAP_HEIGHT]
        print("GF: " + graph_file)
        graph_file = graph_file[0 : len(graph_file)-1]
        map_image = pygame.image.load(os.path.join(map_folder ,graph_file))
        map_image.set_colorkey((255,255,255))  
        return_group = pygame.sprite.OrderedUpdates();
        for i in range(0, MAP_HEIGHT):
            map_row = game_map[i]
        
            for j in range(0, MAP_WIDTH+1):
            
                if map_row[j] == "*":
                
                    x = (WIDTH/MAP_WIDTH)*j
                    y =  (HEIGHT/MAP_HEIGHT)*i
                    return_group.add(Wall(x,y,map_image))
                
                    #  else:
                    #     print("not read" +map_row[j])
        print "MAP SPRITES DONE"
        return return_group
    except Exception, e:
        print ("Can't find map_file :" +file_name)
        print (e)
        quit()

def test_screen(wall_group):
    while True: 
        wall_group.draw(screen)
        wall_group.update()
        pygame.display.flip()


