import unittest
import rip_router

class TestAllShortestDists(unittest.TestCase):
    
    def setUp(self):
        self.test_table = {'b' : {'b':1, 'c':2}, 'c' : {'c':100, 'b':100}}

    def test_all_shortest_dists(self):
        r = rip_router.RIPRouter()
        h = r.all_shortest_dists(self.test_table, 'b')
        should_be = {'b':1, 'c':100}
        self.assertEqual(h, should_be)

if __name__ == '__main__':
    unittest.main()
