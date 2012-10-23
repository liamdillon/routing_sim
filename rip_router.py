from sim.api import *
from sim.basics import *

DEBUG = True

INF = 100

'''
Create your RIP router in this file.
'''
class RIPRouter (Entity):
    def __init__(self):
        # Add your code here!
        #forward_table [go through this node] [to get to that node]
        self.forward_table = {}
        pass

    def handle_rx (self, packet, port):
        # Add your code here!
        src   = packet.src.name
        dst   = packet.dst.name
        ptype = packet.__class__.__name__
        routing_update = RoutingUpdate()
        table_changed = False
        
        if ptype == 'DiscoveryPacket':
            if packet.is_link_up:
                col = self.forward_table.get(src, None)
                if col == None:
                    self.forward_table[src] = {}
                    self.forward_table[src][src] = 0
                else:
                    col[src] = 0
            else:
                col = self.forward_table.get(src, None)
                if col == None:
                    self.forward_table[src] = {}
                    self.forward_table[src][src] = 100
                else:
                    col[src] = 100

            for neighbor, col in self.forward_table:
                for dest in col:
                    dist = self.forward_table.get(dest, INF)
                    routing_update.add_destination(dest, dist)
                                               
        
        if DEBUG:
            self.log("I am:  %s" % self.name)
            self.log("My packet: %s" % packet.__class__.__name__)
            self.log("Source: %s" % src)
            self.log("Destination: %s" % dst)
        #  self.log("Distance from %s to %s is: %d" % (src, self.name, routing_update.get_distance(src)))
            self.log("All Distances: %s" % str(routing_update.all_dests))
            self.log("routing table: %s" % str(self.forward_table))
        

