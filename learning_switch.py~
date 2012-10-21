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

        f_port = self.f_table.get(dst)

        if f_port:
            if f_port != port:
                self.send(packet, f_port)
        else:
            self.f_table[src] = port
            self.send(packet, port, flood=True)
