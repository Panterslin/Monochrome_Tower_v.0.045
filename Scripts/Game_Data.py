from Scripts import Settings
from Timer import Timer
from Settings import ROOT_DIR
from Save_Handler import *
from Groups import *
import random
from Player import *
from Labels import DynamicLabel
pygame.init()
"""Groups"""
Door_group = pygame.sprite.Group()
import Groups
"""Timers"""
timeout=False
Main_Timer=Timer(0.5,False,False)
class SupportVariables:
    def __init__(self):
        # Global Variables
        self.door = ''
        self.clicked = False
        self.click_checker = False
        self.Rain_Wave_started = False
        # RunStats
        self.Rooms_in_floor = 8
        # Corridors
        self.save_corridor = [0, 0, 0]
        # Battle
        self.hitbox_created = False
        self.battle_started = False
        self.hit_mark_direction = 1
        self.save_hitbox = 0
        #Scenes
        self.Running = True
        self.corridor_created = False
class SceneManager:
    def __init__(self,current_scene):
        self.current_scene=current_scene
        self.previous_scene = None
        self.Game_Running=False
        self.instantiate = False
    def create_scene(self,scene_name,isolate_spr=False):
        self.instantiate = True
        self.current_scene = scene_name
    def get_scene(self):
        self.instantiate = False
        return self.current_scene
    def set_scene(self,scene_name):
        self.current_scene=scene_name
Player0=Player(Default_Data)
Player1=Player(Player_Data)
Player2=Player(Player_Data2)
SupportVariables=SupportVariables()
current_player=Player0

class ImageObject(pygame.sprite.Sprite):
    def __init__(self,image_folder_name:str, image_name:str, x,y,ignore_groups=False):
        super().__init__()
        pygame.sprite.Sprite.__init__(self)
        #Buttons_group.add(self) if not ignore_groups else None
        self.image_folder_name=image_folder_name
        self.anim_name= None
        self.frame=1
        self.image_name = image_name
        self.x = x
        self.y = y
        try:
            if self.anim_name is not None:
                self.image = pygame.image.load(os.path.join(ROOT_DIR,image_folder_name, image_name, image_name + '_' + self.anim_name + str(int(self.frame)) + ".png")).convert_alpha()
            else:
                self.image = pygame.image.load(os.path.join(ROOT_DIR,image_folder_name, image_name, image_name + '_'+ str(int(self.frame)) + ".png")).convert_alpha()
        except FileNotFoundError:
            if self.anim_name is not None:
                self.image = pygame.image.load(os.path.join(ROOT_DIR, image_folder_name, image_name,
                                                    image_name + self.anim_name + str(
                                                        int(self.frame)) + ".png")).convert_alpha()
            else:
                self.image = pygame.image.load(os.path.join(ROOT_DIR,image_folder_name, image_name,
                                                    image_name + str(int(self.frame)) + ".png")).convert_alpha()

        self.rect = self.image.get_frect(center=(x,y))
        self.mask = pygame.mask.from_surface(self.image)
        self.mask_sur = self.create_mask_surface()

    def create_mask_surface(self,mask_alpha=255, image_alpha=None):
        self.mask = pygame.mask.from_surface(self.image)
        mask_sur = self.mask.to_surface(setcolor=(0, 0, 0), unsetcolor=(1, 1, 1))
        mask_sur.set_colorkey((1, 1, 1))
        mask_sur.set_alpha(mask_alpha)
        self.image.set_alpha(image_alpha) if image_alpha is not None else None
        return mask_sur
class AnimatedObject(ImageObject):
    def __init__(self,image_folder_name,image_name:str, x=0,y=0,alt_image=""):
        super().__init__(image_folder_name,image_name,x,y)
        self.is_animating=False
        self.anim_name =''
        self.frame = 1
        self.alt_image= alt_image
    def animate(self):
        self.is_animating=True
    def count_frames(self,anim_type=''):
        if anim_type == '':
            return len(os.listdir(join(ROOT_DIR,self.image_folder_name, self.image_name)))
        else:
            return len(os.listdir(join(ROOT_DIR,self.image_folder_name, self.image_name, anim_type)))
    def animation_play(self,frames=1,anim_speed=0.05,anim_type='',align_type='center',dt=None,background=False,visibility=True,image_size=None)->bool:
        end=False
        self.anim_name=anim_type
        if dt is None:
            dt = Settings.dt
        if self.is_animating:
            try:
                if not background:
                    self.image=pygame.image.load(join(ROOT_DIR,self.image_folder_name, self.image_name, self.image_name + '_' + self.anim_name + str(int(self.frame)) + ".png")).convert_alpha()
                else:
                    self.image=pygame.image.load(join(ROOT_DIR,self.image_folder_name, self.image_name, self.image_name + '_' + self.anim_name + str(int(self.frame)) + ".png")).convert()
            except FileNotFoundError: # different file format
                if not background:
                    self.image=pygame.image.load(join(ROOT_DIR,self.image_folder_name, self.image_name, self.image_name + self.anim_name + str(int(self.frame)) + ".png")).convert_alpha()
                else:
                    self.image=pygame.image.load(join(ROOT_DIR,self.image_folder_name, self.image_name, self.image_name + self.anim_name + str(int(self.frame)) + ".png")).convert()
            self.frame+=anim_speed*dt*3
            if align_type == 'center':
                self.rect = self.image.get_frect(center=(self.x,self.y))
            else:
                self.rect = self.image.get_frect(topleft=(self.x, self.y))
            if image_size is not None:
                self.image = pygame.transform.scale_by(self.image, image_size)
                self.rect = self.image.get_frect(topleft=(self.x, self.y))
            if visibility:
                screen.blit(self.image,self.rect)
            if frames + 1 <= self.frame:
                self.frame=1
                self.is_animating=False
                end=True
        return end
class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image= pygame.surface.Surface((10,10))
        self.image.set_alpha(0)
        self.image.fill('red')
        self.rect = self.image.get_frect()
        self.mask = pygame.mask.from_surface(self.image)
    def update(self,func=None,*args):
        self.rect.topleft = pygame.mouse.get_pos()
        if func is not None:
            func(self,*args)
        screen.blit(self.image,self.rect)
    def show(self,area):
        self.image.set_alpha(255 if self.rect.colliderect(area) else 0)
        pygame.mouse.set_visible(False if self.rect.colliderect(area) else True)
    def collide_with_projectiles(self,group):
        return pygame.sprite.spritecollide(self,group,True)
    def player_cursor_death (self):
        pass
        #print('death')
"""Cursor"""
cursor = Cursor()
def cursor_mask_collide(sender, group) -> bool:
    if pygame.sprite.spritecollide(sender, group, False, pygame.sprite.collide_mask):
        return True
    return False

class Button(pygame.sprite.Sprite):
   button_col = 'black'
   hover_col = 'white'
   text_col = 'white'
   text_hover_col = 'black'
   outline_col = 'white'
   def draw_image(self):
       pass
   def __init__(self,x,y,text,width,height,outline:bool,font_size,custom_font_pos=False,font_pos:tuple=(0,0),ignore_groups=False):
       super().__init__()
       self.x = x
       self.y = y
       self.text = text
       self.width = width
       self.height = height
       self.outline = outline
       self.font_size = font_size
       self.custom_font_pos = custom_font_pos
       self.font_pos = font_pos
       self.clicked = False
       Buttons_group.add(self) if not ignore_groups else None
       self.rect = pygame.FRect(self.x-2,self.y-1,self.width+4,self.height+2)
       self.occupied = False # for buttons acting as slots in inventory
       self.font_type = pygame.font.Font(FONT_PATH, self.font_size)
       self.text_img = self.font_type.render(self.text, True, self.text_col)
       self.text_rect = pygame.rect.FRect((self.font_pos[0],self.font_pos[1]),(self.text_img.get_width(), self.text_img.get_height()))
       self.outline_rect = pygame.FRect(self.x - 7, self.y - 7, self.width + 15, self.height + 15)
       self.rects = [self.rect,self.outline_rect,self.text_rect]
   def update(self,click_check=False):
       action = False
       if click_check and self.clicked:
           self.clicked=False
           SupportVariables.click_check=False
       cursor_pos = pygame.mouse.get_pos()

       if self.outline:
           pygame.draw.rect(screen, self.outline_col, self.outline_rect)
       if self.rect.collidepoint(cursor_pos):
           if pygame.mouse.get_pressed()[0]==1:
               self.clicked = True
               pygame.draw.rect(screen,self.hover_col,self.rect)
               self.text_col='black'
           elif pygame.mouse.get_pressed()[0]==0 and self.clicked:
               pygame.draw.rect(screen,self.button_col,self.rect)
               self.text_col='white'
               action = True
               self.clicked = False
           else:
               pygame.draw.rect(screen,self.hover_col,self.rect)
               self.text_col='black'
       else:
           pygame.draw.rect(screen,self.button_col,self.rect)
           self.text_col='white'
       self.text_img = self.font_type.render(self.text, True, self.text_col)
       self.draw_image()
       screen.blit(self.text_img, (self.rect.centerx - int(self.text_img.get_width() / 2),
                                   self.rect.centery - int(self.text_img.get_height() / 2)))

       return action
class ImageButton(Button):
    def __init__(self,image_folder_name,image_name:str,x,y,text,width,height,outline:bool,image_size_relative=0.31):
        super().__init__(x,y,text,width,height,outline,font_size=80)
        self.image_folder_name = image_folder_name
        self.image_name = image_name
        self.image = pygame.image.load(
            join(ROOT_DIR,image_folder_name,image_name + ".png")).convert_alpha()
        self.image = pygame.transform.scale_by(self.image, image_size_relative)
        self.rect = self.image.get_frect()

        self.rect = self.image.get_frect(topleft=(x, y))
    def draw_image(self):
        screen.blit(self.image,self.rect)
    def hide_image(self,unhide=False):
        if not unhide:
            self.image.set_alpha(0)
        else:
            self.image.set_alpha(255)
class Door(AnimatedObject):
   base_col = 'black'
   door_pos_1= (WINDOW_WIDTH/4,WINDOW_HEIGHT/1.85)
   door_pos_2= (WINDOW_WIDTH/1.9,WINDOW_HEIGHT/1.85)
   door_pos_3 = (WINDOW_WIDTH / 1.23, WINDOW_HEIGHT /1.85)
   def __init__(self,image_folder_name,image_name:str, x,y,alt_img,sanity_value):
       super().__init__(image_folder_name,image_name,x,y,alt_img)
       self.sanity_value = sanity_value
       self.alt_img = alt_img
       self.clicked = False
       Door_group.add(self)
   def create_door(self,door_x,door_y):
       action = False
       alt_image = pygame.image.load(join(ROOT_DIR,'Doors',self.image_name, self.alt_img)).convert_alpha()
       self.rect.x= door_x-200
       self.rect.y = door_y-150
       self.mask = pygame.mask.from_surface(alt_image)
       screen.blit(self.image,self.rect)
       cursor.update()
       if self.rect.collidepoint((cursor.rect.x,cursor.rect.y)):
          if cursor_mask_collide(cursor,Door_group):
                if pygame.mouse.get_pressed()[0]==1 and not self.clicked:
                    self.clicked = True
                    screen.blit(alt_image,self.rect)
                elif pygame.mouse.get_pressed()[0]==0 and self.clicked:
                    screen.blit(self.image,self.rect)
                    action = True
                    self.clicked = False
                    Player0.Data['Sanity'] -=self.sanity_value
                else:
                    screen.blit(alt_image,self.rect)
          else:
                screen.blit(self.image,self.rect)
       return action
class UI:
    rect_color='black'
    def __init__(self,heart_icon,profile_icon,sanity_icon,defense_icon):
        self.heart_icon = heart_icon
        self.profile_icon = profile_icon
        self.sanity_icon = sanity_icon
        self.defense_icon = defense_icon
        self.icons = [defense_icon,heart_icon,profile_icon,sanity_icon]
    def update(self):
        offset =0
        back_rect = pygame.rect.Rect((0, WINDOW_HEIGHT - 140), (520, 200))
        pygame.draw.rect(screen, self.rect_color, back_rect)
        for icon in self.icons:
            if icon != self.profile_icon and icon != self.defense_icon:
                rect = pygame.image.load(join(ROOT_DIR,'UI',icon)).convert_alpha().get_frect(center=(440,WINDOW_HEIGHT-100+offset))
                offset+=60
                screen.blit(pygame.image.load(join(ROOT_DIR,'UI',icon)),rect)
            elif icon == self.defense_icon:
                image = pygame.transform.scale_by(pygame.image.load(join(ROOT_DIR,'UI',icon)).convert(),0.5)
                rect = image.get_frect(center=(490,WINDOW_HEIGHT-70))
                screen.blit(image,rect)
                defense_label = DynamicLabel(str(Player0.Data['Defense']), 'black',rect.x+34-len(str(Player0.Data['Defense']))*8,rect.y+14,FONT_PATH,20)
                defense_label.update()
            elif icon == self.profile_icon:
                rect = pygame.image.load(join(ROOT_DIR,'UI',icon)).convert_alpha().get_frect(center=(70,WINDOW_HEIGHT-70))
                screen.blit(pygame.image.load(join(ROOT_DIR,'UI',icon)),rect)
class ProgressBar:
    lbl_color='black'
    def __init__(self,width, height,x,y):
        self.width = width
        self.height = height
        self.modifier = 2.4
        self.x=x
        self.y=y
    def create_bar(self,value,max_value,include_label=True,excess_values=True)->int:

        if value > max_value:
            if not excess_values:
                value=max_value
                self.modifier =(self.width-self.width/25)/value
            else:
                self.modifier = (self.width-self.width / 25) / max_value
        elif value == max_value:
            self.modifier = (self.width-self.width / 25)/value
            value=max_value
        else:
            self.modifier = (self.width-self.width / 25)/max_value
        pygame.draw.rect(screen, 'white', (self.x, self.y, self.width, self.height))
        depleted = pygame.draw.rect(screen, 'black', (self.x+self.width-self.width/50 -
        int(min(self.width-self.width/25 - self.modifier * value*(self.width/250), self.width-self.width/25))
        ,self.y+self.height/15,int(min(self.width-self.width/25 - self.modifier * value*(self.width/250), self.width-self.width/25)), self.height-self.height/7.5))
        if include_label:

            lbl_font = pygame.font.Font(FONT_PATH, int(self.height - self.height / 3))
            width =0
            for i,letter in enumerate(str(value)+'/'+str(max_value)):
                letter_img = lbl_font.render(letter, True, self.lbl_color)
                letter_rect = letter_img.get_frect(topleft=(self.x + self.width / 3 + width / 1.8,
                                                            self.y - int(self.height) + letter_img.get_height() / 1.1))
                i=0 if letter=='1' else i
                width += letter_img.get_width()*2 if i != 0 else letter_img.get_width()*1.7

                if depleted.colliderect(letter_rect):
                    letter_img = lbl_font.render(letter, True, 'white')
                screen.blit(letter_img,letter_rect)

        return max_value
    def find_label_size(self,value,max_value)->int:
        lbl_font = pygame.font.Font(FONT_PATH, int(self.height - self.height / 3))
        label = lbl_font.render(str(value) + '/' + str(max_value), True, self.lbl_color)
        label_size = label.get_width()
        const_label = label_size
        return const_label
class DecoImage(AnimatedObject):
    def __init__(self,image_folder_name,image_name,x,y):
       super().__init__(image_folder_name,image_name,x,y)

"Deco"
#Corridor_Deco = DecoImage('Corridor','Corridor',0,0)

Vermin_I_Deco = DecoImage('Corridor','VerminNest_I',0,0)
"""ProgressBars"""
hp_bar = ProgressBar(250,30,WINDOW_WIDTH/10,WINDOW_HEIGHT-WINDOW_HEIGHT/7.8)
sanity_bar = ProgressBar(250,30,WINDOW_WIDTH/10,WINDOW_HEIGHT-WINDOW_HEIGHT/16)
"""Doors"""
door0 = Door('Doors','Door0',0,0,'Door0_alt.png',0)
door10 = Door('Doors','Door10',0,0,'Door10_alt.png',10)
door20 = Door('Doors','Door20',0,0,'Door20_alt.png',20)
BossDoor = Door('Doors','BossDoor',0,0,'BossDoor_alt.png',0)
Door_group.add(BossDoor,door20,door10,door0)
"""Dictionaries"""
Doors = {0:door0,10:door10,20:door20,'Boss':BossDoor}
"""UI"""
Base_UI = UI('Heart_Icon.png','Profile_Icon.png','Sanity_Icon.png','Defense_Icon.png')


