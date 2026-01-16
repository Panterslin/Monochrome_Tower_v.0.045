import operator
from Groups import *
from Game_Data import AnimatedObject,Button,Player0
from Timer import Timer
from Settings import *
class Item(AnimatedObject):
    def __init__(self,image_folder_name='',image_name='',groups=None,target=None,target_key=None,operand=None,value=None,description="",slot_group=Inventory_slots):
        """target """
        super().__init__(image_folder_name,image_name)
        self.target = target
        self.target_key = target_key
        self.operand = operand
        self.value = value
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
        self.visible = False
        self.disabled = False
        self.image = pygame.transform.scale_by(self.image, 0.25)
        self.rect = self.image.get_frect()
        self.find_starting_pos()
        if groups is not None:
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
            "-":operator.sub
        }
    def apply_effects(self,usable_out_of_battle=True):
        if usable_out_of_battle:
            op = self.operands[self.operand]
            if isinstance(self.target, dict) and self.target_key is not None:
                self.target[self.target_key] = op(self.target.get(self.target_key, 0), self.value)
            elif callable(self.target):
                self.target(self.value)
            else:
                _ = op(self.target, self.value)
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
    def update(self,func=None):
        self.pressed = pygame.mouse.get_pressed()[0]
        self.mouse_pos = pygame.mouse.get_pos()
        screen.blit(self.image,self.rect)
        if func is not None and callable(func):
           if func(self):
               return True
        self.drag()
        if not self.dragging and not self.visible and self.rect.collidepoint(self.mouse_pos) :
            self.show_description()
        if self.max_click_delay.update():
           self.click_counter=0
        if self.click_counter >= 2:
            self.use_inv()
            self.max_click_delay.deactivate()
            self.click_counter=0
        return False

    def show_description(self,font='../Fonts/PixelFont.ttf',size=20):
        font = pygame.font.Font(font, size)
        text = font.render(self.description, True, 'black')
        bg = pygame.Surface((text.get_width() + 40, text.get_height() + 40), flags=pygame.SRCALPHA)
        bg.fill((255, 255, 255, 60))
        x = self.rect.x +100
        y = self.rect.y +20
        screen.blit(bg, (x, y))
        screen.blit(text, (x + 20, y + 20))
    def use_inv(self,*args): #function for double click for inheriting classes
        pass
    def drag_action(self):
        self.pressed = pygame.mouse.get_pressed()[0]
        mouse_over = self.rect.collidepoint(pygame.mouse.get_pos())
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
            else:
                self.click_counter += 1
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
    def drag(self,disabled=None):
        if any(getattr(item, 'dragging', False) for item in self.groups[0] if item is not self):
            return
        if disabled is None or not disabled:
            self.drag_action()
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

        if not just_check:
            self.rect.center = self.original_pos
            for slot in self.slot_group:
                if slot.rect.center == self.original_pos:
                    slot.occupied = True
                    break
            self.dragging = False
        return self.original_pos
class OnetimeUseItem(Item):
    def __init__(self,image_folder_name,image_name,groups,target,operand,value,description,slot_group,target_key,*args):
        super().__init__(image_folder_name,image_name,groups,target,target_key,operand,value,description=description,slot_group=slot_group)
    def use_inv(self,func=None,*args):
        print(self.description + " used!")
        if func is not None:
            return func(*args)
        self.apply_effects()
        self.free_current_slot()
        self.kill()
        return True
class Artifact(Item):
    def __init__(self, image_folder_name, image_name, groups, target, operand, value,description,slot_group,*args):
        super().__init__(image_folder_name, image_name, groups, target, operand, value,description=description,slot_group=slot_group)
class CraftingMaterial(Item):
    def __init__(self, image_folder_name, image_name, groups, target, operand, value,description,slot_group,*args):
        super().__init__(image_folder_name, image_name, groups, target, operand, value,description=description,slot_group=slot_group)
class Equipment(Item):
    def __init__(self, image_folder_name, image_name, groups, target, operand, value,description,slot_group,eq_type:str, *args):
        super().__init__(image_folder_name, image_name, groups, target, operand, value,description=description,slot_group=slot_group)
        self.eq_type = eq_type
        self.eq_slot = Equipment_slots
        self.equipped =False
    def use_inv(self):
        for slot in self.eq_slot:
            if getattr(slot, 'image_name', None)== self.eq_type and not self.equipped:
               self.rect.center = slot.rect.center
               self.free_current_slot()
               self.equipped = True
               slot.occupied = True
               break
            elif self.equipped:
                if self.rect.center != slot.rect.center:
                    self.rect.center = slot.rect.center
                    self.free_current_slot()
                    self.equipped = True
                    slot.occupied = True
                    break
                else:
                 for slotI in self.slot_group:
                    if not getattr(slotI, 'occupied', False):
                        self.equipped = False
                        self.rect.center= slotI.rect.center
                        break

class Note(Item):
    def __init__(self, image_folder_name, image_name,groups,description,slot_group):
        super().__init__(image_folder_name, image_name,groups,description=description,slot_group=slot_group)
        self.visible = False # note popup
        self.rect = self.image.get_frect()
        self.button = Button(10,10,'X',40,40,True,30)
        self.clicked=False
        self.click_counter=0
        self.original_pos = self.rect.center
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

Notes = {'Note_test':lambda:Note('../Enemies','Rat',[Items_group,Notes_group],"Test note",Inventory_slots)}
OneTimeUseItems = {'Bottle':lambda:OnetimeUseItem('../Items','Bottle',
[Items_group,OneTimeUseItems_group],Player0.Data,'+',20,'a bottle of sanity',Inventory_slots,target_key='Sanity')
}
Equipment_Items = {'Helmet':lambda:Equipment('../Enemies','FatRat',
[Items_group,Equipment_slots],None,None,None,"Helmet",Inventory_slots,'Helmet')}

