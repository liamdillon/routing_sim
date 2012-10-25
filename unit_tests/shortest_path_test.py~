import unittest
import rip_router

class TestShortestPath(unittest.TestCase):
    
    def setUp(self):
        self.test_table = {'a' : {'b':1, 'c': 1}, 'b' : {'a':2,'c':1}, 'c' : {'a':4,'b':5} }
        self.port_table   = {'a': 1, 'b': 0, 'c': 2}

    def test_shortest_path(self): 
        r = rip_router.RIPRouter()
        r.forward_table = self.test_table
        r.port_table    = self.port_table
#        import pdb; pdb.set_trace()
        h               = r.shortest_path('c', r.forward_table)
        should_be       = (1, 'b')
        self.assertEqual(h, should_be)

if __name__ == '__main__':
    unittest.main()
