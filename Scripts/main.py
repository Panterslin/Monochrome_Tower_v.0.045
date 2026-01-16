from Game_Data import *
from Enemies import Enemies,EnemyAttack,Attack_board
from Save_Handler import save_data,load_data,update_data,Player_Data
from Scripts.Items import Equipment_Items
from Weapons import Current_Weapon
from pygame import SCALED, FULLSCREEN, DOUBLEBUF
from Items import Notes,OneTimeUseItems
from Groups import *
import time
"""Timers"""
"""display"""
import Settings
from Settings import Fullscreen
pygame.init()
#Temporary var for checking if currently playing on save file (remove later)
Game_ID=0
def restart():
    Game_=Game()
    Game_.run()

#from Enemies import
"""Game_States"""
class Scene:
    def __init__(self,display,scene_manager):
        self.display = display
        self.scene_manager = scene_manager
class End(Scene):
    def __init__(self, display, scene_manager):
        super().__init__(display,scene_manager)
    def run(self):
        victory_label.update()
        global Game_ID
        delete_data(Game_ID)
        if not SupportVariables.click_checker:
            SupportVariables.click_checker = True
            if return_menu.update(True):
                self.scene_manager.set_scene('Menu')
        else:
            if return_menu.update(False):
                self.scene_manager.set_scene('Menu')
class Menu(Scene):
    def __init__(self, display, scene_manager):
        super().__init__(display, scene_manager)
        self.cursor = Cursor()
        self.attack_board = EnemyAttack()
        self.Timer = Timer()
        self.title_label = title_lbl
    def run(self):
        self.attack_board.update(Settings.dt)
        self.title_label.update()
        self.cursor.update(Cursor.show,Attack_board.rect)
        if self.cursor.collide_with_projectiles(Attack_board.projectiles):
            self.cursor.player_cursor_death()
        global Game_ID
        SupportVariables.battle_started=False
        if continue_button.update():
            Game_ID = 1
            self.scene_manager.set_scene('SaveSelection')
        if start.update():
            Game_ID=0
            self.scene_manager.Game_Running = True
            print("Button Pressed")
            self.scene_manager.set_scene('Corridor')
            Game_.Player.reset_stats()
            print(Default_Data)
        if info.update():
            print("info")
class Corridor(Scene):
    def __init__(self, display, scene_manager,player):
        super().__init__(display, scene_manager)
        self.player = player
        self.ui = Base_UI
        self.room_score = room_score
        self.floor_score = floor_score
        print('Corridor Instantiated')
        self.player.Data['Max_HP'] = hp_bar.create_bar(self.player.Data['HP'], self.player.Data['Max_HP'])
        self.player.Data['Max_Sanity'] = sanity_bar.create_bar(self.player.Data['Sanity'],
                                      self.player.Data['Max_Sanity'])
        print(self.player.Data['Sanity'])
        create_corridor(False)
    def run(self):
        Vermin_I_Deco.animate()
        Vermin_I_Deco.animation_play(14, 7, '', 'topleft', Settings.dt)
        self.ui.update()
        room_score.dynamic_update(self.player.Data['Current_Room'])
        floor_score.dynamic_update(self.player.Data['Current_Floor'])
        scene= create_corridor(True)
        if scene=='Battle':
            self.scene_manager.create_scene()
        self.scene_manager.set_scene(scene)
        self.player.Max_HP = hp_bar.create_bar(self.player.Data['HP'], self.player.Data['Max_HP'])
        self.player.Max_Sanity = sanity_bar.create_bar(self.player.Data['Sanity'], self.player.Data['Max_Sanity'])
        Current_Weapon.animate()
        Current_Weapon.animation_play(1, 2, '', '', Settings.dt)
class Death(Scene):
    def __init__(self, display, scene_manager):
        super().__init__(display, scene_manager)
    def run(self):
        death_lbl.update()
        global Game_ID
        delete_data(Game_ID)
        update_data(Game_.Player.Data,Clear_Data)
        if not SupportVariables.click_checker:
            SupportVariables.click_checker = True
            if return_menu.update(True):
                self.scene_manager.set_scene('Menu')
                restart()
        else:
            if return_menu.update(False):
                self.scene_manager.set_scene('Menu')
                restart()
class Battle(Scene):
    def __init__(self,display,scene_manager, player, enemy):
        super().__init__(display,scene_manager)
        self.player = player
        self.enemy = enemy
        self.enemy_killed=False
        self.battle_state="Pre_round"
        self.turn_check=0
        self.attack_board = EnemyAttack()
        self.cursor = Cursor()
    def run(self):
        if Current_Weapon.clicked and not pygame.mouse.get_pressed()[0]:
            Current_Weapon.clicked = False
        if self.player.Data['HP']<=0:
            self.scene_manager.set_scene('Death')
            self.battle_state="Pre_round"
            SupportVariables.clicked=False
        """Sprites setup"""
        Vermin_I_Deco.animate()
        Vermin_I_Deco.animation_play(14,7,'','topleft',Settings.dt)
        room_score.dynamic_update(self.player.Data['Current_Room'])
        floor_score.dynamic_update(self.player.Data['Current_Floor'])
        self.enemy.update()
        self.enemy.animate() if not self.enemy.is_animating and not self.enemy.hp<=0 else None
        self.enemy.animation_play(2, 2.5, '', 'center', Settings.dt)
        Base_UI.update()
        self.player.Data['Max_HP']=hp_bar.create_bar(self.player.Data['HP'], self.player.Data['Max_HP'])
        self.player.Data['Max_Sanity']=sanity_bar.create_bar(self.player.Data['Sanity'], self.player.Data['Max_Sanity'])
        """Battle States"""
        if self.battle_state == "Pre_round":
            pygame.mouse.set_visible(True)
            if attack_button.update():
                self.turn_check=0
                print(SupportVariables.door)
                self.battle_state = 'Battle_init'
        elif self.battle_state == 'Battle_init':
            Current_Weapon.init_player_attack()
            Current_Weapon.player_attack(self.enemy,False, Settings.dt)
            self.battle_state = 'Battle_start'
        elif self.battle_state == 'Defense':
            if self.attack_board.update(Settings.dt): #successful defense
                self.battle_state = 'Pre_round'
                pygame.mouse.set_visible(True)
            self.cursor.update(Cursor.show, self.attack_board.rect)
            if self.cursor.collide_with_projectiles(self.attack_board.projectiles): #failed defense
                self.enemy.attack()
                pygame.mouse.set_visible(True)
                self.battle_state = 'Pre_round'
        elif self.battle_state == 'attack':
            if Current_Weapon.inflict_damage(self.enemy, True) > 0:
                if Current_Weapon.animation_play(4, 10, 'Attack_', '', Settings.dt):
                    Current_Weapon.inflict_damage(self.enemy, False)
                    if self.enemy.hp <= 0:
                        self.enemy_killed = True
                        self.enemy.death()
                        self.battle_state = 'Battle_end'
                    elif Current_Weapon.turn >= Current_Weapon.attack_speed:
                        self.attack_board = EnemyAttack(self.cursor, self.enemy.damage / 10)
                        self.battle_state = 'Defense'
                        Current_Weapon.turn = 0
                        Current_Weapon.swings = 0
                    else:
                        self.battle_state = 'Battle_start'
            else:
                # No damage to apply; enemy gets a counter if turn quota reached
                if Current_Weapon.turn >= Current_Weapon.attack_speed:
                    self.attack_board = EnemyAttack(self.cursor, self.enemy.damage / 10)
                    self.battle_state = 'Defense'
                else:
                    self.battle_state = 'Battle_start'
        elif self.battle_state == 'Battle_start':
            if not self.enemy_killed:
                Current_Weapon.player_attack(self.enemy,True, Settings.dt)
                if Current_Weapon.turn!=self.turn_check:
                    self.turn_check+=1
                    self.battle_state = 'attack'
                if Current_Weapon.turn >= Current_Weapon.attack_speed:
                    self.attack_board = EnemyAttack(self.cursor, self.enemy.damage / 10)
                    self.battle_state = 'Defense'
                    Current_Weapon.turn = 0
                    Current_Weapon.swings = 0
            if self.enemy.hp <= 0:
                self.enemy_killed = True
                self.enemy.death()
                self.battle_state= 'Battle_end'
        Current_Weapon.animate()
        if self.battle_state != 'attack':
            Current_Weapon.animation_play(1, 5, '', '', Settings.dt)
        """On Timeout"""
        if Main_Timer.update():
            update_data(Player_Data, Game_.Player.Data)
            save_data(Game_ID, Game_.Player.Data)
            if SupportVariables.door != 'Boss':
                self.player.Data['Current_Room'] += 1
                self.scene_manager.create_scene()
                self.scene_manager.set_scene('Corridor')
            else:
                self.scene_manager.set_scene('End')
            self.battle_state = "Pre_round"
            self.enemy_killed = False
            Current_Weapon.frame=1
class SaveSelection(Scene):
    def __init__(self, display, scene_manager):
        super().__init__(display, scene_manager)
    def run(self):
        global Game_ID
        if save_slot1_button.update():
            if Game_ID!=0:
                Game_ID=1
                if load_data(1):
                    Game_.Player.update_stats(Player1.Data)
                    self.scene_manager.set_scene('Corridor')
            else:
                save_data(1, Game_.Player.Data)
                SupportVariables.Running=False
        if save_slot2_button.update():
            if Game_ID!=0:
                Game_ID = 2
                if load_data(2):
                    Game_.Player.update_stats(Player2.Data)
                    print(Player_Data2)
                    self.scene_manager.set_scene('Corridor')
            else:
                save_data(2, Game_.Player.Data)
                SupportVariables.Running=False
class Inventory(Scene):
    def __init__(self, display, scene_manager):
        super().__init__(display, scene_manager)
        self.Running = False
        offset_x = 0
        offset_y = 0
        """slots setup"""
        for i in range(5):
            offset_y = 0
            i = Button(10+offset_x,10,'',150,150,True,80)
            Inventory_slots.add(i)
            offset_x += 200
            for j in range(4):
                j = Button(-190+offset_x,190+offset_y,'',150,150,True,80)
                Inventory_slots.add(j)
                offset_y += 180
        helmet_slot =ImageButton('../Icons','Helmet',1200,10,'',200,200,True)
        chestplate_slot =ImageButton('../Icons','ChestPlate',1200,230,'',200,200,True)
        Equipment_slots.add(helmet_slot)
        Equipment_slots.add(chestplate_slot)
        """items setup"""
        self.note = Notes['Note_test']()
        self.bottle = OneTimeUseItems['Bottle']()
        self.helmet = Equipment_Items['Helmet']()
        Items_group.add(self.helmet)
        Items_group.add(self.note)
        Items_group.add(self.bottle)
    def run(self):
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
    def close_inventory(self,previous_scene):
        self.Running =False
        self.scene_manager.set_scene(previous_scene)
classes = {"Menu": Menu, 'Battle':Battle, 'Corridor': Corridor, 'End':End,
                                'Death':Death,'SaveSelection':SaveSelection,'Inventory':Inventory}
class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.Player = Player0
        self.screen = screen
        self.Enemy =Enemies[SupportVariables.door]()
        self.Fullscreen = Fullscreen
        self.SceneManager = SceneManager('Menu')
        self.SaveSelection_ = SaveSelection(self.screen, self.SceneManager)
        self.Menu_ = Menu(self.screen,self.SceneManager)
        self.Corridor_ = Corridor(self.screen,self.SceneManager,self.Player)
        self.Battle_ = Battle(self.screen,self.SceneManager,self.Player,self.Enemy)
        self.Death_ = Death(self.screen,self.SceneManager)
        self.End_ = End(self.screen,self.SceneManager)
        self.Inventory_ = Inventory(self.screen,self.SceneManager)
        self.Scenes =  {"Menu": self.Menu_, 'Battle':self.Battle_, 'Corridor': self.Corridor_, 'End': self.End_,
                                'Death': self.Death_,'SaveSelection':self.SaveSelection_,'Inventory':self.Inventory_}
    def create_scene(self,scene_name,class_name,*additional_args):
        self.Scenes[scene_name]= class_name(self.screen,self.SceneManager,*additional_args)
    def run(self):
        print(Player_Data)
        while SupportVariables.Running:
            global Game_ID
            screen.fill((0,0,0))
            Settings.dt = time.time()- Settings.previous_time
            Settings.previous_time = time.time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if Game_ID == 0 and self.SceneManager.Game_Running:
                        self.SceneManager.set_scene('SaveSelection')
                        self.SceneManager.Game_Running = False
                    else:
                        SupportVariables.Running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11 and not self.Fullscreen:
                         self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT),
                                                                  FULLSCREEN | SCALED | DOUBLEBUF)
                         self.Fullscreen = True
                    elif event.key == pygame.K_F11 and self.Fullscreen:
                        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), SCALED | DOUBLEBUF)
                        self.Fullscreen = False
                    elif event.key == pygame.K_TAB and not self.Inventory_.Running and not self.SceneManager.current_scene=='Battle':
                        self.SceneManager.previous_scene = self.SceneManager.current_scene
                        self.SceneManager.set_scene('Inventory')
                    elif event.key == pygame.K_TAB and self.Inventory_.Running and not self.SceneManager.current_scene=='Battle':
                        self.Inventory_.close_inventory(self.SceneManager.previous_scene)
            if self.SceneManager.instantiate:
                name = self.SceneManager.get_scene()
                cls = classes[name]
                if name == 'Battle':
                    self.Enemy = Enemies[SupportVariables.door]()
                    self.create_scene(name, cls, self.Player, self.Enemy)
                elif name == 'Corridor':
                    self.create_scene(name, cls, self.Player)
                else:
                    self.create_scene(name, cls)
            self.Scenes[self.SceneManager.get_scene()].run()
            pygame.display.update()
            pygame.display.set_caption("Monochrome Tower")
Game_= Game()
Game_.run()

