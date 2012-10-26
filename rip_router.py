from sim.api import *
from sim.basics import *

DEBUG = False

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
            if neighbor in self.port_table:
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
                        if neigh == None:
                            neigh = neighbor

        return min_dis, neigh

    def all_shortest_dists(self, node):
        paths = {}
        for neigh,col in self.forward_table.items():
            for dest,dist in col.items():
                if dest != node and self != neigh:
                    if False:
                        self.log("paths is: %s" % str(paths))
                        self.log("dist is: %s" % dist)

                    if paths.get(dest, INF) > dist:
                    # implement split horizon poison reverse
                        if node is neigh:
                            dist = INF
                        paths[dest] = dist
        return paths

    def contains_shortest_path(self, neighbor):
        involved_in_shortest_path = []
        all_dest_reachable = {}
        for neigh, col in self.forward_table.items():
            for dest, dist in col.items():
                if self != neigh:
                    all_dest_reachable[dest] = dist
        for dest in all_dest_reachable:
            min_dist, neigh = self.shortest_path(dest, self.forward_table)
            involved_in_shortest_path.append(neigh)
        if neighbor in involved_in_shortest_path:
            return True
        else:
            return False
            

    def handle_discovery(self, src, packet, port):
        dist = INF
        table_changed = False
        if src != self:
            if packet.is_link_up:
                dist = 1
                col = self.forward_table.get(src, None)
                if col == None:
                    self.forward_table[src]      = {}
                    self.forward_table[src][src] = dist
                    self.port_table[src]         = port
                else:
                    col[src] = dist
            else:
                table_changed = True
                del self.forward_table[src]
                del self.port_table[src]
        return table_changed
                

    #NEED TO NOT REMOVE NIEGHBOR SO SPLIT HORIZON POISON REVERSE    
   
    def handle_rx (self, packet, port):
        # Add your code here!
        src   = packet.src
        dst   = packet.dst
        ptype = packet.__class__.__name__
        table_changed = False
        
        if ptype == 'DiscoveryPacket':
            table_changed = self.handle_discovery(src, packet, port)
            for neighbor in self.forward_table:
                if neighbor == None:
                    self.forward_table[neighbor] = {}  
                    
                col = self.forward_table[neighbor]
                for dest in col:
                    dist = col.get(dest, INF)
                    table_changed = True
                    

        if ptype == 'RoutingUpdate':
            if self.port_table.get(src, None) is not None:
                all_dest = packet.all_dests()
                if DEBUG:
                    self.log("all_dest is %s" %str(all_dest))
                    self.log("packet.paths is %s" %str(packet.paths))
                for dest in all_dest:
                    if dest != self:
                        if packet.get_distance(dest) == INF:
                            #explicit withdrawal
                            self.forward_table[src][dest] = INF
                        neigh_to_dest        = packet.get_distance(dest)
                        self_to_neigh        = self.forward_table[src][src]
                        total_dist           = neigh_to_dest + self_to_neigh
                        self_to_dest, neigh  = self.shortest_path(dest, self.forward_table)
                        if total_dist < self_to_dest:
                            self.forward_table[src][dest] = total_dist
                            if False:
                                self.log("should be %s is %s" % (dest, str(self.forward_table)))
                            table_changed = True
                for dest in self.forward_table[src]:
                    if dest not in all_dest and dest != src:
                        min_dis, neighbor = self.shortest_path(dest, self.forward_table)
                        if dest == neighbor:
                            table_changed = True
                        self.forward_table[src][dest] = INF

        #send routing update
        if table_changed: 
            if DEBUG:
                self.log("Port table: %s " % str(self.port_table))
            for neighbor in self.port_table:
                neigh_port = self.port_table[neighbor]
                if DEBUG:
                    self.log("I am sending to  %s" % neighbor)
                updated_path = self.all_shortest_dists(neighbor)
                if DEBUG:
                    self.log("Updated_path: %s" % updated_path)

                no_neigh_routing_up = RoutingUpdate()
                for node,dist in updated_path.items():
                    if node != neighbor:
                        no_neigh_routing_up.add_destination(node, dist)
                if DEBUG:
                    self.log("Sending finalized routing update: %s to %s" % (no_neigh_routing_up.str_routing_table(), neighbor))
#                if not (ptype == 'DiscoveryPacket' and no_neigh_routing_up == {}):
                self.send(no_neigh_routing_up, neigh_port)
            
        #packet is a data packet
        if ptype is not 'RoutingUpdate' and ptype is not 'DiscoveryPacket':
            #neighbor to forward to
            self_to_dest, neigh = self.shortest_path(dst, self.forward_table)
            forward_to_port     = self.port_table[neigh]
            self.send(packet, forward_to_port)
            
        if DEBUG:
            self.log("Receiving packet: %s" % packet.__class__.__name__)
            self.log("Source: %s" % src)
            self.log("Destination: %s" % dst)
            if ptype == 'RoutingUpdate':
                self.log("Table in received routing update: %s" % str(packet.str_routing_table()))
            self.log("forward table:")
            for item in self.forward_table:
                self.log("%s: %s" % (item.__repr__(), str(self.forward_table[item])))
            self.log("\n")
