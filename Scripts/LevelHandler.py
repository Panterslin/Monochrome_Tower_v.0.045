import random
from Game_Data import Door,Player0
from Scripts.Labels import AppearingLabel
from Settings import *
class Room:
    def __init__(self,name,scene_manager,scene_type):
        self.name = name
        self.scene_manager = scene_manager
        self.scene_type = scene_type
    def run(self):
        self.scene_manager.set_scene(self.scene_type)
Doors ={
    'Door0':lambda:Door('Doors','Door0',0,0,'Door0_alt.png',0),
    'Door10':lambda:Door('Doors','Door10',0,0,'Door10_alt.png',10),
    'Door20':lambda:Door('Doors','Door20',0,0,'Door20_alt.png',20),
    'Boss':lambda:Door('Doors','BossDoor',0,0,'BossDoor_alt.png',0)
}
class LevelHandler:
    def __init__(self, data_corridor,data_room, room_count=8):
        self.data_corridor = data_corridor
        """ data for corridor generation eg. {'Door10':[30 chance in % for door, 2 instances in floor]} """
        self.number_of_rooms = room_count
        """ data for room generation eg. {'Door10':{'Battle1':[30,2],'Riddle':[20,1]}} """
        self.data_room = data_room
        self.door =None
        self.corridor = ['','','']
        self.current_room = 1
        self.room_placements = [(WINDOW_WIDTH / 4, WINDOW_HEIGHT / 1.85),
         (WINDOW_WIDTH / 1.9, WINDOW_HEIGHT / 1.85),
         (WINDOW_WIDTH / 1.23, WINDOW_HEIGHT / 1.85),(WINDOW_WIDTH/2.2,WINDOW_HEIGHT/3.3)]
        #self.generate_corridor()
        self.doors_obj =[None,None,None]
        self.save_loaded = True
        self.guaranteed_candidates = [(room_key, room_info) for room_key, room_info in self.data_corridor.items() if len(room_info)==3]
        self.title = None
    def title_flash(self,title):
        self.title = AppearingLabel(0.03,title,'white',WINDOW_WIDTH/2,WINDOW_HEIGHT/2,120,FONT_PATH,(800,120),(80,90))
    def generate_door(self):
        if self.number_of_rooms <= self.current_room:
            return 'Boss'

        for room_key, room_info in list(self.guaranteed_candidates): # for guaranteed doors/rooms
                if self.current_room == room_info[2]:
                     self.guaranteed_candidates.remove((room_key,room_info))
                     return room_key
        candidates = [(k, v[0], v) for k, v in self.data_corridor.items() if v[1] > 0]
        if not candidates:
            return None
            """fallback = [k for k, v in self.data_corridor.items() if v[1] > 0]
            return fallback[0] if fallback else list(self.data_corridor.keys())[0]"""
        total_prob = sum(prob for _, prob, _ in candidates)
        rando = random.randint(1, total_prob)
        current = 0
        if isinstance(self.data_corridor,dict):
            for key,prob,values in candidates:
                current += prob
                if  rando <= current :
                    values[1] -= 1
                    return key
        return list(self.data_corridor.keys())[0]
    def load_corridor(self,corridor):
        self.corridor = corridor
        self.save_loaded = False
    def generate_corridor(self):
        self.current_room += 1
        Player0.Data['Current_Room'] = self.current_room
        if self.number_of_rooms <= self.current_room: #generate boss door
            boss = Doors['Boss']()
            boss.create_door(self.room_placements[3][0],
                                                    self.room_placements[3][1])
            self.corridor = [None,'Boss',None]
            self.doors_obj =[None,boss,None]
            return
        else:
            if self.save_loaded:
                new_corridor = []
                for _ in range(3):
                    dk = self.generate_door()
                    if dk is None:
                        dk = 'Door0'
                    new_corridor.append(dk)
                self.corridor = new_corridor
                #self.corridor = [self.generate_door(),self.generate_door(),self.generate_door()]
            else:
                self.save_loaded = True
            self.doors_obj =[]
            for i,key in enumerate(self.corridor):
                obj = Doors[key]()
                obj.create_door(self.room_placements[i][0],self.room_placements[i][1])
                self.doors_obj.append(obj)
            print (self.corridor)
        Player0.Data['Corridor']=self.corridor
    def generate_room(self,key=None):
        if self.number_of_rooms <= self.current_room:
            return 'Boss'
        door_rooms=self.data_room.get(key,{})
        candidates=[]
        for room_key, room_info in door_rooms.items(): # if room is available adds to candidates
            if isinstance(room_info, list) and len(room_info) >= 2:
                prob, ins = room_info[0], room_info[1]
                if ins > 0:
                    candidates.append((room_key, prob, room_info))
        if not candidates:
            return None
        total_prob = sum(prob for _, prob, _ in candidates)
        rando = random.randint(1, total_prob)
        current = 0
        for room_key, prob, values in candidates:
            current += prob
            if rando <= current:
                values[1] -= 1
                if values[1] == 0:
                    self._zero_room_globally(room_key)
                    print('zeroed')
                print(room_key)
                return room_key
        room_keys =list(self.data_room[key].keys())
        print (room_keys[0])
        return room_keys[0] if room_keys else list(self.data_room.keys())[0]
    def generate_scene(self,key=None,key_room=None):
        if key is not None and key_room is not None:
            room_data = self.data_room[key].get(key_room,[])
            if len(room_data) == 3:
                print(room_data[2])
                return room_data[2]
            else:
                return key_room
        return None
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            for i, door in enumerate(self.corridor):
                if Doors[door]().create_door(self.room_placements[i][0], self.room_placements[i][1]):
                    key = self.generate_door()
                    key_room = self.generate_room(key)
                    self.generate_scene(key,key_room)
            pygame.display.update()
            clock.tick(60)
    def update(self):
        for i, obj in enumerate(self.doors_obj):
                Player0.Data['Corridor'] = self.corridor
                if obj is None:
                    continue
                else:
                    clicked = obj.create_door(self.room_placements[i][0], self.room_placements[i][1]) if self.corridor[i]!='Boss'  \
                        else obj.create_door(self.room_placements[3][0], self.room_placements[3][1])
                if clicked:
                    key = self.corridor[i]
                    print('clicked')
                    key_room = self.generate_room(key)
                    scene = self.generate_scene(key,key_room)
                    return key_room,scene
        return None

    def _zero_room_globally(self, room_key):
        for _door, rooms in self.data_room.items():
            info = rooms.get(room_key)
            if isinstance(info, list) and len(info) >= 2:
                info[1] = min(info[1], 0)
                info[0]=0
Levels = {
    'floor1':lambda:LevelHandler(data_corridor={'Door10':[30,6],'Door0':[40,10],'Door20':[50,8],'Boss':[0,1]}
    ,data_room={'Door10':{'FatRat':[50,10,'Battle'],'Riddle':[80,2],'Elite':[10,1],'Chest':[20,4]},
      'Door0':{'Bottles':[40,10],'Rat':[40,10,'Battle'],'FatRat':[10,2,'Battle'],'Note':[10,1]},
      'Door20':{'DecayingRat':[50,10,'Battle'],'BlightMother':[10,1],'Shop':[10,1],'Fireplace':[50,1],
                'Bile':[50,1]},'Boss':{'Boss':[0,1,'Battle']}},room_count=8)


}
#Levels['floor1']().run()






