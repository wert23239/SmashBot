import random
class ExperienceReplay:
    def __init__(self,buffer_size = 50000):
        self.buffer=[]
        self.buffer_size=buffer_size
    
    def extend(self,rows):
        # Add rows to front of list.
        self.buffer[0:0]=rows
        del self.buffer[self.buffer_size:]

    def sample(self,sample_size):
        if sample_size>len(self.buffer):
            return self.buffer
        else:
            return random.sample(self.buffer,sample_size)