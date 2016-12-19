import unittest
 
from pynusmv_lower_interface.nusmv.utils import utils
 
from pynusmv.init        import init_nusmv, deinit_nusmv
from pynusmv.collections import Slist, Conversion
 
class TestSlist(unittest.TestCase):
    o2p = lambda x: utils.int_to_void_star(x)
    p2o = lambda x: utils.void_star_to_int(x) 
    IntConversion = Conversion(p2o, o2p)
        
    def setUp(self):
        init_nusmv()
     
    def tearDown(self):
        deinit_nusmv()
           
    def test_empty(self):
        """This test verifies the behavior of the 'empty' factory method"""
        lst = Slist.empty(self.IntConversion)
          
        self.assertIsNotNone(lst)
        self.assertTrue(lst.is_empty())
        
    def test_to_std_set(self):
        """Conversion to standard collections should come for free"""
        lst = Slist.empty(self.IntConversion)
        lst.push(42)
        
        self.assertEqual({42}, set(lst))
    
    def test_push_single(self):
        """
        This test verifies the behavior of push when a single push is made
        and is also responsible for validating the  the behavior of the 
        is_empty() method
        """
        lst = Slist.empty(self.IntConversion)
        lst.push(42)
        
        self.assertFalse(lst.is_empty(), "The list should contain '42'")
        self.assertEqual(len(lst), 1, "The list should contain one item")
        self.assertEqual(lst[0], 42)
    
    def test_pop_single(self):
        """This test verifies the behavior of pop when a single push is made"""
        lst = Slist.empty(self.IntConversion)
        lst.push(42)

        self.assertEqual(lst.pop(), 42)
        self.assertTrue(lst.is_empty(), "pop removes the top of the list")
    
    def test_push_multi(self):
        """The test verifies the behavior of push when many pushes are made"""
        lst = Slist.empty(self.IntConversion)
        
        self.assertTrue(lst.is_empty())
        for i in range(10): lst.push(i)
        self.assertEqual(len(lst), 10, "list should contain 10 items")
        for i in range(10): self.assertEqual(lst[i], 9-i)
    
    def test_pop_multi(self):
        """This test verifies the behavior of pop when a single push is made"""
        lst = Slist.empty(self.IntConversion)
        for i in range(10): lst.push(i)
        self.assertEqual(len(lst), 10)
        for i in range(10): self.assertEqual(lst.pop(), 9-i)
        self.assertTrue(lst.is_empty(), "pop removes the top of the list")
        self.assertEqual(len(lst), 0)
        
    def test_top(self):
        """Validates the behavior of the top function"""
        lst = Slist.empty(self.IntConversion)
        for i in range(10): lst.push(i)
        self.assertEqual(lst.top(), 9, "The top should be 9")
    
    def test_getitem(self):
        """tests the behavior of the getitem function"""
        lst = Slist.empty(self.IntConversion)
        
        self.assertTrue(lst.is_empty())
        for i in range(10): lst.push(i)
        
        for i in lst:
            self.assertEqual(lst[i], 9-i, "lst[{}] != 9-{}".format(i,i))
        
    def test_copy(self):
        """This test verifies the behavior of the copy method"""
        lst = Slist.empty(self.IntConversion)
        lst.push(42)
         
        cpy = lst.copy()
        self.assertIsNotNone(cpy, "the copy should not be none")
        self.assertFalse(cpy.is_empty(), "like the original list, cpy contains 42")
        self.assertEqual(lst, cpy, "the two lists are supposed to be equal")
        self.assertFalse(lst._ptr == cpy._ptr, "the two copies are supposed to be physically different")
         
    def test_reversed(self):
        """This method vefifies the behavior of the reversed method"""
        lst = Slist.empty(self.IntConversion)
         
        # push prepends to the list, so the numbers are in reverse order
        for i in range(10): lst.push(i)
        # here the numbers should be in the right order again
        rev = reversed(lst)
        self.assertEqual(len(rev), 10, "reversing a list removes no item")
        for i in range(10):
            self.assertEqual(rev[i], i,"rev[{}] != {}".format(i,i))
            
    def test_reverse(self):
        """This method vefifies the behavior of the reverse (mutating) method"""
        lst = Slist.empty(self.IntConversion)
         
        # push prepends to the list, so the numbers are in reverse order
        for i in range(10): lst.push(i)
        # here the numbers should be in the right order again
        lst.reverse()
        for i in range(10):
            self.assertEqual(lst[i], i,"lst[{}] != {}".format(i,i))
            
    def test_eq(self):
        """Validates the behavior of the equality test"""
        a = Slist.empty(self.IntConversion)
        b = Slist.empty(self.IntConversion)
        
        self.assertEqual(a, b, "Both lists are empty, they should be equal")
        
        a.push(42)
        self.assertFalse(a == b)
        
        a.pop()
        self.assertTrue(a == b)
        
        a.push(42)
        b.push(42)
        self.assertTrue(a == b) 
        
    def test_contains(self):
        """Validates the __contains__ behavior"""
        lst = Slist.empty(self.IntConversion)
        for i in range(10): lst.push(i)
        
        self.assertFalse(42 in lst,    "42 was never added to the list")
        self.assertTrue(42 not in lst, "42 was never added to the list")
        for i in range(10):
            self.assertTrue(i in lst)
            
    def test_len(self):
        """Validates the behavior of __len__"""
        lst = Slist.empty(self.IntConversion)
        self.assertEqual(len(lst), 0)
        
        lst.push(1)
        self.assertEqual(len(lst), 1)
        # FIXME: This is a bug in 'Slist.c' at lines 565+, 
        #        which occurs because the field size of the Slist_ptr is never 
        #        updated. It has been reported to FBK.
        # del lst[0]
        # self.assertEqual(len(lst), 0)
        
    def test_del(self):
        """Validates the __delitem__ behavior"""
        lst = Slist.empty(self.IntConversion)
        for i in range(10): lst.push(i)
        
        del lst[5]
        self.assertFalse(4 in lst)
        
        # FIXME: This is a bug in 'Slist.c' at lines 565+, 
        #        which occurs because the field size of the Slist_ptr is never 
        #        updated. It has been reported to FBK.
        #self.assertEqual(len(lst), 9)
    
    def test_extend(self):
        """Validates the extend behavior"""
        a = Slist.empty(self.IntConversion)
        b = Slist.empty(self.IntConversion)
        
        for i in range(5): a.push(i)
        for i in range(5): b.push(9-i)
        
        # initially a and b are disjoint
        self.assertEqual(len(a), 5)
        for i in range(5): 
            self.assertTrue(i in a)
            self.assertFalse(9-i in a)
        
        a.extend(b)
        # after extension there should be 5 more items 
        self.assertEqual(len(a), 10)
        for i in range(5): 
            self.assertTrue(9-i in a)
            
        # and they should be appended in the right order
        self.assertEqual(a[0], 9)
        self.assertEqual(a[1], 8)
        self.assertEqual(a[2], 7)
        self.assertEqual(a[3], 6)
        self.assertEqual(a[4], 5)
        self.assertEqual(a[5], 4)
        self.assertEqual(a[6], 3)
        self.assertEqual(a[7], 2)
        self.assertEqual(a[8], 1)
        self.assertEqual(a[9], 0)
        
        # but it should leave b untouched
        self.assertEqual(len(b), 5)
        for i in range(5): 
            self.assertFalse(i in b)
            self.assertTrue(9-i in b)
            
    def test_clear(self):
        """Validates the behavior of clear"""
        lst = Slist.empty(self.IntConversion)
        
        # it doesn't harm to clear an empty list
        lst.clear()
        self.assertTrue(lst.is_empty())
        self.assertTrue(lst.is_empty())
        
        # when a non empty list is cleared, it is made empty again
        for i in range(5): lst.push(i)
        self.assertEquals(len(lst), 5)
        lst.clear()
        self.assertEquals(len(lst), 0)
        self.assertTrue(lst.is_empty())
        
    def test_conversion_to_builtin_list(self):
        """Validates the behavior of __list__"""
        lst = Slist.empty(self.IntConversion)
        for i in range(5): lst.push(i)
        
        self.assertListEqual(list(lst), [4, 3, 2, 1, 0])
        
    def test_conversion_from_builtin_list(self):
        """Tests the conversion from a builtin list to an Slist"""
        lst = Slist.from_list([4, 3, 2, 1, 0], self.IntConversion)
        
        self.assertEqual(len(lst), 5)
        for i in range(5):
            self.assertEqual(4-i, lst.pop())
    
        