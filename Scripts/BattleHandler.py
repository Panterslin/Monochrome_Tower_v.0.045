
from Enemies import *
from Labels import *
from Game_Data import *
from Weapons import Current_Weapon
from Groups import *
import Settings

class Battle:
    def __init__(self,display,scene_manager, player, enemy, game, game_id):
        self.game_id = game_id
        self.display = display
        self.game = game
        self.scene_manager = scene_manager
        self.player = player
        self.enemy = enemy
        self.enemy_killed=False
        self.battle_state="Pre_round"
        self.turn_check=0
        self.attack_board = EnemyAttackBoard()
        self.cursor = Cursor()
        self.dmg_lbl=AppearingLabel(0.05,str(Current_Weapon.damage),'white',WINDOW_WIDTH/2-100,WINDOW_HEIGHT/2-100,
                               50,FONT_PATH)
        self.item_used=False
        self.Item_button = Button(WINDOW_WIDTH/2-300, WINDOW_HEIGHT/2.5+10, 'ITEM',290,90,True,65,
                                  True,(WINDOW_WIDTH/2-230, WINDOW_HEIGHT/2-90))
        self.attack_button = Button(WINDOW_WIDTH/2-300, WINDOW_HEIGHT/3-40, 'ATTACK',290,90,True,65,
                                    True,(WINDOW_WIDTH/2-295, WINDOW_HEIGHT/3-50))
    def adjust_enemy_attack(self):
        #self.attack_board.damage_multiplier *= self.enemy.damage / 10
        self.attack_board.cursor = self.cursor
        self.enemy.adjust_attack(self.attack_board)
        self.attack_board.create_projectiles(int(self.attack_board.number_of_projectiles / 10))
    def run(self):
        if Current_Weapon.clicked and not pygame.mouse.get_pressed()[0]:
            Current_Weapon.clicked = False
        if self.player.Data['HP']<=0:
            self.scene_manager.create_scene('Death')
            self.battle_state="Pre_round"
            SupportVariables.clicked=False
        """Sprites setup"""
        if self.enemy.no_background is False:
            Vermin_I_Deco.animate()
            Vermin_I_Deco.animation_play(14,2,'','topleft',Settings.dt)
        room_score.dynamic_update(self.player.Data['Current_Room'])
        floor_score.dynamic_update(self.player.Data['Current_Floor'])
        self.enemy.update()
        self.enemy.animate() if not self.enemy.is_animating and not self.enemy.hp<=0 else None
        self.enemy.animation_play(self.enemy.anim_frames, 0.5, '', 'center', Settings.dt)
        Base_UI.update()
        self.player.Data['Max_HP']=hp_bar.create_bar(self.player.Data['HP'], self.player.Data['Max_HP'])
        self.player.Data['Max_Sanity']=sanity_bar.create_bar(self.player.Data['Sanity'], self.player.Data['Max_Sanity'])
        """Battle States"""
        if self.battle_state == "Pre_round":
            pygame.mouse.set_visible(True)
            if self.attack_button.update():
                self.turn_check=0
                print(SupportVariables.door)
                self.battle_state = 'Battle_init'
            if self.Item_button.update() and not self.item_used:
                self.scene_manager.previous_scene='Battle'
                self.scene_manager.set_scene('Inventory')
                self.item_used=True
        elif self.battle_state == 'Battle_init':
            Current_Weapon.init_player_attack()
            Current_Weapon.player_attack(self.enemy,False, Settings.dt)
            self.battle_state = 'Battle_start'
        elif self.battle_state == 'Defense':
            if self.attack_board.update(Settings.dt): #successful defense
                self.battle_state = 'Pre_round'
                self.item_used = False
                pygame.mouse.set_visible(True)
            self.cursor.update(Cursor.show, self.attack_board.rect)
            collision = any(p.collide(self.cursor.rect) for p in self.attack_board.projectiles)
            if collision or any(self.cursor.rect.colliderect(b) for b in self.attack_board.board_border) or not self.attack_board.rect.collidepoint(pygame.mouse.get_pos()):
                 #failed defense
                self.enemy.attack(self.attack_board.damage_multiplier)
                pygame.mouse.set_visible(True)
                self.battle_state = 'Pre_round'
                self.item_used = False
        elif self.battle_state == 'attack':
            self.dmg_lbl.dynamic_render(False, False, True)
            if Current_Weapon.deal_damage > 0:
                if Current_Weapon.animation_play(4, 2, 'Attack_', '', Settings.dt):
                    Current_Weapon.inflict_damage(self.enemy)
                    Current_Weapon.frame=1
                    if self.enemy.hp <= 0:
                        self.enemy_killed = True
                        self.enemy.death()
                        self.battle_state = 'Battle_end'
                    elif Current_Weapon.turn >= Current_Weapon.attack_speed:
                        self.attack_board = self.enemy.choose_an_attack()
                        self.adjust_enemy_attack()
                        self.battle_state = 'Defense'
                        Current_Weapon.turn = 0
                        Current_Weapon.swings = 0
                    else:
                        self.battle_state = 'Battle_start'
            else:
                # No damage to apply; enemy gets a counter if turn quota reached
                if Current_Weapon.turn >= Current_Weapon.attack_speed+1:
                    self.attack_board = self.enemy.choose_an_attack()
                    self.adjust_enemy_attack()
                    self.battle_state = 'Defense'
                else:
                    self.battle_state = 'Battle_start'
        elif self.battle_state == 'Battle_start':
            if not self.enemy_killed:
                Current_Weapon.player_attack(self.enemy,True, Settings.dt)
                if Current_Weapon.turn!=self.turn_check:
                    self.turn_check+=1
                    self.battle_state = 'attack'
                    self.dmg_lbl.__init__(0.05, str(Current_Weapon.damage), 'white', WINDOW_WIDTH / 2 - 100,
                                          WINDOW_HEIGHT / 2 - 100,
                                          50, FONT_PATH)
                elif Current_Weapon.turn >= Current_Weapon.attack_speed:
                    self.attack_board = self.enemy.choose_an_attack()
                    self.adjust_enemy_attack()
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
        if Main_Timer.update():
            update_data(Player_Data, self.game.Player.Data)
            save_data(self.game_id, self.game.Player.Data)
            if SupportVariables.door != 'Boss':
                self.player.Data['Current_Room'] += 1
                self.scene_manager.create_scene('Corridor')
            else:
                self.scene_manager.create_scene('End')
            self.battle_state = "Pre_round"
            self.item_used=False
            self.enemy_killed = False
            Current_Weapon.frame=1
        self.enemy.update(True)
    def pre_round(self):
        pass