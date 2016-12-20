'''
This module validates the behavior of the writeonly decorator used to create 
properties that do not have a getter
'''

from unittest      import TestCase
from pynusmv.utils import writeonly

       
class Dummy:
        """
        Dummy class (okay, it is not a good example) showing how to use the 
        writeonly decorator to provide a propertylike setter without the 
        burden of having a getter.
        """
        
        def __init__(self):
            """Creates a dummy object"""
            self._value = 0
            
        @writeonly
        def value(self, _val):
            """This is the decorated setter"""
            self._value = _val
    
class TestWriteOnly(TestCase):
    
    def test_decorator(self):
        dummy = Dummy()
        # this is to proove something actually happens:
        # the _value field is initialized to 0
        self.assertEqual(0, dummy._value)
        
        # here we use the property like setter
        dummy.value = 42
        # the _value field has been updated
        self.assertEqual(42, dummy._value)
        
        # manually verify that the documentation is ok
        # disabled as it requires manual intervention while running tests
        # help(dummy)
        
        # but we CANNOT use a property like getter for this prop 
        with self.assertRaises(AttributeError):
            print(dummy.value)