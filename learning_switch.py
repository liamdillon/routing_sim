from sim.api import *
from sim.basics import *

DEBUG = False

'''
Create your learning switch in this file.
'''
class LearningSwitch(Entity):
    def __init__(self):
        # keys are destinations, values port numbers
        self.f_table = {}
        pass
    def handle_rx (self, packet, port):
        src = packet.src.name
        dst = packet.dst.name
        org = packet.trace[0]
        f_port = self.f_table.get(dst)
        
        if DEBUG:
            import pdb; pdb.set_trace()

            print "packet is " + packet.__repr__()
            print "src is " + src
            print "dst is " + dst

            print "packet.trace[0] is " + packet.trace[0].__repr__() + "\n"

        if dst is not "NullAddress" and dst is not self.name:
            if f_port is not None:
                if f_port is not port:
                    self.f_table[src] = port
                    self.send(packet, f_port)
            else:
                self.f_table[src] = port
                self.send(packet, port, flood=True)

