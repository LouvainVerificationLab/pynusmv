import unittest

from pynusmv.utils import indexed

class TestIndexed(unittest.TestCase):
    
    def test_property_default_getter_only(self):
        @indexed.property('liste')
        class Cls:
            def __init__(self):
                self._lst = [4,5,6]
                
            def get_liste(self, idx):
                return self._lst[idx]
        
        c = Cls()
        self.assertEqual(5, c.liste[1])
    
    def test_property_default_setter_only(self):
        @indexed.property('liste')
        class Cls:
            def __init__(self):
                self._lst = [4,5,6]
                
            def set_liste(self, idx, val):
                self._lst[idx] = val
        
        c = Cls()
        c.liste[1] = 42
        self.assertEqual([4,42,6], c._lst)
        
    def test_property_default_deleter_only(self):
        @indexed.property('liste')
        class Cls:
            def __init__(self):
                self._lst = [4,5,6]
                
            def del_liste(self, idx):
                del self._lst[idx]
        
        c = Cls()
        del c.liste[1]
        self.assertEqual([4,6], c._lst)
        
    def test_property_default_full_fledged(self):
        @indexed.property('liste')
        class Cls:
            def __init__(self):
                self._lst = [4,5,6]
            
            def get_liste(self, idx):
                return self._lst[idx]
            
            def set_liste(self, idx, val):
                self._lst[idx] = val
                
            def del_liste(self, idx):
                del self._lst[idx]
        
        c = Cls()
        self.assertEqual(c.liste[1], 5)
        c.liste[1] = 42
        self.assertEqual([4,42, 6], c._lst)
        del c.liste[1]
        self.assertEqual([4,6], c._lst)
    
    def test_property_default_doc(self):
        @indexed.property('liste')
        class Cls:
            def __init__(self):
                self._lst = [4,5,6]
            
        c = Cls()
        self.assertEqual(c.liste.__doc__, "Virtual indexed property")
    
    def test_property_custom_doc(self):
        @indexed.property('liste', doc="This is a fake indexed prop")
        class Cls:
            def __init__(self):
                self._lst = [4,5,6]
            
        c = Cls()
        self.assertEqual(c.liste.__doc__, "This is a fake indexed prop")
    
    def test_property_custom_getter_only(self):
        @indexed.property('liste', fget='glst')
        class Cls:
            def __init__(self):
                self._lst = [4,5,6]
                
            def glst(self, idx):
                return self._lst[idx]
        
        c = Cls()
        self.assertEqual(5, c.liste[1])
    
    def test_property_custom_setter_only(self):
        @indexed.property('liste', fset='slst')
        class Cls:
            def __init__(self):
                self._lst = [4,5,6]
                
            def slst(self, idx, val):
                self._lst[idx] = val
        
        c = Cls()
        c.liste[1] = 42
        self.assertEqual([4,42,6], c._lst)
        
    def test_property_custom_deleter_only(self):
        @indexed.property('liste',fdel='dlst')
        class Cls:
            def __init__(self):
                self._lst = [4,5,6]
                
            def dlst(self, idx):
                del self._lst[idx]
        
        c = Cls()
        del c.liste[1]
        self.assertEqual([4,6], c._lst)
        
    def test_property_custom_full_fledged(self):
        @indexed.property('liste', fget='glst', fset='slst', fdel='dlst')
        class Cls:
            def __init__(self):
                self._lst = [4,5,6]
            
            def glst(self, idx):
                return self._lst[idx]
            
            def slst(self, idx, val):
                self._lst[idx] = val
                
            def dlst(self, idx):
                del self._lst[idx]
        
        c = Cls()
        self.assertEqual(c.liste[1], 5)
        c.liste[1] = 42
        self.assertEqual([4,42, 6], c._lst)
        del c.liste[1]
        self.assertEqual([4,6], c._lst)

    def test_getter(self):
        class Cls:
            def __init__(self):
                self._lst = [4,5,6]
                
            @indexed.getter
            def glst(self, idx):
                return self._lst[idx]
        
        c = Cls()
        self.assertEqual(5, c.glst[1])
        
    def test_setter(self):
        class Cls:
            def __init__(self):
                self._lst = [4,5,6]
                
            @indexed.setter
            def slst(self, idx, v):
                self._lst[idx] = v
        
        c = Cls()
        c.slst[1] = 42
        self.assertEqual([4, 42, 6], c._lst)
        
    def test_deleter(self):
        class Cls:
            def __init__(self):
                self._lst = [4,5,6]
                
            @indexed.deleter
            def dlst(self, idx):
                del self._lst[idx]
        
        c = Cls()
        del c.dlst[1]
        self.assertEqual([4, 6], c._lst)
        
    def test_annotated_property(self):
        class Cls:
            def __init__(self):
                self._lst = [4,5,6]
                self.liste= indexed(self, fget=self.glst, fset=self.slst,fdel=self.dlst)
                
            @indexed.setter
            def slst(self, idx, v):
                self._lst[idx] = v
                
            @indexed.getter
            def glst(self, idx):
                return self._lst[idx]
            
            @indexed.deleter
            def dlst(self, idx):
                del self._lst[idx]
        
        c = Cls()
        c.liste[1] = 42
        self.assertEqual([4, 42, 6], c._lst)
        self.assertEqual(42, c.liste[1])
        del c.liste[1]
        self.assertEqual([4, 6], c._lst)
        
    def test_nonannotated_property(self):
        # The difference with the previous test is that: slst and glst are not
        # annotated with indexed.getter an indexed.setter. Hence, the __call__
        # method of the indexed object is going to be used.
        class Cls:
            def __init__(self):
                self._lst = [4,5,6]
                self.liste= indexed(self, fget=self.glst, fset=self.slst,fdel=self.dlst)
                
            def slst(self, idx, v):
                self._lst[idx] = v
                
            def glst(self, idx):
                return self._lst[idx]
            
            def dlst(self, idx):
                del self._lst[idx]
        
        c = Cls()
        c.liste[1] = 42
        self.assertEqual([4, 42, 6], c._lst)
        self.assertEqual(42, c.liste[1])
        del c.liste[1]
        self.assertEqual([4, 6], c._lst)
