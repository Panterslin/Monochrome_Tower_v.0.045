import sys
import operator
from Save_Handler import json,join
from Labels import AppearingLabel
from Scripts.Game_Data import Button,AnimatedObject,SceneManager
from Game_Data import AnimatedObject
from Settings import *
from Items import Notes,Equipment_Items,OneTimeUseItems
from Groups import Characters_group
global current_game # should be set by game class
def load_character(character):
    for ch in Characters_group.sprites():
        if ch.name == character:
            return ch
    return None
def load_anim(character,anim_name):
    ch_sprite = load_character(character)
    ch_sprite.animate()
    ch_sprite.animation_play(ch_sprite.count_frames(anim_name),0.05,anim_name)
def get_manager(game):
    try: return game.SceneManager
    except: return None
def load_reward(reward):
    def get_reward():
        registry = {**Notes, **Equipment_Items, **OneTimeUseItems}
        try:
            cls = []
            for item_name in reward:
                clss = registry.get(item_name)
                if clss is None:
                    print(f"Unknown item: {item_name}")
                    continue
                rew_obj = clss()
                cls.append(rew_obj)
                return cls
        except:
            cls = registry.get(reward)
            if cls is None:
                print(f"Unknown item name: {reward}")
                return None
            return cls()

    rewards = get_reward()
    try: # disable in inventory, show in overworld
        for reward in rewards:
            reward.enabled = False
            reward.image.set_alpha(0)
    except:
        rewards.enabled = False
        rewards.image.set_alpha(0)



operands = {
 "=":operator.eq,
 ">":operator.gt,
 "<":operator.lt,
 "<=":operator.le,
 ">=":operator.ge,
 "!=":operator.ne,
}
callbacks = { # o is an operator
    'if':lambda arg1,arg2,o:o(arg1,arg2),
    'reaction':lambda character,anim_name: load_anim(character,anim_name),
    'triggerScene':lambda scene_name,enemy: get_manager(current_game).create_scene(scene_name,enemy), # enemy is optional
    'triggerReward':lambda reward: load_reward(reward),


}
file_path = 'Dialogues'
def load_dialogue(file):
    with open(join(ROOT_DIR,file_path,file + '.json'), 'r') as f:
        return json.load(f)
def compute_dialogue(dialogue:list):
    offset = 0
    for branch in dialogue:
        if branch['nodeType'] ==0:
            if len(branch['responses']) ==0:
                yield AppearingLabel(0.03,branch['text'],'white',100,100)
            else:
                choices = []
                for response in branch['responses']:
                    Button(100+offset,100,dialogue[response]['text'],50,100,True,30)
                    offset += WINDOW_WIDTH/len(branch['responses'])
                yield AppearingLabel(0.03,branch['text'],'white',100,100)
        elif branch['type'] == 'responses':
            pass


class Test:
    def __init__(self):
        self.dialogue = load_dialogue('sample2')
        self.current_node =0
        self.called = False
        for node in self.dialogue:
            if node['id'] == self.current_node:
                self.label = AppearingLabel(0.03, node['text'], 'white', WINDOW_WIDTH/2, 100)
                self.buttons = []
                self._build_buttons_for_node(node['id'])
                break
        #compute_dialogue(load_dialogue('sample_dialogue'))

    def _build_buttons_for_node(self, node_idx):
        # Clear old buttons
        self.buttons.clear()
        for i,node in enumerate(self.dialogue):
            if node['id'] == node_idx:
                node_idx=i
                break
        node = self.dialogue[node_idx]
        responses = node.get('responses', [])
        if not responses:
            #self.current_node = self.dialogue[node_idx]['nextNodeId']
            return
        # Layout buttons across the screen
        spacing = WINDOW_WIDTH / max(1, len(responses))
        x = spacing/ max(1, len(responses))
        y = 300
        for rid in responses:
            for nodes in self.dialogue:
                if rid ==  nodes['id']:
                    txt = nodes['text']
                    new_btn = Button(x, y, txt, 200 if len(txt)<5 else 30*len(txt)
                    ,80, True, 40, True, (x + 60, y + 10))
                    self.buttons.append(new_btn)
                    if x + spacing + 30*len(txt)*4 < WINDOW_WIDTH:
                        x += spacing
                    else:
                        x=spacing/ max(1, len(responses))
                        y+=200
                    break
    def compute_dialogue_callbacks(self,node_idx):
        current_node = None
        registry = {**operands, **callbacks}
        for i,node in enumerate(self.dialogue):
            if node['id'] == node_idx:
                current_node = node
                break
        if len(current_node['selected_callbacks'])<1:
            return
        else:
            for callback in current_node['selected_callbacks']:
                parts = callback.split('_')
                op_call = registry.get(parts[2]) if len(parts)>2 else None
                call = registry.get(parts[0])
                if call is None:
                    print(f"Warning: Callback '{parts[0]}' not found in registry.")
                    continue  # Skip to the next callback
                print('called'+parts[0])
                if op_call is not None:
                    call(parts[1],parts[3],op_call)
                    return
                if len(parts)==2:
                    call(parts[1])
                    return
                elif len(parts)==3:
                    call(parts[1],parts[2])
                    return
                elif len(parts)==4:
                    call(parts[1],parts[2],parts[3])
                    return
                print('call failed')

    def update(self):
            pygame.mouse.set_visible(True)
            screen.fill('black')
            if self.label.dynamic_render() and not self.called:
                print(self.current_node)
                self.called = True
                self.compute_dialogue_callbacks(self.current_node)
            for i, btn in enumerate(self.buttons):
                if len(self.buttons) == 0:
                    return
                if btn.update():
                        for node in self.dialogue:
                            if node['id'] == self.current_node:
                                next_node = node['responses'][i] if \
                                node['responses'][i] else node['nextNodeId']
                                self.current_node = next_node
                                break
                        print(self.current_node)
                        for node in self.dialogue:
                            if node['id'] == self.current_node:
                                self.current_node = node['nextNodeId'] if node['nextNodeId']!=-1 else node['id']
                                break
                        print(self.current_node)
                        for node in self.dialogue:
                            if node['id'] == self.current_node:
                                txt = node['text']
                                break
                        self.label = AppearingLabel(0.03, txt, 'white',  WINDOW_WIDTH/2, 100)
                        self.called=False

                        self._build_buttons_for_node(self.current_node)
                        break

            pygame.display.update()


#Test().run()