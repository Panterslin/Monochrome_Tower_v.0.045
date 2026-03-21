
from Settings import *
All_sprites=pygame.sprite.Group()
Items_group=pygame.sprite.Group()
Notes_group=pygame.sprite.Group()
OneTimeUseItems_group=pygame.sprite.Group()
Inventory_slots = pygame.sprite.Group()
Equipment_slots = pygame.sprite.Group()
Labels_group=pygame.sprite.Group()
Buttons_group=pygame.sprite.Group()
Equipment_group=pygame.sprite.Group()
Input_group=pygame.sprite.Group()
Characters_group=pygame.sprite.Group()
Overworld_items_group=pygame.sprite.Group()#group for disabling functionality of items in overworld (for inventory)

def isolate_sprites(group): # for isolating certain sprite from processes (such as killings)
    isolated_group=pygame.sprite.Group()
    for sprite in group.sprites():
        isolated_group.add(sprite)
    return isolated_group

def load_isolated(iso_group,group):
    for sprite in iso_group.sprites():
        group.add(sprite) if not sprite in group else None