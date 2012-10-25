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
        min_dis  = INF
        port     = None
        min_port = None
        neigh    = None
        for neighbor in table:
            n_dist = table[neighbor].get(dest, INF)
            port = self.port_table[neighbor]
            if n_dist < min_dis:
                neigh    = neighbor
                min_dis  = n_dist
                min_port = port
            elif n_dist == min_dis:
                other_port = self.port_table[neighbor]
                if other_port < min_port:
                    min_port = other_port
                    neigh    = neighbor
                
        return min_dis, neigh

    def all_shortest_dists(self, node):
        paths = {}
        for neigh,col in self.forward_table.items():
            for dest,dist in col.items():
                if (neigh != node or dest != node) and self != neigh:
                    if paths.get(dest, INF) > dist:
                    # implement split horizon poison reverse
                        if node is neigh:
                            dist = INF
                        paths[dest] = dist
        return paths

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
    
    #NEED TO NOT REMOVE NIEGHBOR SO SPLIT HORIZON POISON REVERSE    
    def remove_neigh_and_self(self, neigh):
#        self.log("We are %s" % (self.__repr__(), str(neigh)))
        table_without_neigh  = self.forward_table.copy()
        del table_without_neigh[neigh]
        if table_without_neigh.get(self, False):
            del table_without_neigh[self]
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
                        self.log("should be %s is %s" % (dest, str(self.forward_table)))
                        table_changed = True
                        routing_update.add_destination(dest, total_dist)


        #send routing update
        if table_changed: 
            for neighbor in self.port_table:
                neigh_port = self.port_table[neighbor]
                updated_path = self.all_shortest_dists(neighbor)
                # deal with split_horizon poison reverse
                
                no_neigh_routing_up = RoutingUpdate()
                for node,dist in updated_path.items():
                    no_neigh_routing_up.add_destination(node, dist)
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
        

