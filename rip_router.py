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
        self.port_table = {}

    def shortest_path(self, dest):
        min_dis = INF
        neigh = None
        for neighbor in self.forward_table:
            n_dest = self.forward_table[neighbor].get(dest, INF)
            if n_dest < min_dis:
                neigh = neighbor
                min_dis = n_dest
        return min_dis, neighbor

    def handle_discovery(self, src, packet, port):
        dist = INF
        if packet.is_link_up:
            dist = 1
        col = self.forward_table.get(src, None)
        if col == None:
            self.forward_table[src]      = {}
            self.forward_table[src][src] = dist
            self.port_table[src]         = port
        else:
            col[src] = dist
        

    def handle_rx (self, packet, port):
        # Add your code here!
        src   = packet.src.name
        dst   = packet.dst.name
        ptype = packet.__class__.__name__
        routing_update = RoutingUpdate()
        table_changed = False
        
        if ptype == 'DiscoveryPacket':
            self.handle_discovery(src, packet, port)
            for neighbor in self.forward_table:
                if neighbor == None:
                    self.forward_table[neighbor] = {}  
                    
                col = self.forward_table[neighbor]
                for dest in col:
                    dist = self.forward_table.get((port, dest), INF)
                    #table_changed = True
                    routing_update.add_destination(dest, dist)

        if ptype == 'RoutingUpdate':
            all_dest = packet.all_dests()
            for dest in all_dest:
                neigh_to_dest        = packet.get_distance(dest)
                self_to_neigh        = self.forward_table[src][src]
                total_dist           = neigh_to_dest + self_to_neigh
                self_to_dest, neigh  = self.shortest_path(dest)
                if total_dist < self_to_dest:
                    self.forward_table[src][dest] = total_dist
                    table_changed = True
                    routing_update.add_destination(dest, total_dist)
        
        #send routing update
        if table_changed: 
            self.send(routing_update, None, flood=True)
            if DEBUG:
                self.log("Flooding routing update")
            
        #packet is a data packet
        if ptype is not 'RoutingUpdate' and ptype is not 'UpdatePacket':
            #neighbor to forward to
            self_to_dest, neigh = self.shortest_path(dest)
            forward_to_port     = self.port_table[neigh]
            self.send(packet, forward_to_port)
            
        if DEBUG:
            self.log("I am:  %s" % self.name)
            self.log("My packet: %s" % packet.__class__.__name__)
            self.log("Source: %s" % src)
            self.log("Destination: %s" % dst)
        #  self.log("Distance from %s to %s is: %d" % (src, self.name, routing_update.get_distance(src)))
            self.log("All Distances: %s" % str(routing_update.all_dests))
            self.log("routing table: %s\n" % str(self.forward_table)) 
        

