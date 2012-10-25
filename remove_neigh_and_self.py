import unittest
import rip_router
from copy import deepcopy 
class TestRemoveNeighAndSelf(unittest.TestCase):
    
    def setUp(self):
        self.test_table = {'a' : {'a':1, 'b':2}, 'b' : {'a':2, 'b':1}, 'c' : {'a':4,'b':5} }

    def test_remove_neigh_and_self(self): 
        r = rip_router.RIPRouter()
        r.forward_table = deepcopy(self.test_table)
        h = r.remove_neigh_and_self('a', 'b')
        should_be = {'b' : {'a':2}, 'c': {'a':4,'b':5}}
        self.assertEqual(h, should_be)

if __name__ == '__main__':
    unittest.main()
