
from Game_Data import AnimatedObject,PhysicsObject,SupportVariables,Player0,Main_Timer,cursor,random,timeout
from Settings import *

class Enemy(AnimatedObject):
    def __init__(self,image_folder_name,image_name,hp,max_hp,damage,value=10,x=WINDOW_WIDTH/1.5,y=WINDOW_HEIGHT/1.9):
        super().__init__(image_folder_name,image_name,x,y)
        self.hp = hp
        self.damage = damage
        self.value = value
        self.is_animating = False
        self.frame = 1
        self.anim_name = ''
        self.max_hp = max_hp
        print("enemy_init")
    def update(self):
        action = False
        if not self.hp <=0:
            screen.blit(self.image,self.rect)
        else:
            self.is_animating = False
        return action
    def attack(self):
        Player0.Data['HP'] -= self.damage
    def death(self,boss=False)->bool:
        next_scene=False
        Main_Timer.activate()

        if not boss:
            SupportVariables.battle_started = False
            SupportVariables.hitbox_created = False
            SupportVariables.corridor_created = False
            Player0.Data['HP']+=self.value
        else:
           SupportVariables.corridor_created = False
        if timeout:
            next_scene=True
            Player0.Data['Current_Room'] += 1
        return next_scene
Enemies = {
    0: lambda: Enemy('../Enemies','Rat',50,50,15,0),
    10: lambda: Enemy('../Enemies','FatRat',100,100,5),
    20: lambda: Enemy('../Enemies','DecayingRat',40,40,45,20),
    'Boss': lambda: Enemy('../Enemies','RatKing',250,250,30,0,WINDOW_WIDTH/1.5,WINDOW_HEIGHT/2.2)
}

class EnemyProjectile(PhysicsObject):
    def __init__(self,group=None,target_pos=(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]),pos=(0,0),velocity=0,max_velocity=150,acceleration=0.05,color='white',size=(10,10)):
        super().__init__(pos,velocity,max_velocity,acceleration,target_pos,color,group,size)
        self.x=pos[0]
        self.color=color
        self.y=pos[1]
    def collide(self,player_pos:tuple)->bool:
        if self.x == player_pos[0] and self.y == player_pos[1]:
            return True
        return False
class EnemyAttack(pygame.sprite.Sprite):
    def __init__(self,p_cursor=cursor,damage_multiplier=1,cost=1,effect="",total_time=500,number_of_projectiles=30,projectile_speed=500,projectile_size=(10,10)):
        super().__init__()
        self.damage_multiplier = damage_multiplier
        self.cost = cost
        self.cursor = p_cursor
        self.effect = effect
        self.total_time = total_time
        self.time = 0
        self.time_elapsed = 0
        self.board_border_surfaces = []
        self.board_border=[]
        self.number_of_projectiles = number_of_projectiles
        self.projectile_speed = projectile_speed
        self.projectile_size = projectile_size
        self.image = pygame.Surface((500,500))
        self.rect = self.image.get_frect(center=(300,500))
        self.projectiles = pygame.sprite.Group()
        self.create_projectiles(int(self.number_of_projectiles/10))
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
    def spawn_pos_rng(self):
        pos = random.randint(-300, 300)
        if -100 < pos < 100:
            return self.spawn_pos_rng()
        return pos
    def set_projectiles_target(self, target_pos,dt=clock.tick(60)/1000):
        reach_eps = 2.0
        for p in self.projectiles:
            dx = (p.target_pos[0] - p.rect.x)
            dy = (p.target_pos[1] - p.rect.y)
            if (dx * dx + dy * dy) ** 0.5 <= reach_eps:
                p.update_target_pos(target_pos)
                p.velocity = 0
    def create_projectiles(self,number):
        for i in range(number):
            spawn_pos = (
                pygame.mouse.get_pos()[0] + self.spawn_pos_rng(),
                pygame.mouse.get_pos()[1] + self.spawn_pos_rng()
            )
            rand_size= (random.randint(int((self.projectile_size[0]/2)*self.damage_multiplier),int(self.projectile_size[0]*self.damage_multiplier)))
            p = EnemyProjectile(
                group=None,
                target_pos=(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]),
                pos=spawn_pos,
                velocity=0,
                max_velocity=random.randint(int(self.projectile_speed/2), self.projectile_speed),
                acceleration=random.randint(int(self.projectile_speed/4), int(self.projectile_speed/2)),
                color='white',
                size=(rand_size, rand_size) if rand_size>10 else (10,10)
            )
            self.projectiles.add(p)
    def update(self,dt=clock.tick(60)/1000,func=None)->bool:
        screen.blit(self.image, self.rect)
        for i in range(len(self.board_border_surfaces)):
            screen.blit(self.board_border_surfaces[i], self.board_border[i])
        self.time_elapsed +=1
        self.time+=1
        if self.time==int(self.total_time/self.number_of_projectiles):
           self.time=0
           self.create_projectiles(1)
        self.set_projectiles_target(pygame.mouse.get_pos(),dt)
        self.projectiles.update(dt,self.rect,self.board_border[0],self.board_border[1],self.board_border[2],self.board_border[3])

        if func is not None:
            func()
        if self.time_elapsed>= self.total_time or (not self.cursor.rect.colliderect(self.rect) and self.time_elapsed>10):
            return True
        return False
Attack_board= EnemyAttack()