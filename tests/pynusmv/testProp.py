import unittest
import sys

from pynusmv import glob
from pynusmv.prop import propStatuses
from pynusmv.init import init_nusmv, deinit_nusmv

class TestPropDb(unittest.TestCase):
    
    def setUp(self):
        init_nusmv()
        
    def tearDown(self):
        deinit_nusmv()
    
    def load_admin_model(self):
        glob.load("tests/pynusmv/models/admin.smv")
        glob.compute_model()
        
            
    def test_prop(self):
        self.load_admin_model()
        propDb = glob.prop_database()
        fsm = propDb.master.bddFsm
        
        prop1 = propDb[0]
        self.assertEqual(prop1.status, propStatuses["Unchecked"])
        self.assertEqual(prop1.name, "")
        