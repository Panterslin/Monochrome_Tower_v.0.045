
from pygame.time import get_ticks
class Timer:
    def __init__(self,duration=1,repeat=False,autostart=False,func=None):
        self.autostart=autostart
        self.duration=duration
        self.repeat=repeat
        self.To_Seconds = 1000
        self.StartTime=0
        self.Active=False
        self.created = False
        self.func = func
        if autostart:
            self.activate()
    def activate(self):
        self.Active=True
        if self.StartTime==0:
            self.StartTime = get_ticks()
    def deactivate(self):
        self.Active=False
        self.StartTime=0
        if self.repeat:
            self.activate()
    def update(self)->bool:
        if self.Active:
            current_time = get_ticks()
            if current_time - self.StartTime >= self.duration*self.To_Seconds:
                if self.func is not None:
                    self.func()
                self.deactivate()
                return True
        return False

