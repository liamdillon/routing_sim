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

    def shortest_path(self, dest, table):
        min_dis = INF
        neigh = None
        for neighbor in table:
            n_dest = table[neighbor].get(dest, INF)
            if n_dest < min_dis:
                neigh = neighbor
                min_dis = n_dest
        return min_dis, neighbor

    def all_shortest_dists(self, table):
        new_table = {}
        for neigh,col in table.items():
            for dest,dist in col.items():
                if new_table.get(dest, INF) > dist:
                    new_table[dest] = dist
        return new_table

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
        
    def remove_neigh(self, neigh):
        table_without_neigh  = self.forward_table.copy()
        for neighbor in self.forward_table:
            if neighbor == neigh:
                del table_without_neigh[neigh]
        return table_without_neigh

  

    def handle_rx (self, packet, port):
        # Add your code here!
        src   = packet.src
        dst   = packet.dst
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
                    dist = col.get(dest, INF)
                    table_changed = True
                    routing_update.add_destination(dest, dist)

        if ptype == 'RoutingUpdate':
            all_dest = packet.all_dests()
            self.log("all_dest is %s" %str(all_dest))
            self.log("packet.paths is %s" %str(packet.paths))
            for dest in all_dest:
                if dest is not self:
                    neigh_to_dest        = packet.get_distance(dest)
                    self_to_neigh        = self.forward_table[src][src]
                    total_dist           = neigh_to_dest + self_to_neigh
                    self_to_dest, neigh  = self.shortest_path(dest, self.forward_table)
                    if total_dist < self_to_dest:
                        self.forward_table[src][dest] = total_dist
                        table_changed = True
                        routing_update.add_destination(dest, total_dist)
        
        #send routing update
        if table_changed: 
            for neighbor in self.port_table:
                neigh_port = self.port_table[neighbor]
                table_without_neigh = self.remove_neigh(neighbor)
                for neigh in table_without_neigh:
                    
#                    dist, n = self.shortest_path( , self.forward_table)
                    no_neigh_routing_up = RoutingUpdate()
                    no_neigh_routing_up.paths = table_without_neigh
                    self.send(no_neigh_routing_up, neigh_port, flood=False)
            
        #packet is a data packet
        if ptype is not 'RoutingUpdate' and ptype is not 'UpdatePacket':
            #neighbor to forward to
            self_to_dest, neigh = self.shortest_path(dest, self.forward_table)
            forward_to_port     = self.port_table[neigh]
            self.send(packet, forward_to_port)
            
        if DEBUG:
            self.log("I am:  %s" % self.name)
            self.log("My packet: %s" % packet.__class__.__name__)
            self.log("Source: %s" % src)
            self.log("Destination: %s" % dst)
        #  self.log("Distance from %s to %s is: %d" % (src, self.name, routing_update.get_distance(src)))
            self.log("All Destinations: %s" % str(routing_update.all_dests()))
            self.log("routing table: %s\n" % str(self.forward_table)) 
        

