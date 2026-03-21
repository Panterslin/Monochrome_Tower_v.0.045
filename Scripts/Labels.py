from Scripts import Settings
import string
from Settings import *
from os.path import join
from Timer import Timer
class Label(pygame.sprite.Sprite):
    def __init__(self, text, color, x, y,font=FONT_PATH,font_size=30,bg_size:tuple=(0,0),bg_pos:tuple=(0,0),background:bool=True,background_color='black'):
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
        self.create_font = pygame.font.Font(self.font, self.font_size)
        self.image = self.create_font.render(self.text, True, self.color)
        self.rect = self.image.get_frect(topleft=(self.x, self.y))
    def update(self,func=None):
        if self.background:
            bg_surface = pygame.Surface(self.bg_size)
            bg_surface.fill(self.background_color)
            screen.blit(bg_surface, (self.bg_pos[0], self.bg_pos[1]))
        if func is None:
            self.image = self.create_font.render(self.text, True, self.color)
            screen.blit(self.image, self.rect)
        else:
            func(self)
    def resize(self,text):
        self.text = text
        self.image = self.create_font.render(self.text, True, self.color)
        self.rect = self.image.get_frect(center=(self.x, self.y))
class DynamicLabel(Label):
    def __init__(self, text, color, x, y, font=FONT_PATH, font_size=30,bg_size: tuple = (0, 0), bg_pos: tuple = (0, 0),
                 background: bool = True, background_color='black',):
        super().__init__(text, color, x, y, font, font_size, bg_size, bg_pos, background,background_color)
    def dynamic_update(self, var):# update the label with variables
        self.text =self.text_const+ str(var)
        self.update()
class AppearingLabel(Label):
    def __init__(self,text_speed,text, color, x, y,font_size=30,font=FONT_PATH,bg_size:tuple=(0,0),bg_pos:tuple=(0,0),background:bool=True,background_color='black'):
        super().__init__(text, color, x, y,font,font_size,bg_size=bg_size,bg_pos=bg_pos,background=background,background_color=background_color)
        self.timer = Timer(text_speed,True,True)
        self.text_speed = text_speed
        self.letterID=0
        self.label =''
        self.final_label = None
        self.fade_time = Timer(self.text_speed/255,True,False)
        self.alpha = 255
        self.digit_multipliers = []
    def dynamic_render(self,flicker=False,digits_as_pauses=False,fading=False,alt_align=False):
        end=False
        target_fade_tick = self.text_speed/255
        if self.fade_time.duration != target_fade_tick:
            self.fade_time.duration=target_fade_tick
        fade_tick = self.fade_time.update()
        if fade_tick:
            self.alpha-=3
        if self.timer.update() or fade_tick:
            if self.timer.duration != self.text_speed:
                self.timer.duration=self.text_speed
            if self.letterID >= len(self.text):
                self.final_label = self.create_font.render(self.label, True, self.color)
                if fading:
                    if not self.fade_time.Active:
                        self.fade_time.activate()
                    if self.alpha <= 0:
                        end = True
                        return end
                if flicker:
                    return end
                elif not flicker and not fading:
                    end = True
            else:
                if self.text[self.letterID].isdigit() and digits_as_pauses:
                    #self.digit_multipliers.append(int(self.text[self.letterID]))
                    self.timer.duration=self.text_speed*int(self.text[self.letterID])
                else:
                    self.label += self.text[self.letterID]
                self.letterID+=1
                self.final_label = self.create_font.render(self.label, True, self.color)
        if self.final_label is not None:
            self.final_label.set_alpha(self.alpha)
            final_rect = self.final_label.get_frect(center=(self.x, self.y)) if not alt_align else self.final_label.get_frect(topleft=(self.x, self.y))
            screen.blit(self.final_label, final_rect)
        return end
class InputArea(Label):
    def __init__(self,color,font,x,y,font_size,bg_size,bg_pos,background,background_color):
        super().__init__(text='',color=color,font=font,x=x,y=y,font_size=font_size,bg_size=bg_size,bg_pos=bg_pos,background=background,background_color=background_color)
        self.flash_timer = Timer(0.5,True,True)
        self.flash=False
        self.blinked =False
    def flash_func(self,duration=None):

        if duration is not None:
            self.flash_timer.duration=duration
        if self.flash_timer.update():
            self.blinked=False
            self.flash = not self.flash
        if not self.flash and not self.blinked:
            if len(self.text)>0:
                if self.text[len(self.text) - 1] != '_' :
                    self.text += '_'
            else:
                    self.text+='_'
            self.blinked=True
        elif self.flash and not self.blinked:
            if len(self.text)>0:
                if self.text[len(self.text)-1] == '_':
                    self.text = self.text[:-1]
            else:
                self.text = self.text[:-1]
            self.blinked=True
        for i,letter in enumerate(self.text):
            if letter == '_' and i is not len(self.text)-1:
                letter = self.text[i+1]
                self.text = self.text[:i]
                self.text += letter
                print('_')



"""Labels"""
title_lbl = AppearingLabel(0.3,"Monochrome Tower", 'white',WINDOW_WIDTH/2,WINDOW_HEIGHT/20+60,80,FONT_PATH,(800,90),(WINDOW_WIDTH/4,70))
death_lbl= Label("Fallen into oblivion...",'white',WINDOW_WIDTH/4,WINDOW_HEIGHT/20,FONT_PATH,80)
room_score = DynamicLabel("Room: " , 'white', WINDOW_WIDTH/20, WINDOW_HEIGHT/20+WINDOW_HEIGHT/20, FONT_PATH, 40, (200,100),(50,50))
floor_score = DynamicLabel("Floor: ", 'white', WINDOW_WIDTH/20, WINDOW_HEIGHT/20, FONT_PATH, 40,(0,0),(0,0))
victory_label = Label("Game Completed", 'white', WINDOW_WIDTH/4, WINDOW_HEIGHT/20, FONT_PATH, 80,(600,600),(200,150))
#turn_label = Label()