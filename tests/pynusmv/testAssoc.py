import unittest

from pynusmv_lower_interface.nusmv.utils import utils as _u
from pynusmv.init        import init_nusmv, deinit_nusmv
from pynusmv.collections import Assoc
from pynusmv.node        import Node 
from pynusmv.parser      import parse_simple_expression

class TestAssoc(unittest.TestCase):
    """
    This class implements a few simple tests to validate the proper behavior
    of the Assoc class
    """
    
    def setUp(self):
        init_nusmv()    
     
    def tearDown(self):
        deinit_nusmv()
    
    def test_associative_array(self):
        """
        This function tests the basic functions of the associative array proto
        """
        h = Assoc(_u.new_assoc(), freeit=True)
        a = Node.from_ptr(parse_simple_expression("a.car = 3"), freeit=False)
        
        # __contains__
        self.assertFalse(a in h)
        # __setitem__
        h[a] = a
        self.assertTrue(a in h)
        # __getitem__
        self.assertEqual(h[a], a)
        # __delitem__
        del h[a]
        self.assertFalse(a in h)
        
    def test_clear(self):
        """Verifies that clear works as expected"""
        h = Assoc(_u.new_assoc(), freeit=True)
        a = Node.from_ptr(parse_simple_expression("a.car = 3"), freeit=False)
        h[a] = a
        h.clear()
        self.assertFalse(a in h) 
        
    def test_copy(self):
        """Tests the copy behavior"""
        h = Assoc(_u.new_assoc(), freeit=True)
        a = Node.from_ptr(parse_simple_expression("a.car = 3"), freeit=False)
        h[a] = a
        h2= h.copy()
        self.assertTrue(a in h2)
        
    def test_from_dict(self):
        """Tests the from_dict factory"""
        a = Node.from_ptr(parse_simple_expression("a.car = 3"), freeit=False)
        d = {a: a}
        h = Assoc.from_dict(d)
        self.assertTrue(a in h)
        
    def test_empty(self):
        """Tests the empty factory"""
        a = Node.from_ptr(parse_simple_expression("a.car = 3"), freeit=False)
        h = Assoc.empty(freeit=True)
        self.assertFalse(a in h)
        