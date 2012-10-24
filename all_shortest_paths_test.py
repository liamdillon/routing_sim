import unittest
import rip_router

class TestAllShortestDists(unittest.TestCase):
    
    def setUp(self):
        self.test_table = {'a' : {'a':1, 'b':2}, 'b' : {'a':2, 'b':1}}

    def test_all_shortest_dists(self):
        r = rip_router.RIPRouter()
        h = r.all_shortest_dists(self.test_table)
        should_be = {'a':1, 'b':1}
        self.assertEqual(h, should_be)

if __name__ == '__main__':
    unittest.main()