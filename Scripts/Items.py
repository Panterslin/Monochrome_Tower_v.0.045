import operator
from Groups import *
from Game_Data import AnimatedObject,Button,Player0
from Timer import Timer
from Settings import *
class Item(AnimatedObject):
    def __init__(self,image_folder_name='',image_name='',groups=None,target=None,target_keys=None,given_operands=None,values=None,description="",slot_group=Inventory_slots,
    duration=None,duration_unit=None,class_targets=None,stackable=None,*args):
        """ *args added for extra values and/or targets"""
        """target """
        super().__init__(image_folder_name,image_name)
        self.target = target
        self.class_targets = class_targets
        self.target_keys = target_keys
        self.given_operands = given_operands
        self.values = values
        self.groups = groups
        self.slot_group = slot_group
        self.description = description
        self.original_pos = self.rect.center
        self.hover_pos = self.original_pos
        self.pressed = pygame.mouse.get_pressed()[0]
        self.did_drag=False
        self.max_click_delay = Timer(0.3)  # check if two clicks are performed in quick succession
        self.drag_delay = Timer(0.1)
        self.dragging = False
        self.clicked = False
        self.click_counter=0
        self.duration = duration
        self.duration_unit = duration_unit
        self.activate = False
        self.init_duration_val =self.target[self.duration_unit] if self.duration_unit is not None else None
        self.current_duration_val = self.init_duration_val
        self.visible = False
        self.disabled = False
        self.initial_target_stats = {}
        self.image = pygame.transform.scale_by(self.image, 0.25)
        self.rect = self.image.get_frect()
        self.stackable = stackable
        self.find_starting_pos() if not self.stackable else self.stack()
        self.scaled = False # for overworld display
        self.quantity_label = None
        self.stacked_items = []
        self.snapped=False
        self.used=False

        self.set_initial_target_stats()
        for group in groups:
            group.add(self)
        self.operands = {
            "=":operator.eq,
            ">":operator.gt,
            "<":operator.lt,
            "<=":operator.le,
            ">=":operator.ge,
            "!=":operator.ne,
            "*":operator.mul,
            "/":operator.truediv,
            "+":operator.add,
            '++':operator.iadd, # used for reaching amount over max value
            "-":operator.sub,
            'set': lambda a, b: b,
            'clamp-' : lambda a, b: max(b, a),
            'clamp+' : lambda a, b: min(b, a)
        }
        self.inverse_ops = {
            '+': operator.sub,
            '-': operator.add,
            '*': operator.truediv,
            '/': operator.mul,
        }
    def find_objects_in_slot(self,enable_previous=None): #finds all items in the same slot
        stack = [itm for itm in self.groups[0]
        if itm.rect.center == self.rect.center and itm.image_name == self.image_name]
        stack.sort(key=lambda x: id(x))
        self.stacked_items = stack
        if len(stack) <= 1:
            for itm in stack:
                itm.disabled = False
        else:
            for i, itm in enumerate(stack):
                itm.disabled = (i != len(stack) - 1)
            for slot,itm in zip(self.slot_group,stack):
                if slot.rect.center == any(itm.rect.center):
                    slot.occupied = True
                    break
        if enable_previous and len(stack) >= 1:
            top = stack[-1]
            top.disabled = False
        self.quantity_label = pixel_font.render('x'+str(len(self.stacked_items)), True, 'white') \
        if len(stack) > 1 else None
    def stack(self):
        same_kind = [itm for itm in self.groups[0] if itm is not self and itm.image_name == self.image_name]
        if not self.stackable :
            return
        if same_kind:
            base = next((itm for itm in same_kind), same_kind[0])
            self.rect.center = base.rect.center
            stack = [
                itm for itm in self.groups[0]
                if itm.rect.center == self.rect.center and itm.image_name == self.image_name
            ]
            stack.sort(key=lambda x: id(x))
            for i, itm in enumerate(stack):
                itm.disabled = (i != len(stack) - 1)
        else:
            self.disabled=False
            self.find_starting_pos()
    def append_to_player_data(self):
        Player0.Data['Items'].append(self.image_name)
    def display_in_overworld(self,pos=(WINDOW_WIDTH,WINDOW_HEIGHT),size=None):
        self.pressed = pygame.mouse.get_pressed()[0]
        if size is not None and not self.scaled:
            self.image = pygame.transform.scale_by(self.image, size)
            self.rect = self.image.get_frect()
            self.scaled = True
        for slot in self.slot_group:
            if slot.rect.center == self.original_pos:
                slot.occupied = False
                break
        self.rect.center = pos
        screen.blit(self.image, self.rect)
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if self.pressed:
                for group in self.groups:
                    group.add(self)
                #self.find_starting_pos()
                self.image = pygame.transform.scale_by(self.image, 1/size) if size is not None else self.image
                self.rect = self.image.get_frect()
                self.rect.center = self.original_pos
                for slot in self.slot_group:
                    if slot.rect.center == self.original_pos:
                        slot.occupied = True
                        break
                self.scaled = False
                return True
            else:
                self.show_description()

        return False
    def set_initial_target_stats(self): # reads player stats to which the effects are applied
        if self.values is not None and self.given_operands is not None:
            """Converts given_operands and values to dicts with keys equal to target_keys"""
            if not self.target_keys:
                return
            ops_by_key = {}
            if self.given_operands is None:
                ops_by_key = {}
            elif isinstance(self.given_operands, (list, tuple)):
                for i, k in enumerate(self.target_keys):
                    ops_by_key[k] = self.given_operands[i if i < len(self.given_operands) else -1] # converts values of lists, tuples to dicts
            elif isinstance(self.given_operands, str):
                ops_by_key = {k: self.given_operands for k in self.target_keys} # applies operand to each target_key
            else:
                ops_by_key = {}
            # with values
            vals_by_key = {}
            if self.values is None:
                vals_by_key = {}
            elif isinstance(self.values, (list, tuple)):
                for i, k in enumerate(self.target_keys):
                    vals_by_key[k] = self.values[i if i < len(self.values) else -1]
            else:
                vals_by_key = {k: self.values for k in self.target_keys}

            """converting to dicts"""
            if ops_by_key:
                self.given_operands = ops_by_key
            if vals_by_key:
                self.values = vals_by_key

            for key in self.target_keys:
                 if key is not None and isinstance(self.target, dict):
                    self.initial_target_stats[key] = self.target[key] # first stat to which the effect is applied
    def apply_effects(self,usable_out_of_battle=True): #applies the effects of the item to the target
        if not usable_out_of_battle:
            return
        #effects on dicts (eg. Player0)
        if isinstance(self.target, dict) and self.initial_target_stats:
            if isinstance(self.given_operands, dict):
                for key in self.initial_target_stats:
                    op = self.operands[self.given_operands.get(key)]
                    if not 'Max_' + key in self.target.keys():
                        self.target[key] = op(self.target.get(key, 0), self.values[key])
                    else:
                        if op == operator.add or op == operator.mul:
                            if op(self.target.get(key),self.values[key]) >= self.target['Max_' + key]:
                                self.target[key] = self.target['Max_' + key]
                            else:
                                self.target[key] = op(self.target.get(key, 0), self.values[key])
                        else:
                            self.target[key] = op(self.target.get(key, 0), self.values[key])
                return

            # Handle function effects
        if callable(self.target):
            for key in self.initial_target_stats:
                self.target(self.values[key])
            return
        #Plain operand effects
        for key in self.target_keys:
            for operand in self.given_operands:
                op = self.operands[operand]
                self.target[key] = op(self.target, self.values)
    def lasting_effect(self):
        self.current_duration_val = self.target[self.duration_unit] if self.duration_unit is not None else None
        if self.duration_unit is not None and self.duration is not None and self.activate:
            self.image.set_alpha(0)
            needs_dyn = False
            if isinstance(self.given_operands, str):
                needs_dyn = self.given_operands in ('clamp-', 'clamp+')
            elif isinstance(self.given_operands, dict):
                needs_dyn = any(v in ('clamp-', 'clamp+') for v in self.given_operands.values())
            if needs_dyn:
                self.read_dynamic_values()
            self.rect.x = WINDOW_WIDTH *2
            self.apply_effects() if self.current_duration_val - self.init_duration_val < self.duration else self.kill()

    def save_current_stats(self):
        if isinstance(self.target, dict) and self.initial_target_stats:
            for value in self.initial_target_stats: # saves values before applying effects
                self.initial_target_stats[value] = self.target[value]
    def revert_effects(self,usable_out_of_battle=True):
        if isinstance(self.target, dict) and self.initial_target_stats:
            if isinstance(self.given_operands, dict):
                for key,operand in self.given_operands.items():
                    if operand in ("clamp-", "clamp+"):
                        continue
                    inv_op = self.inverse_ops[operand] if operand in self.inverse_ops else None
                    if inv_op is not None and key in self.values:
                        self.target[key] = inv_op(self.target.get(key, 0), self.values[key]) #perform inverse operation
                    else: # for non invertible
                        if key in self.initial_target_stats:
                            self.target[key] = self.initial_target_stats[key]
            else:
                for key in self.initial_target_stats:
                    self.target[key] = self.initial_target_stats[key]

    def free_current_slot(self):
        for slot in self.slot_group:
            if getattr(slot, 'occupied', False) and slot.rect.center == self.rect.center:
                slot.occupied = False
                break
    def find_starting_pos(self):
        for slot in self.slot_group:
            if not getattr(slot, 'occupied'):
                self.rect.center = slot.rect.center
                slot.occupied = True
                self.original_pos = self.rect.center
                break
    def read_dynamic_values(self): # if value changes depending on the state of game
        if not self.target_keys or not self.class_targets:
            return
        for target, key in zip(self.class_targets, self.target_keys):
            if hasattr(target, 'get_value') and callable(getattr(target, 'get_value')): # if target is a class
                curr = target.get_value(key) # e.g calls get_value function from Player0 and assigns it to the items value
            elif isinstance(target, dict):
                curr = target.get(key)
            elif hasattr(target, 'Data') and isinstance(target.Data, dict):
                curr = target.Data.get(key) # if target is a class assigns st
            else:
                curr = getattr(target, key, None)
            if curr is None:
                continue
            op_for_key = None
            if isinstance(self.given_operands, dict):
                op_for_key = self.given_operands.get(key)
            elif isinstance(self.given_operands, str):
                op_for_key = self.given_operands
            prev = None
            if isinstance(self.values, dict):
                prev = self.values.get(key)

            # Monotonic update based on clamp type
            if op_for_key == 'clamp-':
                new_val = curr if prev is None else max(prev, curr)
            elif op_for_key == 'clamp+':
                new_val = curr if prev is None else min(prev, curr)
            else:
                new_val = curr

            if isinstance(self.values, dict):
                self.values[key] = new_val
            elif isinstance(self.values, list):
                try:
                    idx = self.target_keys.index(key)
                    if 0 <= idx < len(self.values):
                        self.values[idx] = new_val
                except ValueError:
                    pass

    def update(self,func=None):
        self.pressed = pygame.mouse.get_pressed()[0]
        self.mouse_pos = pygame.mouse.get_pos()
        screen.blit(self.image,self.rect)
        self.find_objects_in_slot()
        if self.quantity_label and self.stacked_items: # blit quantity label on top of stacked items
            is_top = (self is self.stacked_items[-1])
            if is_top:
                slot = next((s for s in self.slot_group if s.rect.center == self.rect.center), None)
                if slot:
                    pos = (slot.rect.right - self.quantity_label.get_width() - 4,
                           slot.rect.bottom - self.quantity_label.get_height() - 2)
                    screen.blit(self.quantity_label, pos)
        if func is not None and callable(func):
           if func(self):
               return True
        self.drag()

        if not self.dragging and not self.visible and self.rect.collidepoint(self.mouse_pos):
            self.show_description()
        if self.max_click_delay.update():
           self.click_counter=0
        if self.click_counter >= 2:
            self.use_inv()
            self.max_click_delay.deactivate()
            self.click_counter=0
        self.lasting_effect()
        return False
    def unconditional_update(self):
        self.lasting_effect()
    def show_description(self,font='../Fonts/PixelFont.ttf',size=15):
        if self.disabled:
            return
        font = pygame.font.Font(font, size)
        text = font.render(self.description, True, 'black')
        bg = pygame.Surface((text.get_width() + 40, text.get_height() + 40), flags=pygame.SRCALPHA)
        bg.fill('white')
        x = self.rect.x +100
        y = self.rect.y +20
        screen.blit(bg, (x, y))
        screen.blit(text, (x + 20, y + 20))
    def use_inv(self,*args): #function for double click for inheriting classes
        pass
    def check_if_in_slot(self):
        pass
    def stack_drag(self):
        alt_pressed = pygame.mouse.get_pressed()[2]
        if alt_pressed and self.stacked_items:
            self.drag_action(alt_pressed)
            for item in self.stacked_items:
                item.rect.center = self.rect.center
        else:
            self.drag_action()
            if self.snapped:
                for item in self.stacked_items:
                    item.snap_to_invslot()
                    if item.rect.center != self.rect.center:
                        item.rect.center = self.rect.center

    def drag_action(self,alt_pressed=None):
        self.snapped=False
        self.pressed = pygame.mouse.get_pressed()[0]
        if alt_pressed is not None:
            self.pressed = alt_pressed
        mouse_over = self.rect.collidepoint(pygame.mouse.get_pos())
        for slot in self.slot_group:
            if slot.rect.center == self.rect.center:
                mouse_over  = slot.rect.collidepoint(pygame.mouse.get_pos())
                break
        if self.pressed and mouse_over and not self.clicked:
            self.clicked = True
            self.dragging = False
            self.did_drag = False
            self.drag_delay.deactivate()
            self.drag_delay.activate()
        elif not self.pressed and self.clicked:
            self.clicked = False
            if self.did_drag:
                self.original_pos = self.snap_to_invslot()
                self.snapped = True
            else:
                self.click_counter += 1 if not self.disabled else 0
                self.max_click_delay.activate()
            self.drag_delay.deactivate()
            self.did_drag = False

        elif self.pressed and self.clicked:
            if not self.dragging:
                if self.drag_delay.update():
                    self.dragging = True
            else: #actually dragging
                self.did_drag = True
                self.rect.center = pygame.mouse.get_pos()
                self.original_pos = self.snap_to_invslot(True)
                self.check_if_in_slot()
    def drag(self,disabled=None):
        if any(getattr(item, 'dragging', False) for item in self.groups[0] if item is not self or not item in self.stacked_items):
            return
        if disabled is None or not disabled:
            self.drag_action() if not self.stackable else self.stack_drag()
    def acquire_target(self,target): # for picking new enemy targets
        self.target = target
    def snap_to_invslot(self,just_check=False):
        hovered_slot = None
        for slot in self.slot_group:
            if slot.rect.collidepoint(self.mouse_pos):
                for prev in self.slot_group:
                    if prev.rect.center == self.original_pos:
                        prev.occupied = False
                        break
                hovered_slot = slot
                break
        if hovered_slot and not getattr(hovered_slot, 'occupied', False):
            if not just_check:
                for prev in self.slot_group:
                    if getattr(prev, 'occupied', False) and prev.rect.center == self.original_pos:
                        prev.occupied = False
                        break
                self.rect.center = hovered_slot.rect.center
                hovered_slot.occupied = True
                self.dragging = False
                return self.rect.center
            return hovered_slot.rect.center
        elif hovered_slot and getattr(hovered_slot, 'occupied', False) and any(hovered_slot.rect.center == itm.rect.center \
        for itm in self.groups[0] if itm is not self and itm.image_name == self.image_name):
            if not just_check:
                self.rect.center = hovered_slot.rect.center
                self.stack()
                self.dragging = False
            return hovered_slot.rect.center
        if not just_check:
            self.rect.center = self.original_pos
            for slot in self.slot_group:
                if slot.rect.center == self.original_pos:
                    slot.occupied = True
                    break
            self.dragging = False
        return self.original_pos
class OnetimeUseItem(Item):
    def __init__(self,image_folder_name,image_name,groups,target,given_operands,values,description,slot_group,target_keys,duration=None,duration_unit=None,class_targets=None,*args):
        super().__init__(image_folder_name,image_name,groups,target,target_keys,given_operands,values,description=description,slot_group=slot_group,
        duration=duration,duration_unit=duration_unit,class_targets=class_targets,stackable=True)

    def use_inv(self,func=None,*args):
        self.used=True
        if self.disabled:
            return None
        Player0.Data['Items'].remove(self.image_name) if self.image_name in Player0.Data['Items'] else None
        print(self.description + " used!")
        self.disabled = True
        result = None
        if func is not None:
            result = func(*args)
        if not result:
            self.activate = True
            self.init_duration_val = self.target[self.duration_unit] if self.duration_unit is not None else None
            self.read_dynamic_values()
            #self.lasting_effect()
            for item in self.groups[0]:  # for lasting effect items
                if isinstance(item.given_operands, dict) and any(
                        v in ('clamp-', 'clamp+') for v in item.given_operands.values()):
                    item.read_dynamic_values()
        self.apply_effects()
        self.find_objects_in_slot(True)
        self.free_current_slot() if len(self.stacked_items) <=1 else None
        self.kill() if self.duration is None else None
        return True

class Artifact(Item):
    def __init__(self, image_folder_name, image_name, groups, target, given_operands, values,description,slot_group,*args):
        super().__init__(image_folder_name, image_name, groups, target, given_operands, values,description=description,slot_group=slot_group)
class CraftingMaterial(Item):
    def __init__(self, image_folder_name, image_name, groups, target, given_operands, values,description,slot_group,*args):
        super().__init__(image_folder_name, image_name, groups, target, given_operands, values,description=description,slot_group=slot_group)
class Equipment(Item):
    def __init__(self, image_folder_name, image_name, groups, target, given_operands, values,description,slot_group,target_keys,eq_type:str, *args):
        super().__init__(image_folder_name, image_name, groups, target,target_keys, given_operands, values,description=description,slot_group=slot_group)
        self.eq_type = eq_type
        self.eq_slot = Equipment_slots
        self.equipped =False
    def check_if_in_slot(self):
        if not self.equipped:
            return
        in_eq = any(self.rect.center == s.rect.center for s in self.eq_slot)
        if not in_eq:
            for s in self.eq_slot:
                if s.rect.center == self.original_pos:
                    s.occupied = False
                    s.image.set_alpha(255)
                    break
            self.equipped = False
            self.revert_effects()
    def use_inv(self):
        swapped = False
        self.used= True
        for slot in self.eq_slot:
            if getattr(slot, 'image_name', None) == self.eq_type:
                if not self.equipped and not getattr(slot, 'occupied', False):
                   slot.image.set_alpha(0)
                   self.free_current_slot()
                   self.rect.center = slot.rect.center
                   self.original_pos = self.rect.center
                   self.equipped = True
                   slot.occupied = True
                   break
                elif self.equipped:
                    if self.rect.center != slot.rect.center:
                        self.revert_effects()
                        self.rect.center = slot.rect.center
                        self.original_pos = self.rect.center
                        self.free_current_slot()
                        self.equipped = True
                        slot.occupied = True
                        slot.image.set_alpha(0)
                        break
                    else:
                        free_inv = next((s for s in self.slot_group if not getattr(s, 'occupied', False)), None)
                        if free_inv is None:
                            break
                        self.equipped = False
                        slot.occupied = False
                        slot.image.set_alpha(255)
                        self.rect.center= free_inv.rect.center
                        free_inv.occupied = True
                        self.original_pos = self.rect.center
                elif getattr(slot, 'occupied', False): # swap two eq items
                    for item in self.groups[1]:
                        if item is not self and item.rect.center == slot.rect.center:
                            prev_center = self.rect.center
                            self.free_current_slot()
                            item.free_current_slot()
                            item.rect.center = prev_center
                            self.rect.center = slot.rect.center
                            slot.occupied = True
                            slot.image.set_alpha(0)
                            self.equipped = True
                            self.original_pos = self.rect.center
                            item.equipped = False
                            for inv_slot in self.slot_group:
                                if inv_slot.rect.center == prev_center:
                                    inv_slot.occupied = True
                                    break
                            item.revert_effects()
                            self.apply_effects()
                            swapped= True
                            return
            else:
                continue
            for item in self.groups[0]: # for lasting effect items
                item.read_dynamic_values() if item.given_operands in ('clamp-','clamp+') else None

        if self.equipped and any(self.rect.center == s.rect.center for s in self.eq_slot):
            self.apply_effects() if not swapped else None
        else:
            self.revert_effects()
            self.equipped = False
            for slot in self.eq_slot:
                if slot.rect.center == self.rect.center:
                    slot.occupied = False
                    slot.image.set_alpha(255)
                    break

class Note(Item):
    def __init__(self,image_folder_name, image_name,groups,description,slot_group):
        super().__init__(image_folder_name, image_name,groups,description=description,slot_group=slot_group)
        self.visible = False # note popup
        self.rect = self.image.get_frect()
        self.button = Button(10,10,'X',40,40,True,30)
        self.clicked=False
        self.click_counter=0
        self.disabled = False
    def use_inv(self):
        self.visible = True if self.click_counter >= 2 else False
        self.disabled = True if self.click_counter >= 2 else False
        self.image.set_alpha(0)
    def show(self,font='../Fonts/PixelFont.ttf',size=20):
        if self.visible:
            self.image.set_alpha(0)
            font = pygame.font.Font(font, size)
            text = font.render(self.description, True, 'white')
            bg = pygame.Surface((text.get_width() + 40, text.get_height() + 40), flags=pygame.SRCALPHA)
            bg.fill((255,255,255, 20))
            x = WINDOW_WIDTH // 2 - bg.get_width() // 2
            y = WINDOW_HEIGHT // 2 - bg.get_height() // 2
            screen.blit(bg, (x, y))
            screen.blit(text, (x + 20, y + 20))
            if self.button.update():
                self.visible = False
                self.click_counter = 0
                self.disabled = False
        else:
            self.image.set_alpha(255)
        return self.visible

Notes = {'Test_Note':lambda:Note('../Notes','Test_Note',[Items_group,Notes_group],"Test note",Inventory_slots)}
OneTimeUseItems = {
    'Bottle':lambda:OnetimeUseItem('../Items','Bottle',
[Items_group,OneTimeUseItems_group],Player0.Data,'+',20,'Item:a bottle of sanity\n'
    'Old habits die hard\n+20 Sanity',Inventory_slots,target_keys=['Sanity']),
    'Powdered Happiness':lambda:OnetimeUseItem('../Items','Powdered Happiness',[Items_group,OneTimeUseItems_group],
    Player0.Data,'clamp-',0,'Item:powdered happiness\n prevents the loss of sanity\n duration:3 rooms',Inventory_slots,target_keys=['Sanity'],
    duration=3,duration_unit='Current_Room',class_targets=[Player0]),

}
Equipment_Items = {
'Sack':lambda:Equipment('../Equipment','Sack',
[Items_group,Equipment_group],Player0.Data,['-','+'],[20,40],"Armor:Sack \n "
    "live and die a slave\n +40 MaxHp -20 MaxSanity",Inventory_slots,['Max_Sanity','Max_HP'],'Helmet'),
'Helmet':lambda:Equipment('../Equipment','Helmet',
[Items_group,Equipment_group],Player0.Data,'+',20,"Armor: Helmet \n Tad bit rusty, but reliable \n"
"+20Max_HP",Inventory_slots,['Max_HP'],'Helmet'),
'Crusade':lambda:Equipment('../Equipment','Crusade',
[Items_group,Equipment_group],Player0.Data,'+',20,"Armor: Crusade \n"
"Inscription reads:\n Deus Vult \n+20 Defense",Inventory_slots,['Defense'],'ChestPlate')

                   }

