import pygame
import socket
from threading import Thread, Lock, Timer
import json
import time
from sprite_classes import *
from map_convert import *
from menu import *
from title_animation import *
from text_scroll import *
from anime_thread import *
from input_popup import *
from setup import *
from lobby_item import *


# SceneBase is the base class from which all other scene classes inherit
# It defines the base functions that are executed continously in the game loop,
# and which must all be overridden by each subclass.
class SceneBase:
    def __init__(self):
        self.next = self

    def ProcessInput(self, events, pressed_keys):
        print("YOU DIDNT OVERRIDE PROCESSINPUT IN SUBCLASS")

    def Update(self):
        print("YOU DIDNT OVERRIDE UPDATE IN SUBCLASS")

    def Render(self):
        print("YOU DIDNT OVERRIDE RENDER IN SUBCLASS")

    def use_events(self,event):
        pass

    def SwitchToScene(self, next_scene):
        self.next = next_scene


    def SendQuitMessage(self):
        pass

    def Terminate(self):
        self.SwitchToScene(None)

##StartScene

class TitleScene(SceneBase):
        #asks for and sets player name
    def name(self):
        self._input_box.enable()

        #asks for ands set ip to server
    def ip(self):
        self._ip_box.enable()

        #ends game
    def quit_all(self):
         quit()

        #starts game
    def start(self):
        print ("start")
        # if ip == 0 or playerName == "player_name":
        #    msgbox("please choose name and set ip before starting!")
        # else:
        self.SwitchToScene(LobbyScene(self._name, self._ip, self._th, self.star_group))


      #init scene
      #name - dummy name
      # ip - ip dummy ip
      #menu_item = the title screen menu
      #star_group the background stars
      #th = the animating thread
    def __init__ (self):

        self._name = "player_name"
        self._ip = "localhost"
        SceneBase.__init__(self)

        self.game_folder = os.path.dirname (__file__)
        self.spr_folder = os.path.join(game_folder,"menu_items")
        self.menu_item = [{"pointer":"pointer.png",
            "screen_height": setup.get("Screen_width"),
            "screen_width" : setup.get("Screen_height"),
            "top_position" : 140 ,
            "distance" : 150 } ,
            ("Name.png",self.name), ("ip.png",self.ip) ,("start.png",self.start),("quit.png",self.quit_all) ]

        self.menu = Menu(self.menu_item)
        self.scroll_file = open(os.path.join(spr_folder,"scroll_text.txt" ))
        self.scroll_text = self.scroll_file.readline()
        self.scroll_text2 = self.scroll_file.readline()
        self.scroll = make_scroll(self.scroll_text,5,True, 0, 60)
        self.scroll2 = make_scroll(self.scroll_text2,700,False, 2,32)
        self._input_box= Input_window()
        self._ip_box = Input_window()
        self.star_group = create_stars(2000)
        self._th = AnimeThread(0.01, self.scroll,self.scroll2, self.star_group)
        self._anime_mutex = Lock()

    def ProcessInput(self, events, pressed_keys):
        pass
        #self.menu._update(screen, pressed_keys)
        #if self._input_box.isEnabled():
        #   self._input_box.ProcessInput(events, pressed_keys)

    def Update(self):

        pass

    def use_events(self, event):

        if self._ip_box.isEnabled() or self._input_box.isEnabled():
            self.menu._deactivate()
            self.menu._switch_off()
        else:
            self.menu._activate()
            self.menu._switch_on()
        if self._ip_box.isEnabled():
            #self._input_box.disable()
            self._ip = self._ip_box.getText(event)
            self.menu._active = False

        if self._input_box.isEnabled():
            #self._ip_box.disable()
            self.menu._active = False
            self._name = self._input_box.getText(event)

        self.menu._check_Move(event)

    def Render(self, screen):
        screen.fill((0,0,0))
        self._anime_mutex.acquire()
        self.star_group.draw(screen)
        self.scroll.draw(screen)
        self.scroll2.draw(screen)
        self._anime_mutex.release()

        if self.menu._visible:
            self.menu._show(screen)

        if self._input_box.isEnabled():
            self._input_box.Render(screen,self._name,'Please enter your name')
        if self._ip_box.isEnabled():
            self._ip_box.Render(screen,self._ip,'Enter ip to server')

        pygame.display.flip()

class LobbyScene(SceneBase):
    def __init__(self, player_name, ip_address, anime_thread, star_group):
        SceneBase.__init__(self)
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client.connect((ip_address, 8080))
        self._decoder = json.JSONDecoder()
        self._player_name = player_name
        self._players_ready = []
        self._th = anime_thread
        self.star_group = star_group
        self._anime_mutex = Lock()

        self._font = pygame.font.Font('freesansbold.ttf', 40)

        self._receive_thread = Thread(target = self._receive_data)
        self._receive_thread.daemon = True
        self._receive_thread.start()

        self._lobby_items = {}
        try:
            add_msg = json.dumps({'Id': 200, 'Name': "ADD_PLAYER", 'PlayerName': self._player_name, 'X': 801, 'Y': 380, 'Facing': 2})
            self._client.send(add_msg)

            get_players_msg = json.dumps({'Id': 1000, 'Name': "GET_ALL_PLAYERS"})
            self._client.send(get_players_msg)
        except:
            self.SwitchToScene(GameRunningScene())

    def use_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self._player_name not in self._players_ready:
                    print "Player is ready"
                    ready_msg = json.dumps({'Id': 800, 'Name': "READY_PLAYER", 'PlayerName': self._player_name})
                    self._client.send(ready_msg)
            if event.key == pygame.K_BACKSPACE:
                remove_msg = json.dumps({'Id': 300, 'Name': "REMOVE_PLAYER", 'PlayerName': self._player_name})
                self._client.send(remove_msg)


    def ProcessInput(self, events, pressed_keys):
        pass

    def Update(self):
        pass

    def Render(self, screen):
        screen.fill((0,0,0))
        self._anime_mutex.acquire()
        self.star_group.draw(screen)
        self._anime_mutex.release()

        # text = self._font.render("PRESS ENTER WHEN YOU ARE READY", True, (255, 255, 255))
        # textRect = text.get_rect()
        # textRect.center = (512, 300)

        # screen.blit(text, textRect)

        for item in self._lobby_items:
            self._lobby_items[item]._draw(screen)

    def _receive_data(self):
        while True:
            for line in linesplit(self._client):
                json_data = self._decoder.decode(line)
                self._handle_response(json_data)

    def _handle_response(self, json_data):
        id = json_data['Id']
        if id == 201:
            name = json_data['EntityName']
            if name not in self._lobby_items:
                player = lobby_item(name, setup.get("Screen_width") / 4, 40 + (60 * (len(self._lobby_items) + 1)))
                if json_data['Ready'] == True:
                    player._set_ready()
                self._lobby_items[name] = player

        elif id == 301:
            name = json_data['EntityName']
            if name in self._lobby_items:
                del self._lobby_items[name]
                if name == self._player_name:
                    self.SwitchToScene(TitleScene())
        elif id == 801:
            name = json_data["EntityName"]
            self._lobby_items[name]._set_ready()
        elif id == 802:
            self.SwitchToScene(GameScene(self._player_name, self._client))
            self._th.end_thread()

            # Since this function is runned on a seperate thread, we need to exit so that the thread dies
            # and lets GameScene run it's own thread
            exit()

## GameScene
# The scene that handles that actual game where you run around.
class GameScene(SceneBase):
    def __init__(self, player_name, connection):
        SceneBase.__init__(self)
        self._client = connection
        self._decoder = json.JSONDecoder()

        #Number of updates each animation frame should last for (1 update = 1/60 seconds)#
        self._frame_time = 2
        self._frame_ctr = 0

        self._PLAYER_NAME = player_name

        self._bullet_mutex = Lock()
        self._bot_mutex = Lock()
        self._player_mutex = Lock()

        self._font = pygame.font.Font('freesansbold.ttf', 25)
        self._hit_points_text = "0"
        self._hit_points_surface = self._font.render(self._hit_points_text, True, (255, 255, 255))
        self._hit_points_rect = self._hit_points_surface.get_rect()
        self._hit_points_rect.x = 5
        self._hit_points_rect.y = 5

        self._player_killed_text = ""
        self._player_killed_surface = self._font.render(self._player_killed_text, True, (255, 255, 255))
        self._player_killed_rect = self._player_killed_surface.get_rect()
        self._player_killed_rect.x = 5
        self._player_killed_rect.y = 35

        self._background = get_image("maps/floor_grass_2.png").convert()
        self._player_group = pygame.sprite.GroupSingle()
        self._opponents_group = pygame.sprite.Group()
        self._bullets = pygame.sprite.Group()
        self._game_map = read_map("map.txt")
        self._sprite_render_group = pygame.sprite.OrderedUpdates()
        self._walls = make_map_sprites(self._game_map)

        self._bots = pygame.sprite.Group()

        self._sprite_group_mutex = Lock()

        self._receive_thread = Thread(target = self._receive_data)
        self._receive_thread.daemon = True
        self._receive_thread.start()

        getInitStateMsg = json.dumps({'Id': 900, 'Name': "GET_INITIAL_STATE"})
        self._client.send(getInitStateMsg)

        self._labyrint = pygame.image.load("maps/labyrint.png").convert()
        self._labyrint = pygame.transform.scale(self._labyrint, (setup.get("Screen_width"), setup.get("Screen_height")))

        self._up = setup.get("up_key")
        self._down = setup.get("down_key")
        self._left = setup.get("left_key")
        self._right = setup.get("right_key")


    def ProcessInput(self, events, pressed_keys):
        try:
            if self._player_group.sprite != None:
                move_x = 0
                move_y = 0

                # 0 means don't move
                # 1 means move forward in a direction
                # -1 means move backward in a direction

                if pressed_keys[eval(self._up)]:
                    move_y = -1
                if pressed_keys[eval(self._down)]:
                    move_y = 1
                if pressed_keys[eval(self._left)]:
                    move_x = -1
                if pressed_keys[eval(self._right)]:
                    move_x = 1
                if move_x != 0 or move_y != 0:
                    move_message = json.dumps({"Id":400, "Name":"MOVE_PLAYER", "PlayerName":self._player._name, "X": move_x, "Y": move_y})
                    self._client.send(move_message)
                if pressed_keys[pygame.K_TAB]:
                    fire_message = json.dumps({"Id":500, "Name":"FIRE_BULLET", "PlayerName":self._player._name, "X": self._player.rect.center[0], "Y": self._player.rect.center[1]})
                    self._client.send(fire_message)
        except:
            pass

    def Update(self):
        self._sprite_group_mutex.acquire()
        self._bot_mutex.acquire()
        self._player_mutex.acquire()
        try:
            self._sprite_render_group._spritelist.sort(key=lambda x: x.rect.bottom)
            if self._player_group.sprite != None:
                self._hit_points_text = "HP: " + str(self._player._hit_points) + " / PLAYERS ALIVE: " + str(len(self._opponents_group) + len(self._player_group)) + " / BOTS ALIVE: " + str(len(self._bots))
                self._hit_points_surface = self._font.render(self._hit_points_text, True, (255, 255, 255))
                self._animate_object(self._player_group.sprite, 1)
            for player in self._opponents_group:
                self._animate_object(player, 1)
            for bot in self._bots:
                self._animate_object(bot, 6)
            self._bullet_mutex.acquire()
            for bullet in self._bullets:
                self._animate_object(bullet, 2)
            self._bullet_mutex.release()
        finally:
            self._sprite_group_mutex.release()
            self._bot_mutex.release()
            self._player_mutex.release()
        self._frame_ctr += 1

    # Updates the current animation frame of a
    # sprite object, if necessary.
    def _animate_object(self, sprite_object, frame_time):
        sprite_object._current_frame = (self._frame_ctr // frame_time) % sprite_object._anim_frames
        sprite_object._set_image()

    def Render(self,screen):
        screen.blit(self._background, (0,0))
        self._sprite_group_mutex.acquire()
        self._bullet_mutex.acquire()
        try:
            screen.blit(self._labyrint,[0,0])

            #self._walls.draw(screen)
            self._sprite_render_group.draw(screen)
            self._display_hp()
        finally:
            self._bullet_mutex.release()
            self._sprite_group_mutex.release()
            screen.blit(self._hit_points_surface, self._hit_points_rect)
            screen.blit(self._player_killed_surface, self._player_killed_rect)

    def SendQuitMessage(self):
        quit_message = json.dumps({"Id":300, "Name":"REMOVE_PLAYER", "PlayerName":self._player._name})
        self._client.send(quit_message)

    ##Draws hp bar for selected sprite group.
    def _render_hp_bar(self,group):
        offset = 0
        if group == self._bots:
            offset = -10
        for entity in group:
            width =  30 *(float(entity._hit_points) / float(entity._max_hit_points))
            pygame.draw.rect(screen,(255,0,0),(entity.rect.center[0]-15,entity.rect.center[1]-30+offset,30,7))
            pygame.draw.rect(screen,(0,255,0),(entity.rect.center[0]-15,entity.rect.center[1]-30+offset,(width),7))

    ## Renders hp bar for every sprite group.
    def _display_hp(self):
        self._player_mutex.acquire()
        self._bot_mutex.acquire()
        self._render_hp_bar(self._player_group)
        self._render_hp_bar(self._bots)
        self._render_hp_bar(self._opponents_group)
        self._player_mutex.release()
        self._bot_mutex.release()


    def _receive_data(self):
        while True:
            for line in linesplit(self._client):
                json_data = self._decoder.decode(line)
                self._handle_response(json_data)

    def _handle_response(self, json_data):
        id = json_data['Id']
        if id == 201:
            self._add_sprite(json_data)
        elif id == 202:
            print json_data['Message']
        elif id == 203:
            print json_data['Message']
        elif self._player_group.sprite != None:
            if id == 101:
                self._change_entity_state(json_data)
            elif id == 102:
                self._update_bullet(json_data)
            elif id == 301:
                self._kill_sprite(json_data)
            elif id == 501:
                self._add_bullet(json_data)
            elif id == 601:
                self._remove_bullet(json_data)
            elif id == 701:
                self._winning_player(json_data)
            elif id == 1101:
                self._client.close()
                exit()

    def _winning_player(self,json_data):
            if (json_data['EntityName']== self._PLAYER_NAME):
                print json_data['EntityName']
                try:
                    self.SwitchToScene(WinningScene(self._PLAYER_NAME))
                except:
                    print "Program terminated"
            else:
                self.SwitchToScene(GameOverScene())
                print "Did not Win"


    def _add_sprite(self, json_data):
        self._sprite_group_mutex.acquire()
        try:
            char_type = json_data['CharType']
            if char_type == 0:
                if (json_data['EntityName'] == self._PLAYER_NAME):
                    self._add_client_player(json_data)
                else:
                    self._add_opponent(json_data)
            elif char_type == 1:
                self._add_bot(json_data)
        finally:
            self._sprite_group_mutex.release()

    def _add_client_player(self, json_data):
        self._player_mutex.acquire()
        self._player = Player(json_data['EntityName'], json_data['X'], json_data['Y'], json_data['HitPoints'])
        self._player_group.add(self._player)
        self._sprite_render_group.add(self._player)
        print json_data['EntityName'] + " succesfully added!"
        self._player_mutex.release()

    def _add_opponent(self, json_data):
        self._player_mutex.acquire()
        opponent = Player(json_data['EntityName'], json_data['X'], json_data['Y'], json_data['HitPoints'])
        self._opponents_group.add(opponent)
        self._sprite_render_group.add(opponent)
        print json_data['EntityName'] + " succesfully added!"
        self._player_mutex.release()

    def _add_bot(self, json_data):
        self._bot_mutex.acquire()
        bot = Bot(json_data['EntityName'], json_data['X'], json_data['Y'], json_data['HitPoints'])
        self._bots.add(bot)
        self._sprite_render_group.add(bot)
        print "Added bot with HP: " + str(bot._hit_points)
        self._bot_mutex.release()

    def _add_bullet(self, json_data):
        self._bullet_mutex.acquire()
        bullet = Bullet(json_data['EntityName'], json_data['X'], json_data['Y'])
        self._bullets.add(bullet)
        self._sprite_render_group.add(bullet)
        self._bullet_mutex.release()

    def _kill_sprite(self, json_data):
        self._bot_mutex.acquire()
        print "SPRITE KILLED: " + json_data['EntityName']
        for bot in self._bots:
            print bot._name
        if json_data['CharType'] == 0:
            self._player_mutex.acquire()
            if (json_data['EntityName'] == self._player._name):
                self._player.kill()
                try:
                    self.SwitchToScene(GameOverScene())
                except:
                    print "Program terminated"
            else:
                for opponent in self._opponents_group:
                    if (json_data['EntityName'] == opponent._name):
                        self._show_player_killed_text(opponent)
                        opponent.kill()
                        t = Timer(5.0, self._hide_player_killed_text)
                        t.start()
            self._player_mutex.release()
        else:
            print "KILLED BOT " + json_data['EntityName']
            for bot in self._bots:
                if (json_data['EntityName'] == bot._name):
                    bot.kill()
        self._bot_mutex.release()

    def _remove_bullet(self, json_data):
        self._bullet_mutex.acquire()
        for bullet in self._bullets:
                if (json_data['EntityName'] == bullet._name):
                    bullet.kill()
        self._bullet_mutex.release()

    def _show_player_killed_text(self, opponent):
        self._player_killed_text = opponent._name + " HAS DIED"
        self._player_killed_surface = self._font.render(self._player_killed_text, True, (255, 255, 255))

    def _hide_player_killed_text(self):
        self._player_killed_text = ""
        self._player_killed_surface = self._font.render(self._player_killed_text, True, (255, 255, 255))

    def _change_entity_state(self, json_data):
        if json_data['CharType'] == 0:
            self._player_mutex.acquire()
            if (json_data['EntityName'] == self._player._name):
                self._player._set_position(json_data['X'], json_data['Y'])
                self._player._facing = json_data['Facing']
                self._player._set_hit_points(json_data['HitPoints'])
            else:
                for opponent in self._opponents_group:
                    if (json_data['EntityName'] == opponent._name):
                        opponent._set_position(json_data['X'], json_data['Y'])
                        opponent._facing = json_data['Facing']
                        opponent._set_hit_points(json_data['HitPoints'])
            self._player_mutex.release()
        else:
            self._bot_mutex.acquire()
            for bot in self._bots:
                if (json_data['EntityName'] == bot._name):
                    bot._set_position(json_data['X'], json_data['Y'])
                    bot._facing = json_data['Facing']
                    bot._set_hit_points(json_data['HitPoints'])
            self._bot_mutex.release()

    def _update_bullet(self, json_data):
        self._bullet_mutex.acquire()
        for bullet in self._bullets:
                if (json_data['EntityName'] == bullet._name):
                    bullet._set_position(json_data['X'], json_data['Y'])
        self._bullet_mutex.release()

class GameOverScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self._font = pygame.font.Font('freesansbold.ttf', 60)
        self._small_font = pygame.font.Font('freesansbold.ttf', 20)
        self._btn_color = (155, 185, 255)
        self._btn_highlight_color = (205, 205, 255)

        self._mouse_pos = [0, 0]
        self._new_game_button = pygame.Rect(412, 375, 200, 50)

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._new_game_button.collidepoint(self._mouse_pos):
                    self.SwitchToScene(TitleScene())


    def Update(self):
        self._mouse_pos = pygame.mouse.get_pos()

    def Render(self,screen):
        screen.fill((127, 0, 0))

        text = self._font.render('GAME OVER', True, (255, 255, 255), (127, 0, 0))
        textRect = text.get_rect()
        textRect.center = (512, 300)

        if self._new_game_button.collidepoint(self._mouse_pos):
            pygame.draw.rect(screen, self._btn_highlight_color,(412, 375, 200, 50))
            new_game_text = self._small_font.render('NEW GAME', True, (0, 0, 0), self._btn_highlight_color)
        else:
            pygame.draw.rect(screen, self._btn_color,(412, 375, 200, 50))
            new_game_text = self._small_font.render('NEW GAME', True, (0, 0, 0), self._btn_color)


        new_game_text_rect = new_game_text.get_rect()
        new_game_text_rect.center = (512, 400)

        screen.blit(new_game_text, new_game_text_rect)
        screen.blit(text, textRect)

## Scene for WinningScene
# After receiving response 701 for winning, WinningScene is selected. Winning scene shows a picture and plays music.
class WinningScene(SceneBase):
    def __init__(self, playername):
        SceneBase.__init__(self)
        self._font = pygame.font.Font('freesansbold.ttf', 60)
        self._small_font = pygame.font.Font('freesansbold.ttf', 20)
        self._btn_color = (155, 185, 255)
        self._btn_highlight_color = (205, 205, 255)

        self._winner_name = playername

        self._mouse_pos = [0, 0]
        self._new_game_button = pygame.Rect(412, 375, 200, 50)

        winning_music_thread = Thread(target = self._play_winning_music())
        winning_music_thread.daemon = True
        winning_music_thread.start()

    ##Checks for input on newgame button
    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._new_game_button.collidepoint(self._mouse_pos):
                    self._stop_winning_music()

                    self.SwitchToScene(TitleScene())

    ## Gets new mouse position.
    def Update(self):
        self._mouse_pos = pygame.mouse.get_pos()

    ## main function of class. Draws and renders everything, image, button and text.
    def Render(self,screen):
        screen.fill((50, 205, 50))

        text = self._font.render(self._winner_name + " WON!", True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = (512, 300)

        img = pygame.image.load('img/winner.jpg')

        if self._new_game_button.collidepoint(self._mouse_pos):
            pygame.draw.rect(screen, self._btn_highlight_color,(412, 375, 200, 50))
            new_game_text = self._small_font.render('NEW GAME', True, (0, 0, 0), self._btn_highlight_color)
        else:
            pygame.draw.rect(screen, self._btn_color,(412, 375, 200, 50))
            new_game_text = self._small_font.render('NEW GAME', True, (0, 0, 0), self._btn_color)


        new_game_text_rect = new_game_text.get_rect()
        new_game_text_rect.center = (512, 400)

        screen.blit(img, (0,0))
        screen.blit(new_game_text, new_game_text_rect)
        screen.blit(text, textRect)

    ## stop music
    def _stop_winning_music(self):
        pass
#        pygame.mixer.music.stop()

    ## Start music
    def _play_winning_music(self):
        pass
#        pygame.mixer.music.load("sound/WINNING.wav")

#        pygame.mixer.music.play(1)

class GameRunningScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self._font = pygame.font.Font('freesansbold.ttf', 30)
        self._small_font = pygame.font.Font('freesansbold.ttf', 20)
        self._btn_color = (155, 185, 255)
        self._btn_highlight_color = (205, 205, 255)

        self._mouse_pos = [0, 0]
        self._new_game_button = pygame.Rect(387, 375, 250, 50)

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._new_game_button.collidepoint(self._mouse_pos):
                    self.SwitchToScene(TitleScene())


    def Update(self):
        self._mouse_pos = pygame.mouse.get_pos()

    def Render(self,screen):
        screen.fill((0, 50, 150))

        text = self._font.render('GAME IS ALREADY RUNNING, CONNECTION REFUSED', True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = (512, 300)

        if self._new_game_button.collidepoint(self._mouse_pos):
            pygame.draw.rect(screen, self._btn_highlight_color,(387, 375, 250, 50))
            new_game_text = self._small_font.render('RETURN TO MAIN MENU', True, (0, 0, 0), self._btn_highlight_color)
        else:
            pygame.draw.rect(screen, self._btn_color,(387, 375, 250, 50))
            new_game_text = self._small_font.render('RETURN TO MAIN MENU', True, (0, 0, 0), self._btn_color)


        new_game_text_rect = new_game_text.get_rect()
        new_game_text_rect.center = (512, 400)

        screen.blit(new_game_text, new_game_text_rect)
        screen.blit(text, textRect)

# Splits input from a stream at newlines and yields one line at a time
def linesplit(client):
    buf = client.recv(4096)
    buffering = True
    while buffering:
        if "}" in buf:
            (line, buf) = buf.split("}", 1)
            yield line + "}"
        else:
            more = client.recv(4096)
            if not more:
                buffering = False
            else:
                buf += more
    if buf:
        yield buf
