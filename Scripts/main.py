
"""from Game_Data import *
from Enemies import Enemies,EnemyAttackBoard
from Save_Handler import save_data,load_data,update_data,Player_Data
from Scripts import Items
from Weapons import Current_Weapon"""
import pygame
from pygame import SCALED, FULLSCREEN
from Items import Notes
from LevelHandler import *
from EventScenes import *
from BattleHandler import *
import EventScenes
import time

from Scripts import DevTools

"""Timers"""
"""display"""
import Settings
from DevTools import *
pygame.init()
Level = Levels['floor1']()
#Temporary var for checking if currently playing on save file (remove later)
Game_ID=0
def restart(game):
    for item in Items_group:
        item.kill()
    for slot in Inventory_slots:
        slot.occupied = False
    EventScenes.Active_Riddles = Riddles.copy()
    global Level
    Game_.Player.reset_stats()
    Level = Levels['floor1']()
    game = Game()
    game.run()

#from Enemies import
"""Game_States"""
class Scene:
    def __init__(self,display,scene_manager):
        self.display = display
        self.scene_manager = scene_manager
class End(Scene):
    def __init__(self, display, scene_manager):
        super().__init__(display,scene_manager)
        self.return_menu = Button(WINDOW_WIDTH / 2 - 145, WINDOW_HEIGHT / 2, 'Return', 290, 90, True, 75)

    def run(self):

        victory_label.update()
        global Game_ID
        delete_data(Game_ID)
        if not SupportVariables.click_checker:
            SupportVariables.click_checker = True
            if self.return_menu.update(True):
                restart(Game_)
                self.scene_manager.set_scene('Menu')
        else:
            if self.return_menu.update(False):
                restart(Game_)
                self.scene_manager.set_scene('Menu')
class Menu(Scene):
    def __init__(self, display, scene_manager):
        super().__init__(display, scene_manager)
        self.cursor = Cursor()
        self.attack_board = EnemyAttackBoard('',self.cursor,2,3)
        self.attack_board.image = screen
        self.attack_board.rect = screen.get_frect(topleft=(0, 0))
        self.start = Button(WINDOW_WIDTH / 2 - 145, WINDOW_HEIGHT / 2, 'START', 290, 90, True, 75)
        self.info = Button(WINDOW_WIDTH * 0.9, WINDOW_HEIGHT * 0.9, 'i', 50, 50, True, 55)
        self.continue_button = Button(WINDOW_WIDTH / 2 - 145, WINDOW_HEIGHT / 1.5, 'Continue', 290, 90, True, 60, True,
                                 (WINDOW_WIDTH / 2.4, WINDOW_HEIGHT / 1.53))
        for border,sur in zip(self.attack_board.board_border,self.attack_board.board_border_surfaces):
            sur.set_alpha(0)
            self.attack_board.board_border_surfaces.remove(sur)
            self.attack_board.board_border.remove(border)
            sur.set_alpha(0)
        for sur in self.attack_board.board_border_surfaces:
            sur.set_alpha(0)
        self.Timer = Timer()
        self.title_label = title_lbl
        self.label = None
        try:
            Game_.DevTools_Move.load_sprite_pos()
        except:
            pass
    def run(self):

        self.attack_board.update(Settings.dt)
        self.title_label.update(lambda label: label.dynamic_render())
        self.cursor.update(Cursor.show,self.attack_board.rect)
        if self.cursor.collide_with_projectiles(self.attack_board.projectiles):
            self.cursor.player_cursor_death()
        global Game_ID
        SupportVariables.battle_started=False
        if self.continue_button.update():
            Game_ID = 1
            self.scene_manager.create_scene()
            self.scene_manager.set_scene('SaveSelection')
        if self.start.update():
            Game_ID=0
            self.scene_manager.Game_Running = True
            print("Button Pressed")
            self.label = AppearingLabel(0.2, "VerminNest I3", 'white',WINDOW_WIDTH/2, WINDOW_HEIGHT / 2-50, 120, 'PixelFont.ttf',
                           (800, 120), (80, 90))

            Game_.Player.reset_stats()
            print(Default_Data)

        if self.info.update():
            print("info")
        if self.label is not None:
            if self.label.dynamic_render(False,True,True):
                self.scene_manager.create_scene()
                self.scene_manager.set_scene('Corridor')
                global Level
                Level = Levels['floor1']()
                screen.fill('black')
            else:
                screen.fill('black')
                self.label.dynamic_render(False,True,True)
class Corridor(Scene):
    def __init__(self, display, scene_manager,player):
        super().__init__(display, scene_manager)
        self.player = player
        self.ui = Base_UI
        self.room_score = room_score
        self.floor_score = floor_score
        self.enemy=None
        SupportVariables.click_checker = False
        SupportVariables.clicked = False
        global Level
        self.level = Level if Level is not None else None
        print('Corridor Instantiated')
        self.player.Data['Max_HP'] = hp_bar.create_bar(self.player.Data['HP'], self.player.Data['Max_HP'])
        self.player.Data['Max_Sanity'] = sanity_bar.create_bar(self.player.Data['Sanity'],
                                      self.player.Data['Max_Sanity'])
        print(self.player.Data['Sanity'])
        #create_corridor(False)
        pygame.mouse.set_visible(True)
        global Game_ID
        self.level.generate_corridor()
        self.level.update() if self.level is not None else None
    def run(self):
        pygame.mouse.set_visible(True)
        Vermin_I_Deco.animate()
        Vermin_I_Deco.animation_play(14, 2, '', 'topleft', Settings.dt)
        self.ui.update()
        room_score.dynamic_update(self.player.Data['Current_Room'])
        floor_score.dynamic_update(self.player.Data['Current_Floor'])
        level_update_result = self.level.update()
        if level_update_result is not None:
            if level_update_result[1] == 'Battle':
                self.scene_manager.instantiate = True
                self.scene_manager.set_scene('Battle')
                SupportVariables.door=level_update_result[0]
            elif level_update_result[1] == 'Bile':
                SupportVariables.door=level_update_result[0]
                self.scene_manager.create_scene()
                self.scene_manager.set_scene('Bile')
            elif level_update_result[1] == 'Fireplace':
                self.scene_manager.create_scene()
                self.scene_manager.set_scene('Fireplace')
            elif level_update_result[1] == 'Riddle':
                self.scene_manager.create_scene()
                self.scene_manager.set_scene('Riddle')
            else:
                #self.scene_manager.set_scene(self.level.generate_scene())
                print(self.level.generate_scene())
                self.scene_manager.instantiate = True
                self.enemy = 'Rat'
                SupportVariables.door='Rat'
                self.scene_manager.set_scene('Battle')
        for item in Items_group:
            item.unconditional_update()
        self.player.Max_HP = hp_bar.create_bar(self.player.Data['HP'], self.player.Data['Max_HP'])
        self.player.Max_Sanity = sanity_bar.create_bar(self.player.Data['Sanity'], self.player.Data['Max_Sanity'])
        Current_Weapon.animate()
        Current_Weapon.animation_play(1, 2, '', '', Settings.dt)
class Death(Scene):
    def __init__(self, display, scene_manager):
        super().__init__(display, scene_manager)
        self.death = ImageObject('../Scenes', 'Death', 100, 400)
        self.death.image = pygame.transform.scale_by(self.death.image,2)
        self.death.rect = self.death.image.get_frect()
        self.return_menu = Button(WINDOW_WIDTH / 2 - 145, WINDOW_HEIGHT / 2, 'Return', 290, 90, True, 75)
    def run(self):
        screen.blit(self.death.image, self.death.rect)
        death_lbl.update()
        global Game_ID
        delete_data(Game_ID)
        update_data(Game_.Player.Data,Clear_Data)
        if not SupportVariables.click_checker:
            SupportVariables.click_checker = True
            if self.return_menu.update(True):
                self.scene_manager.set_scene('Menu')
                restart(Game_)
        else:
            if self.return_menu.update(False):
                self.scene_manager.set_scene('Menu')
                restart(Game_)
class SaveSelection(Scene):
    def __init__(self, display, scene_manager):
        super().__init__(display, scene_manager)
        self.save_slot1_button = Button(WINDOW_WIDTH / 4 - 145, 20, 'Slot1', 290, WINDOW_HEIGHT - 50, True, 75, True,
                                   (300, WINDOW_HEIGHT / 2.5))
        self.save_slot2_button = Button(WINDOW_WIDTH / 2, 20, 'Slot2', 290, WINDOW_HEIGHT - 50, True, 75, True,
                                   (850, WINDOW_HEIGHT / 2.5))
    def run(self):
        global Game_ID
        global Level
        if self.save_slot1_button.update():
            if Game_ID!=0:
                Game_ID=1
                if load_data(1):
                    self.scene_manager.create_scene()
                    Game_.Player.update_stats(Player1.Data)
                    Game_.Inventory_.__init__(Game_.screen,Game_.SceneManager)
                    Level.load_corridor(Game_.Player.Data['Corridor'])
                    Level.generate_corridor()
                    self.scene_manager.set_scene('Corridor')
            else:
                save_data(1, Game_.Player.Data)
                SupportVariables.Running=False
        if self.save_slot2_button.update():
            if Game_ID!=0:
                Game_ID = 2
                if load_data(2):
                    self.scene_manager.create_scene()
                    self.scene_manager.set_scene('Corridor')
                    Game_.Player.update_stats(Player2.Data)
                    Game_.Corridor_.__init__(Game_.screen, Game_.SceneManager, Game_.Player)
                    print(Player_Data2)
                    Level.load_corridor(Game_.Player.Data['Corridor'])
                    Level.generate_corridor()


            else:
                save_data(2, Game_.Player.Data)
                SupportVariables.Running=False
class Inventory(Scene):
    def __init__(self, display, scene_manager):
        super().__init__(display, scene_manager)
        for item in Items_group: # refresh items every time inventory is instantiated
            item.kill()
        Inventory_slots.empty()
        Equipment_slots.empty()
        Notes_group.empty()
        OneTimeUseItems_group.empty()
        Equipment_group.empty()
        self.Running = False
        self.label = AppearingLabel(0.3,"inventory",'white',1200,800)
        self.snapshot=[]
        offset_x = 0
        """slots setup"""
        for i in range(5):
            offset_y = 0
            i = Button(10+offset_x,10,'',150,150,True,80,False,(100,100),True)
            Inventory_slots.add(i)
            offset_x += 200
            for j in range(4):
                j = Button(-190+offset_x,190+offset_y,'',150,150,True,80,False,(100,100),True)
                Inventory_slots.add(j)
                offset_y += 180
        helmet_slot =ImageButton('../Icons','Helmet',1200,10,'',200,200,True)
        chestplate_slot =ImageButton('../Icons','ChestPlate',1200,230,'',200,200,True)
        Equipment_slots.add(helmet_slot)
        Equipment_slots.add(chestplate_slot)
        """items setup"""
        if len(Player0.Data['Items']) ==0:
            self.note = Notes['Test_Note']()
            self.bottle = OneTimeUseItems['Bottle']()
            self.bottle2 = OneTimeUseItems['Bottle']()
            self.bottle3 = OneTimeUseItems['Bottle']()
            self.helmet2 = Equipment_Items['Helmet']()
            self.pill = OneTimeUseItems['Powdered Happiness']()
            print(Player0.Data['Items'])
            #Items_group.add(self.helmet2)
            #Items_group.add(self.note)
            #Items_group.add(self.bottle)
            #Items_group.add(self.pill)
        else:

            registry = {**Notes, **Equipment_Items, **OneTimeUseItems}
            for item_name in Player0.Data['Items']:
                equipped = item_name.endswith('_equipped')
                base_name = item_name[:-9] if equipped else item_name
                cls = registry.get(base_name)
                if cls is None:
                    print(f"Unknown item name in save: {item_name}")
                    continue
                print(item_name)
                item = cls()
                if equipped:
                    for slot in Equipment_slots:
                        if getattr(slot, 'image_name', None) == getattr(item, 'eq_type', None) and not getattr(slot,
                        'occupied',False):
                            item.free_current_slot()
                            item.rect.center = slot.rect.center
                            item.original_pos = item.rect.center
                            item.equipped = True
                            slot.occupied = True
                            slot.image.set_alpha(0)
                            item.apply_effects()
                            break

    def state_save(self):
        self.snapshot = [item.used for item in Items_group]
        for i,item in enumerate(Items_group):
            self.snapshot[i] = item.used
    def state_check(self): # detects if any item was used in battle

        current_snapshot = [item.used for item in Items_group]
        if len(self.snapshot)!=len(current_snapshot):
            if len(self.snapshot)==0:
                self.snapshot = current_snapshot
                return False
            else:
                self.snapshot = current_snapshot
                print(Player0.Data['Sanity'])
                return True
        for i,item in enumerate(Items_group):
            if current_snapshot[i] != self.snapshot[i]:
                item.used = False
                print(Player0.Data['Sanity'])
                return True
        return False

    def run(self):
        self.state_save() if self.scene_manager.previous_scene=='Battle' else None
        screen.fill('black')
        pygame.mouse.set_visible(True)
        Notes_group.update(lambda s: s.show())
        any_visible = any(n.visible for n in Notes_group.sprites())
        if any_visible:
            self.Running = True
            return
        Inventory_slots.update()
        Equipment_slots.update()
        Items_group.update()
        self.Running = True
        self.label.update(lambda label: label.dynamic_render())
        if self.state_check() and self.scene_manager.previous_scene=='Battle':
            self.close_inventory('Battle')
    def close_inventory(self,previous_scene):
        self.Running =False
        self.scene_manager.set_scene(previous_scene)
classes = {"Menu": Menu, 'Battle':Battle, 'Corridor': Corridor, 'End':End,
                                'Death':Death,'SaveSelection':SaveSelection,'Inventory':Inventory, 'Bile':Bile, 'Fireplace':Fireplace,'Riddle':Riddle}
class Game:
    def __init__(self):
        global Game_ID
        pygame.init()
        self.game_state = None
        self.floor = 'floor1'
        self.level =None
        self.clock = pygame.time.Clock()
        self.Player = Player0
        self.screen = screen
        self.Enemy =Enemies['Rat']()
        self.Fullscreen = Fullscreen

        self.SceneManager = SceneManager('Menu')
        self.Menu_ = Menu(self.screen, self.SceneManager)
        self.SaveSelection_ = None#SaveSelection(self.screen, self.SceneManager)
        self.Corridor_ = None #Corridor(self.screen,self.SceneManager,self.Player)
        self.Battle_ = None #Battle(self.screen,self.SceneManager,self.Player,self.Enemy,self, Game_ID)
        self.Death_ = None#Death(self.screen,self.SceneManager)
        self.Bile_ = None#Bile(self.SceneManager)
        self.Fireplace_ = None#Fireplace(self.SceneManager,self.Player)
        self.End_ = None#End(self.screen,self.SceneManager)
        self.Inventory_ = Inventory(self.screen,self.SceneManager)
        self.Riddle_ = None#Riddle(self.SceneManager)
        self.Scenes =  {"Menu": self.Menu_, 'Battle':self.Battle_, 'Corridor': self.Corridor_, 'End': self.End_,
            'Bile': self.Bile_, 'Fireplace': self.Fireplace_,
            'Death': self.Death_,'SaveSelection':self.SaveSelection_,'Inventory':self.Inventory_,'Riddle':self.Riddle_}
        self.DevTools_Move = MoveTool(Buttons_group, lambda: self.SceneManager.current_scene,self.Scenes.keys())
        print(Buttons_group)
    def create_scene(self,scene_name,class_name,*additional_args):
        try:
            self.Scenes[scene_name]= class_name(self.screen,self.SceneManager,*additional_args)
        except:
            self.Scenes[scene_name] = class_name(self.SceneManager, *additional_args)
        self.DevTools_Move.capture_scene_positions()
        self.DevTools_Move.apply_positions()

        print(Buttons_group)
    def run(self):
        print(Player_Data)
        while SupportVariables.Running:
            global Game_ID
            self.DevTools_Move.move_sprites(self.DevTools_Move.group)
            screen.fill((0,0,0))
            Settings.dt = clock.tick(60)/1000.0
            Settings.previous_time = time.time()
            def save_items():
                for item in list(Items_group):
                    if item in Equipment_group and getattr(item, 'equipped', False):
                        item.revert_effects()

                snapshot = []
                for item in list(Items_group):
                    name = getattr(item, 'image_name', None)
                    if not name:
                        continue
                    entry = f"{name}_equipped" if getattr(item, 'equipped', False) else name
                    snapshot.append(entry)

                Player0.Data['Items'] = snapshot
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.DevTools_Move.save_sprite_pos()
                    if Game_ID == 0 and self.SceneManager.Game_Running:
                        self.SceneManager.set_scene('SaveSelection')
                        self.SceneManager.Game_Running = False
                        save_items()

                    else:
                        save_items()
                        SupportVariables.Running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11 and not self.Fullscreen:
                         self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT),
                                                                  FULLSCREEN | SCALED | DOUBLEBUF)
                         self.Fullscreen = True
                    elif event.key == pygame.K_F11 and self.Fullscreen:
                        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), SCALED | DOUBLEBUF)
                        self.Fullscreen = False
                    elif event.key == pygame.K_TAB and not self.Inventory_.Running and not self.SceneManager.current_scene in['Battle','Menu','SaveSelection']:
                        self.SceneManager.previous_scene = self.SceneManager.current_scene
                        self.SceneManager.set_scene('Inventory')
                    elif event.key == pygame.K_TAB and self.Inventory_.Running and not self.SceneManager.current_scene=='Battle':
                        self.Inventory_.close_inventory(self.SceneManager.previous_scene)
                    elif event.unicode in string.ascii_letters:
                        for inputArea in Input_group:
                            inputArea.text += event.unicode.upper()
                    elif event.key == pygame.K_BACKSPACE:
                        for inputArea in Input_group:
                            if len(inputArea.text)>1:
                                inputArea.text = inputArea.text[:-1] if inputArea.text[len(inputArea.text)-1]!='_' else inputArea.text[:-2]
                    elif event.key == pygame.K_RETURN:
                        current_scene_obj = self.Scenes.get(self.SceneManager.current_scene)
                        if hasattr(current_scene_obj, 'check_answer'):
                            current_scene_obj.check_answer()
                    elif event.key == pygame.K_0:
                        print('o')
                        self.DevTools_Move.factory_reset()

            if self.SceneManager.instantiate:
                name = self.SceneManager.get_scene()
                cls = classes[name]
                if name == 'Battle':
                    self.Enemy = Enemies[SupportVariables.door]()
                    self.create_scene(name, cls, self.Player, self.Enemy,self,Game_ID)
                elif name == 'Corridor' or name == 'Fireplace':
                    self.create_scene(name, cls, self.Player)
                elif name == 'Bile':
                    global Level
                    self.create_scene(name,cls,Level)
                else:
                    self.create_scene(name, cls)
            self.Scenes[self.SceneManager.get_scene()].run()
            for item in Items_group:
                item.unconditional_update()
            pygame.display.update()
            pygame.display.set_caption("Monochrome Tower")

def create_floor(level,floor):
    if level is None:
        level = Levels[floor]()
Game_= Game()
Game_.run()

