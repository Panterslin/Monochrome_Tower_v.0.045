from json import JSONDecodeError
import copy
from Groups import *
from Save_Handler import json,os,join
class MoveTool:
    def __init__(self,group=Buttons_group,scene_name_getter=None,scenes=None,key_getter=None):
        self.dragged = False
        self.group = group

        self.key_getter = key_getter or (lambda s: getattr(s, 'dev_id', getattr(s, 'text', getattr(s, 'image_name', None))))
        self.scene_name_getter = scene_name_getter or (lambda: 'global')
        self.sprite_dragged = []
        self.scenes = scenes
        self.original_positions = self._capture_original_positions()
        self.data = self.load_sprite_pos()
        self.init_data = copy.deepcopy(self.data)
        self.apply_positions()
        self.alt_pressed = False

    def _capture_original_positions(self):
        scene = self.current_scene()
        snap = {scene: {}}
        for sprite in self.group:
            key = self.key_getter(sprite)
            if not key:
                continue
            if getattr(sprite, 'rects', None):
                snap[scene][key] = [tuple(r.center) for r in sprite.rects]
            else:
                snap[scene][key] = tuple(sprite.rect.center)
        return snap
    def capture_scene_positions(self):
        scene_snapshot = self._capture_original_positions()
        self.original_positions.update(scene_snapshot)
    def factory_reset(self):
        scene = self.current_scene()
        original_data = self.original_positions.get(scene, {})
        self.data[scene] = copy.deepcopy(original_data)
        self.apply_positions()
        self.save_sprite_pos()
    def current_scene(self):
        return self.scene_name_getter()
    def move_sprites(self,group):
        pressed = pygame.mouse.get_pressed()[2]
        scene = self.current_scene()
        for i,sprite in enumerate(group):
            key = self.key_getter(sprite)
            if (pressed or self.alt_pressed) and sprite.rect.collidepoint(pygame.mouse.get_pos()):
                if not 0<pygame.mouse.get_pos()[0]<WINDOW_WIDTH  or not 0<pygame.mouse.get_pos()[1]<WINDOW_HEIGHT:
                    break
                self.sprite_dragged.append(sprite) if sprite not in self.sprite_dragged else None
                if len(self.sprite_dragged) > 1:
                   continue
                if not getattr(sprite, 'rects', None):
                    sprite.rect.center = pygame.mouse.get_pos()
                else:
                    for rect in sprite.rects: rect.center = pygame.mouse.get_pos()

                self.dragged = True
                break
            elif not (pressed or self.alt_pressed) and sprite.rect.collidepoint(pygame.mouse.get_pos()) and self.dragged:
                self.dragged = False
                print('dragged')
                self.sprite_dragged.clear()
                if not getattr(sprite, 'rects', None):
                    self.data[scene][key] = sprite.rect.center
                else:
                    self.data[scene][key] = [rect.center for rect in sprite.rects]
                self.save_sprite_pos()
                return sprite.rect.center
            self.sprite_dragged.clear()
        return None
    def reset_sprite_pos(self):
        self.data = copy.deepcopy(self.init_data)
        self.apply_positions()
        self.save_sprite_pos()
    def apply_positions(self):
        if not self.data:
            return
        scene = self.current_scene()
        scene_map = self.data.get(scene, {})
        for sprite in self.group:
            key = self.key_getter(sprite)
            if not key:
                continue
            pos = scene_map.get(key)
            if pos is None:
                continue
            if not getattr(sprite, 'rects', None):
                sprite.rect.center = tuple(pos)
            else:
                for rect, p in zip(sprite.rects, pos):
                    rect.center = tuple(p)
    def save_sprite_pos(self):
        if not os.path.exists('SpriteData'):
            os.makedirs('SpriteData')
        with open(join(ROOT_DIR,'SpriteData', 'Sprite_Positions' '.txt'), 'w') as pos_file:
            json.dump(self.data, pos_file,indent=2)
    def load_sprite_pos(self):
        path = join(ROOT_DIR,'SpriteData', 'Sprite_Positions' '.txt')
        if os.path.exists(path):
            with open(path, 'r') as pos_file:
                return json.load(pos_file)
        return {key:{} for key in self.scenes}
