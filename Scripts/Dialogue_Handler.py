import sys

from Save_Handler import json,join
from Labels import AppearingLabel
from Scripts.Game_Data import Button
from Settings import *

file_path = '../Dialogues'
def load_dialogue(file):
    with open(join(file_path,file + '.json'), 'r') as f:
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
        self.dialogue = load_dialogue('sample_dialogue')
        self.current_node =0
        self.label = AppearingLabel(0.03, self.dialogue[self.current_node]['text'], 'white', WINDOW_WIDTH/2, 100)
        self.buttons = []
        self._build_buttons_for_node(self.current_node)

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
            self.current_node = self.dialogue[node_idx]['nextNodeId']
            return
        # Layout buttons across the screen
        spacing = WINDOW_WIDTH / max(1, len(responses))
        x = 300
        y = 300
        for rid in responses:
            for nodes in self.dialogue:
                if rid ==  nodes['id']:
                    txt = nodes['text']
                    self.buttons.append(Button(x, y, txt, 200, 80, True, 40, True, (x + 60, y + 10)))
                    x += spacing
                    break
    def compute_dialogue_callbacks(self):
        for node in self.dialogue:
            if len(node['selected_callbacks'])>0:
                for callback in node['selected_callbacks']:
                    callback()

    def run(self):
        while True:
            screen.fill('black')
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.label.dynamic_render()
            for i, btn in enumerate(self.buttons):
                if btn.update():
                        # go to the response node that this button represents
                    next_node = self.dialogue[self.current_node]['responses'][i] if \
                        self.dialogue[self.current_node]['responses'][i] else self.dialogue[self.current_node]['nextNodeId']
                    self.current_node = next_node if self.dialogue[next_node]['nodeType'] == 0 else self.dialogue[next_node]['nextNodeId']
                    print(self.current_node)
                    for node in self.dialogue:
                        if node['id'] == self.current_node:
                            self.current_node = node['nextNodeId'] if node['nextNodeId'] else 0
                            break
                    print(self.current_node)
                    for node in self.dialogue:
                        if node['id'] == self.current_node:
                            txt = node['text']
                            break
                    self.label = AppearingLabel(0.03, txt, 'white',  WINDOW_WIDTH/2, 100)
                    self._build_buttons_for_node(self.current_node)
                    break

            pygame.display.update()


Test().run()