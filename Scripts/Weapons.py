from Game_Data import AnimatedObject,SupportVariables,random
from Settings import *
import Settings
class Weapon(AnimatedObject):
    def __init__(self,damage, accuracy, image_name='',image_folder_name='',attack_speed=2, weight=50,x=WINDOW_WIDTH/2.5,y=WINDOW_HEIGHT/2.5):
        super().__init__(image_folder_name,image_name,x,y)
        self.damage = damage
        self.accuracy = accuracy
        self.attack_speed= attack_speed
        self.weight = weight
        self.swings=0
        self.fails=0
        self.hit_mark_direction=1
        self.save_hitbox = 0
        self.hit_mark_sur = pygame.Surface((20, 50))
        self.hit_mark = self.hit_mark_sur.get_frect(center=(220, 525))
        self.hit_area_sur = pygame.Surface((self.accuracy, 50))
        self.hit_area = self.hit_area_sur.get_frect(center=(self.save_hitbox, 525))
        self.dir_changed = False
        self.deal_damage=0
        self.clicked=False
        self.turn=0
        self.border_sur = [pygame.Surface((5,50)),pygame.Surface((5,50))]
        self.borders = [pygame.Surface((5,50)).get_frect(topleft=(230,500)),pygame.Surface((5,50)).get_frect(topright=(685,500))]
        self.end_zone = False
        #self.create_borders()
    def create_borders(self,initial_borders=False):
        if initial_borders:
            for i in self.border_sur:
                i = pygame.Surface((5, 50))
            self.borders = [pygame.Surface((5,50)).get_frect(topleft=(230,500)),pygame.Surface((5,50)).get_frect(topright=(685,500))]
        value =  5 + ((self.weight / 10) * (self.swings+1))  # ensures that the hitmark won't go off bounds
        left_sur = (pygame.Surface((value,50)))
        right_sur = (pygame.Surface((value,50)))
        left_rect = left_sur.get_frect(topleft=(230,500))
        right_rect = right_sur.get_frect(topright=(685,500))
        self.border_sur = [left_sur,right_sur]
        self.borders = [left_rect,right_rect]
        self.border_sur[0].fill('red')
    def collide(self):
        border_hit = any(self.hit_mark.colliderect(i) for i in self.borders)
        if border_hit :
            return True
        return False
    def player_attack(self,enemy,attacked=True,delta=None)->int:
        value = 5 + (self.weight / 10 * (self.swings + 2))
        if delta is None:
            delta = Settings.dt# ensures that the hitmark won't go off bounds
        if self.deal_damage > self.damage * self.attack_speed:
            self.deal_damage = 0
        pygame.draw.rect(screen, 'black', (230, 500, 455, 50))
        pygame.draw.rect(screen, 'white', (230, 500, 455, 50), 5)
        screen.blit(self.hit_area_sur, self.hit_area)
        screen.blit(self.hit_mark_sur, self.hit_mark)

        self.dir_changed=False
        self.hit_area_sur = pygame.Surface((self.accuracy, 50))
        self.hit_area = self.hit_area_sur.get_frect(center=(self.save_hitbox, 525))
        self.hit_mark_sur.fill('white')
        self.hit_area_sur.fill('white')

        self.pressed = pygame.mouse.get_pressed()[0]
        if self.fails >= 2 and self.weight <75 or self.fails >= 4 and self.weight >=75:
            self.swings += 1
            self.turn += 1
            self.fails = 0
            self.dir_changed = True
            self.save_hitbox = random.randint(int(230 + self.accuracy / 2), int(600 - self.accuracy / 2))
        if self.hit_area.colliderect(self.hit_mark):
           self.hit_mark_sur.fill('black')
           if self.pressed and not self.clicked:
               self.clicked=True
               self.deal_damage+=self.damage
               self.swings+=1
               self.fails=0
               self.turn+=1
               self.hit_mark_direction = 1
               self.save_hitbox = random.randint(int(230 + self.accuracy / 2), int(600 - self.accuracy / 2))
               self.hit_mark.x = self.borders[0].right + value
        elif not self.hit_area.colliderect(self.hit_mark):
           self.hit_mark_sur.fill('white')
           if self.pressed and not self.clicked:
                self.clicked=True
                self.swings += 1
                self.turn+=1
                self.fails = 0
                self.hit_mark_direction =1
                self.save_hitbox = random.randint(int(230 + self.accuracy / 2), int(600 - self.accuracy / 2))
        if not attacked:
            self.save_hitbox= random.randint( int(230+self.accuracy/2),int(600-self.accuracy/2))
            attacked=True
            self.dir_changed = True
        else:
            self.create_borders()
        if self.collide() and not self.end_zone: # when hitmark reaches one of the hitbox borders
            self.fails+=1
            self.hit_mark_direction *= -1
            self.dir_changed = True
            self.end_zone = True
        else:
            self.end_zone = False
        if self.swings==self.attack_speed and enemy.hp>0:
            self.swings=0
            self.fails=0
            self.hit_mark_direction=1
            screen.fill('white')

        if self.hit_mark.right < self.borders[0].left: # ensures that the hitmark won't go off bounds'
            self.hit_mark.left = self.borders[0].left +10
        elif self.hit_mark.left > self.borders[1].right:
            self.hit_mark.right = self.borders[1].right -10
        else:
            self.hit_mark.x += (((self.weight / 10) + (
                        self.weight / 10) * self.swings) * self.hit_mark_direction) * delta * 70
        if not self.pressed and self.clicked:
            self.clicked=False
        return self.turn
    def init_player_attack(self):
        self.hit_mark.x = 235 + 5 + (self.weight / 10 * (self.swings + 2))
        self.dir_changed = True
        self.fails = 0
        self.turn=0
        self.swings = 0
        self.hit_mark_direction=1
        self.deal_damage=0
        self.save_hitbox = random.randint(int(230 + self.accuracy / 2), int(600 - self.accuracy / 2))
        self.create_borders(True)#create default borders
        self.clicked = False
        print("Start of round")
    def inflict_damage(self,enemy):
        if self.deal_damage >0:
            enemy.hp -= self.damage
            self.deal_damage=0
RustyBlade = Weapon(25,50,'RustyBlade','../Weapons',3,50,WINDOW_WIDTH/2.5,WINDOW_HEIGHT-450)
Current_Weapon = RustyBlade