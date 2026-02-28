import json
import os
from os.path import join
def generate_data():
    dictio={
        'HP': 100,
        'Sanity': 150,
        'Max_HP': 100,
        'Max_Sanity': 150,
        'Defense':0,
        'Money':0,
        'Current_Floor': 1,
        'Current_Room': 1,
        'Level': 1,
        'Experience': 0,
        'Items':[],
        'Corridor':[None,None,None]
    }
    return dictio

Clear_Data=generate_data()
Default_Data=generate_data()
Player_Data=generate_data()
Player_Data2=generate_data()

def delete_data(savefile_index:int):
    with open(join('../Saves','Save_File'+str(savefile_index)+'.txt'), 'w') as save_file:
        json.dump(Clear_Data, save_file)
def update_data(current_data:dict,new_data:dict):
    current_data = new_data
def save_data(savefile_index:int,data:dict):
    global Player_Data
    global Player_Data2
    if not os.path.exists('../Saves'):
        os.makedirs('../Saves')
    with open(join('../Saves','Save_File'+str(savefile_index)+'.txt'), 'w') as save_file:
        if savefile_index == 1:
            json.dump(data,save_file)
        if savefile_index == 2:
            json.dump(data,save_file)
def load_data(savefile_index:int)->bool:
    success=False
    global Player_Data
    global Player_Data2
    global Default_Data
    file_path = join('../Saves', 'Save_File' + str(savefile_index) + '.txt')
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as save_file:
                if savefile_index==1:
                  Player_Data = json.load(save_file)
                elif savefile_index==2:
                    Player_Data2 = json.load(save_file)
                else:
                    Default_Data = json.load(save_file)
            success= True
        except:
            if load_data(0):
                success=True
            else:
                print('No save file')
                success=False
        return success
load_data(1)
load_data(2)