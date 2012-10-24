import sys
sys.path.append('.')

from sim.api import *
from sim.basics import *
from rip_router import RIPRouter
import sim.topo as topo
import os
import time

class ReceiveEntity (Entity):
    def __init__(self, expected):
        self.expect = expected
        self.unexpecteds = -1 # we expect a single packet

    def handle_rx(self, packet, port):
        if isinstance(packet, DiscoveryPacket):
            return
        self.unexpecteds += 1
        self.send(packet, port, flood=True)
