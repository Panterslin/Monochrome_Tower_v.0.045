from Timer import Timer
from Settings import screen,WINDOW_WIDTH,WINDOW_HEIGHT,clock,pygame
from Save_Handler import *
import random
pygame.init()
"""Groups"""
Door_group = pygame.sprite.Group()
"""Timers"""
timeout=False
Main_Timer=Timer(0.5,False,False)
class SupportVariables:
    def __init__(self):
        # Global Variables
        self.door = 0
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
    def create_scene(self):
        self.instantiate = True
    def get_scene(self):
        self.instantiate = False
        return self.current_scene
    def set_scene(self,scene_name):
        self.current_scene=scene_name
class Player:
    def __init__(self,save_data_:dict):
        self.Data = save_data_
    def update_stats(self,player_data:dict):
        self.Data= player_data
    def reset_stats(self):
        self.Data['HP'] = 100
        self.Data['Sanity'] = 150
        self.Data['Max_HP'] = 100
        self.Data['Max_Sanity'] = 150
        self.Data['Current_Floor'] = 1
        self.Data['Current_Room'] = 1
        self.Data['Level'] = 1
Player0=Player(Default_Data)
Player1=Player(Player_Data)
Player2=Player(Player_Data2)
SupportVariables=SupportVariables()
class PhysicsObject(pygame.sprite.Sprite):
    def __init__(self,pos:tuple,velocity:float,max_velocity:int,acceleration:float,target_pos:tuple,color,group,size:tuple):
        super().__init__()
        self.velocity = velocity
        self.Group = group
        #self.Group.add(self)
        self.size= size
        self.image = pygame.surface.Surface((self.size[0], self.size[1]), flags=pygame.SRCALPHA)
        self.acceleration = acceleration
        self.min_acceleration = self.acceleration/10
        self.target_pos = target_pos
        self.color= color
        self.rect = self.image.get_frect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.max_velocity=max_velocity
        self.direction= pygame.math.Vector2()
        self.chase=True
    def hide(self,area=None,*args):
        inside_area = self.rect.colliderect(area) if area is not None else True
        hits_border = any(self.rect.colliderect(r) for r in args)
        self.image.set_alpha(255 if inside_area and not hits_border else 0)
    def update(self,dt=clock.tick(60)/1000,area=None,*args)->bool:
        self.hide(area,*args)
        self.image.fill(self.color)
        screen.blit(self.image,self.rect)
        if self.target_pos[0]>self.rect.x and self.target_pos[1]>self.rect.y:
            self.direction = (1,1)
        elif self.target_pos[0]<self.rect.x and self.target_pos[1]<self.rect.y:
            self.direction = (-1,-1)
        elif self.target_pos[0]<self.rect.x and self.target_pos[1]>self.rect.y:
            self.direction = (-1,1)
        elif self.target_pos[0]>self.rect.x and self.target_pos[1]<self.rect.y:
            self.direction = (1,-1)
        if abs(self.rect.x-self.target_pos[0]) < self.velocity* dt and abs(self.target_pos[1]-self.rect.y) < self.velocity* dt:
            self.velocity=0
            return True
        if self.velocity<self.max_velocity:
                self.velocity += self.acceleration * dt
                self.rect.x += self.velocity * self.direction[0] * dt
                self.rect.y += self.velocity * self.direction[1] * dt
        else:
            self.velocity=0
            return True
        return False
    def update_target_pos(self,target_pos:tuple):
        self.target_pos = target_pos
        print(self.target_pos)
class ImageObject(pygame.sprite.Sprite):
    def __init__(self,image_folder_name:str, image_name:str, x,y):
        super().__init__()
        pygame.sprite.Sprite.__init__(self)
        self.image_folder_name=image_folder_name
        self.anim_name= None
        self.frame=1
        self.image_name = image_name
        self.x = x
        self.y = y
        if self.anim_name is not None:
            self.image = pygame.image.load(join(image_folder_name, image_name, image_name + '_' + self.anim_name + str(int(self.frame)) + ".png")).convert_alpha()
        else:
            self.image = pygame.image.load(join(image_folder_name, image_name, image_name + '_'+ str(int(self.frame)) + ".png")).convert_alpha()

        self.rect = self.image.get_frect(center=(x,y))
        self.mask = pygame.mask.from_surface(self.image)
class AnimatedObject(ImageObject):
    def __init__(self,image_folder_name,image_name:str, x=0,y=0,alt_image=""):
        super().__init__(image_folder_name,image_name,x,y)
        self.is_animating=False
        self.anim_name =''
        self.frame = 1
        self.alt_image= alt_image
    def animate(self):
        self.is_animating=True
    def animation_play(self,frames,anim_speed,anim_type='',align_type='center',dt=clock.tick(60)/1000,background=False,visibility=True)->bool:
        end=False
        self.anim_name=anim_type
        if self.is_animating:
            if not background:
                self.image=pygame.image.load(join(self.image_folder_name, self.image_name, self.image_name + '_' + self.anim_name + str(int(self.frame)) + ".png")).convert_alpha()
            else:
                self.image=pygame.image.load(join(self.image_folder_name, self.image_name, self.image_name + '_' + self.anim_name + str(int(self.frame)) + ".png")).convert()
            self.frame+=anim_speed*dt
            if align_type == 'center':
                self.rect = self.image.get_frect(center=(self.x,self.y))
            else:
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
        print('death')
"""Cursor"""
cursor = Cursor()
def cursor_mask_collide(sender, group) -> bool:
    if pygame.sprite.spritecollide(sender, group, False, pygame.sprite.collide_mask):
        return True
    return False
class Label(pygame.sprite.Sprite):
    def __init__(self, text, color, x, y,font,font_size,bg_size:tuple=(0,0),bg_pos:tuple=(0,0),background:bool=True,background_color='black'):
        super().__init__()
        self.text = text
        self.text_const = text
        self.color = color
        self.x = x
        self.y = y
        self.font = font
        self.font_size = font_size
        self.background = background
        self.background_color = background_color
        self.bg_size = bg_size
        self.bg_pos = bg_pos
    def update(self):
        if self.background:
            bg_surface = pygame.Surface(self.bg_size)
            screen.blit(bg_surface, (self.bg_pos[0], self.bg_pos[1]))
            bg_surface.fill(self.background_color)
        create_font = pygame.font.Font(join('../Fonts', self.font), self.font_size)
        label = create_font.render(self.text, True, self.color)
        screen.blit(label, (self.x, self.y))
class DynamicLabel(Label):
    def __init__(self, text, color, x, y, font, font_size,bg_size: tuple = (0, 0), bg_pos: tuple = (0, 0),
                 background: bool = True, background_color='black',):
        super().__init__(text, color, x, y, font, font_size, bg_size, bg_pos, background,background_color)
    def dynamic_update(self, var):# update the label with variable
        self.text =self.text_const+ str(var)
        self.update()
class Button(pygame.sprite.Sprite):
   button_col = 'black'
   hover_col = 'white'
   text_col = 'white'
   text_hover_col = 'black'
   outline_col = 'white'
   def draw_image(self):
       pass
   def __init__(self,x,y,text,width,height,outline:bool,font_size,custom_font_pos=False,font_pos:tuple=(0,0)):
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
       self.rect = pygame.FRect(self.x-2,self.y-1,self.width+4,self.height+2)
       self.occupied = False # for buttons acting as slots in inventory
   def update(self,click_check=False):
       action = False
       if click_check and self.clicked:
           self.clicked=False
           SupportVariables.click_check=False
       cursor_pos = pygame.mouse.get_pos()
       font_type = pygame.font.Font('../Fonts/PixelFont.ttf', self.font_size)
       outline_rect = pygame.FRect(self.x-7,self.y-7,self.width+15,self.height+15)
       if self.outline:
           pygame.draw.rect(screen, self.outline_col, outline_rect)
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
       text_img = font_type.render(self.text, True, self.text_col)
       text_len = text_img.get_width()
       if not self.custom_font_pos:
        if self.font_size <= self.height:
            screen.blit(text_img, (self.x+int(self.width/2)-int(text_len/2)+3, self.y-int(self.height)+self.font_size))
        else:
            screen.blit(text_img, (self.x + int(self.width / 2) - int(text_len / 2) + 3,self.y - int(self.height) + self.font_size/2+3))
       else:
           screen.blit(text_img,(self.font_pos[0],self.font_pos[1]))
       self.draw_image()
       return action
class ImageButton(Button):
    def __init__(self,image_folder_name,image_name:str,x,y,text,width,height,outline:bool,image_size_relative=0.31):
        super().__init__(x,y,text,width,height,outline,font_size=80)
        self.image_folder_name = image_folder_name
        self.image_name = image_name
        self.image = pygame.image.load(
            join(image_folder_name,image_name + ".png")).convert_alpha()
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
   def create_door(self,door_x,door_y):
       action = False
       alt_image = pygame.image.load(join('../Doors',self.image_name, self.alt_img)).convert_alpha()
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
    def __init__(self,heart_icon,profile_icon,sanity_icon):
        self.heart_icon = heart_icon
        self.profile_icon = profile_icon
        self.sanity_icon = sanity_icon
    def update(self):
        back_rect = pygame.rect.Rect((0, WINDOW_HEIGHT - 140), (500, 200))
        pygame.draw.rect(screen, self.rect_color, back_rect)
        heart_image = pygame.image.load(join('../UI', self.heart_icon)).convert_alpha()
        heart_rect = heart_image.get_frect(center=(450,WINDOW_HEIGHT-100))
        screen.blit(heart_image,heart_rect)
        sanity_image = pygame.image.load(join('../UI', self.sanity_icon)).convert_alpha()
        sanity_rect = sanity_image.get_frect(center=(450, WINDOW_HEIGHT - 40))
        screen.blit(sanity_image, sanity_rect)
        profile_image = pygame.image.load(join('../UI', self.profile_icon)).convert_alpha()
        profile_rect = profile_image.get_frect(center=(70, WINDOW_HEIGHT - 70))
        screen.blit(profile_image, profile_rect)
class ProgressBar:
    lbl_color='black'
    def __init__(self,width, height,x,y):
        self.width = width
        self.height = height
        self.modifier = 2.4
        self.x=x
        self.y=y
    def create_bar(self,value,max_value,include_label=True)->int:
        if value > max_value:
            max_value = value
            self.modifier =(self.width-self.width/25)/value
        elif value == max_value:
            self.modifier = (self.width-self.width / 25)/value
            value=max_value
        else:
            self.modifier = (self.width-self.width / 25)/max_value
        pygame.draw.rect(screen, 'white', (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, 'black', (self.x+self.width-self.width/50 -
        int(min(self.width-self.width/25 - self.modifier * value*(self.width/250), self.width-self.width/25))
        ,self.y+self.height/15,int(min(self.width-self.width/25 - self.modifier * value*(self.width/250), self.width-self.width/25)), self.height-self.height/7.5))
        if include_label:

            lbl_font = pygame.font.Font('../Fonts/PixelFont.ttf', int(self.height - self.height / 3))
            label = lbl_font.render(str(value)+'/'+str(max_value), True, self.lbl_color)
            label_size=self.find_label_size(value,max_value)
            screen.blit(label,(self.x+self.width/2-label_size/2,self.y-int(self.height)+label_size/2.8))

            if max_value/2+label_size/5.5 > value > max_value/2:
                label=lbl_font.render(str(value)+'/'+str(int(max_value)), True, self.lbl_color)
                label2=lbl_font.render(str(max_value)[len(str(max_value))-1], True, 'white')
                screen.blit(label,(self.x+self.width/2-label_size/2,self.y-int(self.height)+label_size/2.8))
                screen.blit(label2,(self.x+self.width/2+label_size/3,self.y-int(self.height)+label_size/2.8))
            elif value<max_value/2:
                label = lbl_font.render(str(value) + '/' + str(int(max_value)), True, 'white')
                screen.blit(label,
                            (self.x + self.width / 2 - label_size / 2, self.y - int(self.height) + label_size / 2.8))

        return max_value
    def find_label_size(self,value,max_value)->int:
        lbl_font = pygame.font.Font('../Fonts/PixelFont.ttf', int(self.height - self.height / 3))
        label = lbl_font.render(str(value) + '/' + str(max_value), True, self.lbl_color)
        label_size = label.get_width()
        const_label = label_size
        return const_label
class DecoImage(AnimatedObject):
    def __init__(self,image_folder_name,image_name,x,y):
       super().__init__(image_folder_name,image_name,x,y)
def rng_pos()->int:
    random_int = random.randint(-int(WINDOW_WIDTH/3.5),int(WINDOW_WIDTH/2.5))
    if random_int%30!=0:
        return rng_pos()
    else:
        return random_int
def rng_size()->int:
    random_int = random.randint(5,20)
    return random_int
"Deco"
#Corridor_Deco = DecoImage('Corridor','Corridor',0,0)

Vermin_I_Deco = DecoImage('../Corridor','VerminNest_I',0,0)
"""ProgressBars"""
hp_bar = ProgressBar(250,30,WINDOW_WIDTH/10,WINDOW_HEIGHT-WINDOW_HEIGHT/7.8)
sanity_bar = ProgressBar(250,30,WINDOW_WIDTH/10,WINDOW_HEIGHT-WINDOW_HEIGHT/16)
"""Doors"""
door0 = Door('../Doors','Door0',0,0,'Door0_alt.png',0)
door10 = Door('../Doors','Door10',0,0,'Door10_alt.png',10)
door20 = Door('../Doors','Door20',0,0,'Door20_alt.png',20)
BossDoor = Door('../Doors','BossDoor',0,0,'BossDoor_alt.png',0)
Door_group.add(BossDoor,door20,door10,door0)
"""Dictionaries"""
Doors = {0:door0,10:door10,20:door20,'Boss':BossDoor}
"""Buttons"""
start = Button(WINDOW_WIDTH/2-145, WINDOW_HEIGHT/2, 'START',290,90,True,75)
info = Button(WINDOW_WIDTH*0.9, WINDOW_HEIGHT*0.9, 'i',50,50,True,55)
return_menu= Button(WINDOW_WIDTH/2-145, WINDOW_HEIGHT/2, 'Return',290,90,True,75)
continue_button = Button(WINDOW_WIDTH/2-145, WINDOW_HEIGHT/1.5, 'Continue',290,90,True,60,True,(WINDOW_WIDTH/2.4,WINDOW_HEIGHT/1.53))
save_slot1_button = Button(WINDOW_WIDTH/4-145, 20, 'Slot1',290,WINDOW_HEIGHT-50,True,75,True,(300,WINDOW_HEIGHT/2.5))
save_slot2_button = Button(WINDOW_WIDTH/2,20,'Slot2',290,WINDOW_HEIGHT-50,True,75,True,(850,WINDOW_HEIGHT/2.5))
attack_button = Button(WINDOW_WIDTH/2-300, WINDOW_HEIGHT/2, 'ATTACK',290,90,True,65,True,(WINDOW_WIDTH/2-295, WINDOW_HEIGHT/2-10))
"""Labels"""
title_lbl = Label("Monochrome Tower", 'white',WINDOW_WIDTH/4,WINDOW_HEIGHT/20,'PixelFont.ttf',80,(800,120),(80,90))
death_lbl= Label("Fallen into oblivion...",'white',WINDOW_WIDTH/4,WINDOW_HEIGHT/20,'PixelFont.ttf',80)
room_score = DynamicLabel("Room: " , 'white', WINDOW_WIDTH/20, WINDOW_HEIGHT/20+WINDOW_HEIGHT/20, 'PixelFont.ttf', 40, (200,100),(50,50))
floor_score = DynamicLabel("Floor: ", 'white', WINDOW_WIDTH/20, WINDOW_HEIGHT/20, 'PixelFont.ttf', 40,(0,0),(0,0))
victory_label = Label("Game Completed", 'white', WINDOW_WIDTH/4, WINDOW_HEIGHT/20, 'PixelFont.ttf', 80,(600,600),(200,150))
#turn_label = Label()
"""UI"""
Base_UI = UI('Heart_Icon.png','Profile_Icon.png','Sanity_Icon.png')
def create_corridor(corridor_signed) -> str:
    corridor = [0, 0, 0]
    corridor_door_pos = [Door.door_pos_1, Door.door_pos_2, Door.door_pos_3]
    current_scene = 'Corridor'

    def rng_door() -> int:

        rand = random.randint(0, 20)

        if rand % 10 != 0:
            return rng_door()
        else:
            return rand

    if not corridor_signed:
        corridor[0] = rng_door()
        corridor[1] = rng_door()
        corridor[2] = rng_door()

        SupportVariables.save_corridor = [corridor[0], corridor[1], corridor[2]]
        print(corridor)
    else:
        corridor[0] = SupportVariables.save_corridor[0]
        corridor[1] = SupportVariables.save_corridor[1]
        corridor[2] = SupportVariables.save_corridor[2]
    Doors[corridor[2]].animate(), Doors[corridor[1]].animate(), Doors[corridor[0]].animate()

    if Player0.Data['Current_Room'] != SupportVariables.Rooms_in_floor:
        for i in range(3):
            try:
                Doors[corridor[i]].animation_play(4, 5, '', 'center', clock.tick(60) / 1000, False, False)
            except:
                pass
        if Doors[corridor[0]].create_door(corridor_door_pos[0][0], corridor_door_pos[0][1]):
            SupportVariables.corridor_created = False
            current_scene = 'Battle'
            SupportVariables.door = corridor[0]
        if Doors[corridor[1]].create_door(corridor_door_pos[1][0], corridor_door_pos[1][1]):
            SupportVariables.corridor_created = False
            current_scene = 'Battle'
            SupportVariables.door = corridor[1]
        if Doors[corridor[2]].create_door(corridor_door_pos[2][0], corridor_door_pos[2][1]):
            SupportVariables.corridor_created = False
            current_scene = 'Battle'
            SupportVariables.door = corridor[2]
    else:
        if Doors['Boss'].create_door(corridor_door_pos[1][0], corridor_door_pos[1][1]):
            print('Boss')
            SupportVariables.corridor_created = False
            current_scene = 'Battle'
            SupportVariables.door = 'Boss'
    return current_scene

