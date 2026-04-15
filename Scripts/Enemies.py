
from pygame import mouse
from Game_Data import AnimatedObject,SupportVariables,Player0,Main_Timer,cursor,random,timeout
from Scripts.Labels import AppearingLabel
from Settings import *
from Labels import Label
import Settings

class EnemyProjectile(pygame.sprite.Sprite):
    def __init__(self,pos:tuple,color,group,size:tuple):
        super().__init__()
        self.pos = pos
        self.color = color
        self.Group = group
        self.size = size
        self.image = pygame.surface.Surface((self.size[0], self.size[1]), flags=pygame.SRCALPHA)
        self.rect = self.image.get_frect()
        self.rect.center = pos
    def collide(self, player) -> bool:
        if self.rect.colliderect(player) and self.image.get_alpha() ==255:
            return True
        return False
class DynamicEnemyProjectile(EnemyProjectile):
    def __init__(self,pos:tuple,velocity:float,max_velocity:int,acceleration:float,target_pos:tuple,color,group,size:tuple):
        super().__init__(pos,color,group,size)
        self.velocity = velocity
        self.image = pygame.surface.Surface((self.size[0], self.size[1]), flags=pygame.SRCALPHA)
        self.acceleration = acceleration
        self.min_acceleration = self.acceleration / 10
        self.target_pos = target_pos
        self.color = color
        self.rect = self.image.get_frect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.max_velocity = max_velocity
        self.direction = pygame.math.Vector2()
class DelayedSeekingProjectile(DynamicEnemyProjectile):
    def __init__(self,group=None,target_pos=(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]),pos=(0,0),velocity=0,max_velocity=150,acceleration=0.05,color='white',size=(10,10)):
        super().__init__(pos,velocity,max_velocity,acceleration,target_pos,color,group,size)
        self.chase=True
    def hide(self,area=None,*args):
        inside_area = self.rect.colliderect(area) if area is not None else True
        hits_border = any(self.rect.colliderect(r) for r in args)
        self.image.set_alpha(255 if inside_area and not hits_border else 50)
    def update(self,dt=None,area=None,*args)->bool:
        if dt is None:
            dt=Settings.dt
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
class StaticProjectile(EnemyProjectile):
    def __init__(self,pos:tuple,color,group,size:tuple,lifetime=3,appearing_speed=5):
        super().__init__(pos,color,group,size)
        self.image.set_alpha(20)
        self.alpha = 20
        self.appearing_speed = appearing_speed
        self.lifetime = lifetime
    def appear(self,dt=None):
        self.alpha += Settings.dt*self.appearing_speed if dt is None else dt*self.appearing_speed
        self.image.set_alpha(int(self.alpha))
        if self.alpha >= 255:
            return True
        return False
    def disappear(self,dt=None,just_check=False):
        if just_check:
            return self.alpha <= 0
        self.alpha -= Settings.dt*self.appearing_speed*5 if dt is None else dt*self.appearing_speed*5
        self.image.set_alpha(int(self.alpha))
        if self.alpha <= 20:
            self.kill()
            return True
        return False
    def update(self,dt=None):
        if self.lifetime <= 0:
            self.disappear(dt)
            self.image.fill(self.color)
            screen.blit(self.image, self.rect)
            return
        if self.appear(dt):
            self.lifetime -= 1 * Settings.dt
        self.image.fill(self.color)
        screen.blit(self.image,self.rect)
class EnemyAttack(pygame.sprite.Sprite):
    def __init__(self, name='', damage_multiplier=1.0,difficulty=1.0, cost=1, effect="",total_time=10):
        super().__init__()
        self.damage_multiplier = damage_multiplier
        self.name = name
        self.difficulty = difficulty
        self.cost = cost
        self.effect = effect
        self.time=0
        self.time_elapsed=0
        self.total_time=total_time
        self.lbl_pause = '999'

class EnemyAttackBoard(EnemyAttack):
    def __init__(self, name='', p_cursor=cursor, damage_multiplier=1,difficulty=1, cost=1, effect="", total_time=10, number_of_projectiles=30, projectile_speed=500, projectile_size=(10,10),
                 projectile_types=(DelayedSeekingProjectile,StaticProjectile)):
        super().__init__(name,damage_multiplier,difficulty,cost,effect,total_time)
        self.image = pygame.Surface((500, 500))
        self.rect = self.image.get_frect(center=(300, 500))
        if projectile_types is None:
            projectile_types = ['Seeking']
        self.cursor = p_cursor
        self.projectile_types = projectile_types
        self.board_border_surfaces = []
        self.board_border=[]
        self.number_of_projectiles = number_of_projectiles
        self.projectile_speed = projectile_speed
        self.projectile_size = projectile_size
        self.attack_lbl = AppearingLabel(0.05, self.name + self.lbl_pause, 'white', self.rect.centerx,
                                         self.rect.centery - 295, 50) if self.rect is not None else None
        self.projectiles = pygame.sprite.Group()
        self.projectiles_seek = pygame.sprite.Group()
        pygame.mouse.set_pos(self.rect.center)
        self.set_borders()
    def set_borders(self):
        for i in range(2):
            self.board_border_surfaces.append(pygame.Surface((500,10)))
            self.board_border_surfaces.append(pygame.Surface((10,510)))
        for i in self.board_border_surfaces:
            i.fill('white')
        self.board_border.append(self.board_border_surfaces[0].get_frect(topleft=(self.rect.left,self.rect.bottom-10)))
        self.board_border.append(self.board_border_surfaces[1].get_frect(topright=(self.rect.right,self.rect.top-10)))
        self.board_border.append(self.board_border_surfaces[2].get_frect(topright=(self.rect.right, self.rect.top-10)))
        self.board_border.append(self.board_border_surfaces[3].get_frect(topleft=(self.rect.left-10, self.rect.top-10)))
    def spawn_pos_rng(self,static=False):
        posx = random.randint(int(self.rect.left), int(self.rect.right))
        posy = random.randint(int(self.rect.top), int(self.rect.bottom))
        if static:
            return posx,posy
        if abs(posx -mouse.get_pos()[0])<50 or abs(posy -mouse.get_pos()[1])<50:
            return self.spawn_pos_rng()
        return posx,posy
    def set_projectiles_target(self, target_pos):
        reach_eps = 2.0
        for p in self.projectiles:
            if not isinstance(p, DelayedSeekingProjectile):
                 continue
            dx = (p.target_pos[0] - p.rect.x)
            dy = (p.target_pos[1] - p.rect.y)
            if (dx * dx + dy * dy) ** 0.5 <= reach_eps:
                p.update_target_pos(target_pos)
                p.velocity = 0
    def create_projectiles(self,number):
        def construct_projectile(projectile_cls):
            spawn_pos = (
                pygame.mouse.get_pos()[0] + self.spawn_pos_rng()[0],
                pygame.mouse.get_pos()[1] + self.spawn_pos_rng()[1]
            )

            rand_size = (random.randint(int((self.projectile_size[0] / 2) * self.difficulty),
                                        int(self.projectile_size[0] * self.difficulty)))
            static_spawn_pos = (
                self.spawn_pos_rng(True)[0],
                self.spawn_pos_rng(True)[1]
            )
            try:
                p = projectile_cls(
                    group=None,
                    target_pos=(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]),
                    pos=spawn_pos,
                    velocity=0,
                    max_velocity=random.randint(int(self.projectile_speed / 2 * self.difficulty / 2),
                                                int(self.projectile_speed * self.difficulty / 2)),
                    acceleration=random.randint(int(self.projectile_speed / 4 * self.difficulty / 2),
                                                int(self.projectile_speed / 2 * self.difficulty / 2)),
                    color='white',
                    size=(rand_size, rand_size) if rand_size > 10 else (10, 10)
                )
            except:
                p = projectile_cls(
                    group=None,
                    pos=static_spawn_pos,
                    color='white',
                    size=(rand_size * 2, rand_size * 2) if rand_size > 10 else (10, 10),
                    lifetime=2,
                    appearing_speed=random.randint(50,
                                                   100)
                )
            return p
        for i in range(number):
            if self.projectile_types:
                if isinstance(self.projectile_types,tuple):
                    for projectile in list(self.projectile_types):
                        choose = construct_projectile \
                            (random.choice(self.projectile_types))
                        self.projectiles.add(choose)
                        self.projectiles_seek.add(choose) if projectile is DelayedSeekingProjectile else None
                else:
                    self.projectiles.add(construct_projectile(self.projectile_types))
    def update(self,dt=None,func=None)->bool:
        if dt is None:
            dt = Settings.dt
        screen.blit(self.image, self.rect)
        for i in range(len(self.board_border_surfaces)):
            screen.blit(self.board_border_surfaces[i], self.board_border[i])
        back_lbl = pygame.surface.Surface((self.attack_lbl.image.get_width(), self.attack_lbl.image.get_height() / 2))
        back_lbl.fill('black')
        back_lbl.set_alpha(self.attack_lbl.alpha)
        back_rect = back_lbl.get_frect(center=(self.rect.centerx, self.rect.centery - 295))
        screen.blit(back_lbl, back_rect)
        self.attack_lbl.dynamic_render(False,True,True)
        self.time_elapsed += dt
        self.time+= dt
        if self.time>=self.total_time*5/self.number_of_projectiles:
           self.time=0
           self.create_projectiles(5)
        self.set_projectiles_target(pygame.mouse.get_pos())
        for projectile in self.projectiles:
            if projectile in self.projectiles_seek:
                try:
                    projectile.update(dt, self.rect, self.board_border[0], self.board_border[1], self.board_border[2],
                                      self.board_border[3])
                except:
                    projectile.update(dt)
            else:
                projectile.update(dt)
            if isinstance(projectile,StaticProjectile):
                if projectile.disappear(dt,True): # spawn new projectile
                    q = StaticProjectile(projectile.pos, projectile.color,projectile.Group, projectile.size, projectile.lifetime, projectile.appearing_speed)
                    self.projectiles.add(q)
        if func is not None:
            func()
        if self.time_elapsed>= self.total_time or (not self.cursor.rect.colliderect(self.rect) and self.time_elapsed>10):
            return True
        return False

Enemy_Movesets = \
{
'Default': lambda: EnemyAttackBoard('Default'),
'Special': lambda: EnemyAttackBoard('Special',None,2,1.5,projectile_types=DelayedSeekingProjectile)

}
class Enemy(AnimatedObject):
    def __init__(self,image_folder_name,image_name,hp,max_hp,damage,value=10,moveset=(('Default','D'),('Special','S')),anim_frames=2,x=WINDOW_WIDTH/1.5,y=WINDOW_HEIGHT/1.9,no_background=False):
        super().__init__(image_folder_name,image_name,x,y)
        self.hp = hp
        self.damage = damage
        self.value = value
        self.is_animating = False
        self.frame = 1
        self.anim_frames = anim_frames
        self.anim_name = ''
        self.moveset = moveset
        self.max_hp = max_hp
        self.no_background=no_background
        self.capital_name = self.image_name
        self.alt_moveset_names = None
        for letter in self.capital_name:
            letter.capitalize()
        self.image_l = len(self.capital_name)*30
        self.description = Label(self.capital_name,'white',int(self.rect.centerx),int(self.rect.centery),FONT_PATH,
                                 30,(self.image_l,40),(int(self.rect.centerx-self.image_l/4),int(self.rect.centery)),True,'black')
        print("enemy_init")

    def adjust_attack(self,attack):
        for move in self.moveset:
            if isinstance(move, tuple):
                if attack.name == move[0]:
                    attack.name = move[1]
                    attack.attack_lbl.resize(move[1])
                    attack.attack_lbl.text = move[1] + attack.lbl_pause
                    attack.damage_multiplier= move[2] if len(move)>=3 else attack.damage_multiplier
                    attack.difficulty= move[3] if len(move)>=4 else attack.difficulty
                    return

    def choose_an_attack(self):
        candidate_attacks = [attack for attack in self.moveset]
        try:
            return Enemy_Movesets[candidate_attacks[random.randint(0,len(candidate_attacks)-1)][0]]() # for custom attack names
        except:
            return Enemy_Movesets[candidate_attacks[random.randint(0, len(candidate_attacks) - 1)]]() #for default names
    def update(self,only_description=False)->bool:
        action = False
        if not only_description:
            if not self.hp <=0:
                screen.blit(self.image,self.rect)
            else:
                self.is_animating = False
        else:
            if self.rect.collidepoint(mouse.get_pos()):
                self.description.update()
        return action
    def attack(self,attack_multiplier):
        damage = int((self.damage -Player0.Data['Defense'])*attack_multiplier)
        Player0.Data['HP'] -= damage if damage>0 else 0
    def death(self,boss=False)->bool:
        next_scene=False
        Main_Timer.activate()

        if not boss:
            SupportVariables.battle_started = False
            SupportVariables.hitbox_created = False
            SupportVariables.corridor_created = False
            if Player0.Data['HP'] + self.value <= Player0.Data['Max_HP']:
                Player0.Data['HP'] += self.value
            else:
                Player0.Data['HP'] = Player0.Data['Max_HP']
        else:
           SupportVariables.corridor_created = False
        if timeout:
            next_scene=True
            Player0.Data['Current_Room'] += 1
        return next_scene
""" moveset consists of: name of template constructor, custom name,damage_multiplier, difficulty """
Enemies = {
    'Rat': lambda: Enemy('Enemies','Rat',50,50,15,0,(('Default','Scratch'),('Special','Bite'))),
    'FatRat': lambda: Enemy('Enemies','FatRat',100,100,5,10,(('Default','Scratch'),('Special','Bite'))),
    'DecayingRat': lambda: Enemy('Enemies','DecayingRat',40,40,45,20),
    'Boss': lambda: Enemy('Enemies','RatKing',250,250,30,0,(('Default','Shank'),('Special','Gutting',1,3)),
                          2,WINDOW_WIDTH/1.5,WINDOW_HEIGHT/2.2,True),
    'Bile':lambda:Enemy('Enemies','Bile',700,700,60,100,(('Default','Vomit',1,4),('Special','Harm',1.5,3)),8,
                        WINDOW_WIDTH/2,WINDOW_HEIGHT/2.2,True)
}
