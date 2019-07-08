import pygame
import os
#TODO:Image address till en constant
player_dir = "sprites/player/"
player_image = "player-first-draft"
bot_dir = "sprites/bots/"
bot_image = "goblin_bot"
bullet_dir = "sprites/bullet/"
bullet_image = "bullet"

class Entity(pygame.sprite.Sprite):
    def __init__(self, name, x_coord, y_coord, image_dir, image_name):
        pygame.sprite.Sprite.__init__(self)
        self._name = name
        self._image_dir = image_dir
        self._image_name = image_name
        self._anim_frames = 1
        self._current_frame = 0
        self._facing = "South"
        self._set_image()
        self.rect = self.image.get_rect()
        self.rect.center = (x_coord, y_coord)

    def _set_position(self, x_pos, y_pos):
        self.rect.center = (x_pos, y_pos)

    def _set_image(self):
        self._image_address = self._image_dir + self._facing + "/" + self._image_name + str(self._current_frame + 1) + ".png"
        self.image = get_image(self._image_address)#.convert()

class Player(Entity):
    def __init__(self, name, x_coord, y_coord, hit_points):
        Entity.__init__(self, name, x_coord, y_coord, player_dir, player_image)
        self._hit_points = hit_points
        self._max_hit_points = hit_points

    def _set_hit_points(self, hit_points):
        if self._hit_points != hit_points:
            self._hit_points = hit_points
            print "Player now has " + str(hit_points) + " hit points"

class Bot(Entity):
    def __init__(self, name, x_coord, y_coord, hit_points):
        Entity.__init__(self, name, x_coord, y_coord, bot_dir, bot_image)
        self._hit_points = hit_points
        self._max_hit_points = hit_points
        self._anim_frames = 8

    def _set_hit_points(self, hit_points):
        if self._hit_points != hit_points:
            self._hit_points = hit_points
            print "Player now has " + str(hit_points) + " hit points"

class Bullet(Entity):
    def __init__(self, name, x_coord, y_coord):
        Entity.__init__(self, name, x_coord, y_coord, bullet_dir, bullet_image)

        self._anim_frames = 8


_image_library = {}
def get_image(path):
    global _image_library
    image = _image_library.get(path)
    if image == None:
        canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
        image = pygame.image.load(canonicalized_path)
        _image_library[path] = image
    return image
