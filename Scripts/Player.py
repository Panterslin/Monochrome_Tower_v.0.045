
import Save_Handler
class Player:
    def __init__(self,save_data_:dict):
        self.Data = save_data_
    def update_stats(self,player_data:dict):
        self.Data= player_data
    def reset_stats(self):
        Save_Handler.generate_data()
        self.Data['HP'] = 100
        self.Data['Sanity'] = 150
        self.Data['Max_HP'] = 100
        self.Data['Max_Sanity'] = 150
        self.Data['Current_Floor'] = 1
        self.Data['Current_Room'] = 1
        self.Data['Level'] = 1
        self.Data['Defense']=0
        self.Data['Money'] = 0
        self.Data['Experience'] = 0
        self.Data['Corridor'] = [None,None,None]
        for item in self.Data['Items']:
            self.Data['Items'].remove(item)
    def get_value(self,key,item_key=None):
        return self.Data[key] if isinstance(self.Data[key],int) else self.Data[key][item_key]