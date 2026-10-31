from Scripts import Groups, Settings
from Scripts.Game_Data import AnimatedObject, Player0
from Scripts.Items import OneTimeUseItems
from Settings import *
from Game_Data import ImageObject, Button, SupportVariables
from Labels import AppearingLabel,InputArea
from Groups import Input_group,Overworld_items_group
from Items import Equipment_Items,Items_group
from Dialogue_Handler import Test
from LevelHandler import LevelHandler
import random
class Scene:
    def __init__(self,scene_manager=None):
        self.scene_manager = scene_manager
class Bile(Scene):
    def __init__(self,scene_manager=None,level_handler=None):
        super().__init__(scene_manager=scene_manager)
        self.levelHandler = level_handler
        self.Button = Button(WINDOW_WIDTH/10,WINDOW_HEIGHT/3.1,'TURN BACK',350,70,True,50,
                             True,(WINDOW_WIDTH/8.5,WINDOW_HEIGHT/3.2))
        self.Button2 = Button(WINDOW_WIDTH/1.5,WINDOW_HEIGHT/3.1,'TOUCH',200,70,True,50,
                              True,(WINDOW_WIDTH/1.49,WINDOW_HEIGHT/3.2))
        self.BileIntro = ImageObject('Scenes','BileIntro',WINDOW_WIDTH/2,WINDOW_HEIGHT/2)
        self.Label = AppearingLabel(0.03,'Silence                        fills the room99','white',200,50,80)
    def run(self):
            screen.blit(self.BileIntro.image,self.BileIntro.rect)
            if self.Button.update():
                self.scene_manager.create_scene('Corridor')
                self.levelHandler.current_room -=1
                self.levelHandler.load_corridor(Player0.Data['Corridor'])
            if self.Button2.update():
               SupportVariables.current_enemy = 'Bile'
               self.scene_manager.create_scene('Battle')
            self.Label.dynamic_render(False,True,True,True)
class Fireplace(Scene):
    def __init__(self,scene_manager=None,player=None):
        super().__init__(scene_manager)
        self.player = player
        self.Fireplace = ImageObject('Scenes','Fireplace',WINDOW_WIDTH/2,WINDOW_HEIGHT/2)
        self.Label = AppearingLabel(0.03,'FEEL THE WARMTH','white',WINDOW_WIDTH/2,50,80)
        self.Label2 = AppearingLabel(0.03,'YOU FEEL REJUVENATED','white',WINDOW_WIDTH/2,50,80)
        self.Button = Button(WINDOW_WIDTH/6,WINDOW_HEIGHT/3.1,'REST',200,70,True,50)
        self.Button2 = Button(WINDOW_WIDTH/1.5,WINDOW_HEIGHT/3.1,'MEDITATE',300,70,True,50)
        self.start_render=False
    def run(self):
        screen.blit(self.Fireplace.image,self.Fireplace.rect)
        self.Label.dynamic_render(False,False,True)
        if self.Button.update():
            self.player.Data['HP'] = self.player.Data['Max_HP']
            self.start_render=True
        if self.Button2.update():
            self.player.Data['Sanity'] = self.player.Data['Max_Sanity']
            self.start_render = True
        if self.start_render:
            if self.Label2.dynamic_render(False,False,True):
                self.scene_manager.create_scene('Corridor')
class Riddle(Scene):
    def __init__(self,scene_manager=None):
        super().__init__(scene_manager)
        self.input = InputArea('white',FONT_PATH,220,WINDOW_HEIGHT-200, 80,(1000,150),(20,WINDOW_HEIGHT),True,'black')
        Input_group.add(self.input)
        self.Riddler = AnimatedObject('NPCS','Riddler',WINDOW_WIDTH/2,WINDOW_HEIGHT-750,image_size=6)
        self.Riddle = random.choice(Active_Riddles)
        self.label = AppearingLabel(0.03,self.Riddle[1],'white',100,100,60)
        self.wrong_answer_label = AppearingLabel(0.03,"Wrong",'white',WINDOW_WIDTH/1.4,WINDOW_HEIGHT/7,80)
        self.checked=False
        self.Reward = None
        self.test_dialogue = Test()
        self.run_dialogue = False
    def run(self):
        if pygame.mouse.get_pressed()[0] and self.Riddler.rect.collidepoint(pygame.mouse.get_pos()):
            self.run_dialogue = True

        self.Riddler.animate()
        self.label.dynamic_render(False,False,False,True)
        self.Riddler.animation_play(2,4,'','',Settings.dt,False,True,6) if not self.checked else \
             self.Riddler.animation_play(2,4,'pointing_','topleft',Settings.dt,False,True,6)
        self.input.update()
        self.input.flash_func()
        text =''
        if self.checked:
            for letter in self.input.text:
                if letter != '_':
                    text += letter
            if self.Riddle[0] == text and self.Reward is not None:
                self.Reward.image.set_alpha(255)
                self.Reward.disabled = False
                Overworld_items_group.add(self.Reward)
                if self.Reward.display_in_overworld(self.scene_manager,(WINDOW_WIDTH/1.8,WINDOW_HEIGHT/7),1.8):  # if reward is taken
                    print('Item Taken')
                    Overworld_items_group.remove(self.Reward)
                    Items_group.add(self.Reward)
                    self.Riddler.animate()
                    Active_Riddles.remove(self.Riddle)
                    self.scene_manager.create_scene('Corridor')
                    Input_group.remove(self.input)
                    self.checked=False
                    self.Reward.stack()
            else:
                self.Reward.kill()
                if self.wrong_answer_label.dynamic_render(False, False, True,True):
                    self.scene_manager.create_scene('Corridor')
                    Input_group.remove(self.input)
                    self.checked=False
        self.test_dialogue.update() if self.run_dialogue else None

    def check_answer(self):
        if not self.checked:
            self.Reward = self.Riddle[2]()
            Items_group.remove(self.Reward)
            self.Reward.image.set_alpha(0)
            self.Reward.disabled = True
        self.checked=True

Riddles = [
     ['TIME','Even though \n I control your entire\n existence you can never\n get enough of me \n What am I?', Equipment_Items['Sack']],
     ['ABYSS', 'I stare back\n invisible eyes\n peering into you\n What am I?', Equipment_Items['Crusade']],
     ['HAPPINESS', 'The wiser you get,\n the harder I am to find\n What am I?', OneTimeUseItems['Powdered Happiness']]
]
Active_Riddles= Riddles.copy()



