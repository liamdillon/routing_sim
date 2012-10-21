from sim.api import *
from sim.basics import *

'''
Create your learning switch in this file.
'''
class LearningSwitch(Entity):
    def __init__(self):
        # keys are destinations, values port numbers
        self.f_table = {}

    def handle_rx (self, packet, port):
        src = packet.src
        dst = packet.dst
        org = packet.trace[0]
        
        f_port = self.f_table.get(dst)
        
        
        if dst != None and dst != self: 
            if f_port:
                if f_port != port:
                    self.send(packet, f_port)
            else:
                self.f_table[org] = port
                self.send(packet, port, flood=True)
