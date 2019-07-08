from setup import *
from text_scroll import *

class lobby_item():
    def __init__(self, name, x, y):
        self._name = name
        self._x = x
        self._y = y
        self._ready = False
        self._lobby_headline = make_scroll("     lobby ", 30, False, 0, 48)
        self._background_color = eval(setup.get("lobby_item_bgcolor"))
        self._item_size = (setup.get("Screen_width") / 2, setup.get("lobby_item_height"))
        self._font = pygame.font.Font('freesansbold.ttf', 30)
        self._set_name_rect()

    def _set_name_rect(self):
        self._name_text = self._font.render(self._name, True, (0,0,0), self._background_color)
        self._name_rect = self._name_text.get_rect()
        self._name_rect.x = self._x + 10
        self._name_rect.y = self._y + 10

    def _draw(self, screen):
        pygame.draw.rect(screen, self._background_color, (self._x, self._y, self._item_size[0], self._item_size[1]))
        screen.blit(self._name_text, self._name_rect)
        self._lobby_headline.draw(screen)

    def _set_ready(self):
        self._ready = True
        self._background_color = eval(setup.get("lobby_item_readycolor"))
        self._set_name_rect()
