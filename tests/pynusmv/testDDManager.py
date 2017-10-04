import unittest

from pynusmv.init import init_nusmv, deinit_nusmv
from pynusmv.fsm import BddFsm
from pynusmv.dd import BDD
from pynusmv.dd import (reorder, enable_dynamic_reordering,
                        disable_dynamic_reordering, dynamic_reordering_enabled)
from pynusmv.exception import MissingManagerError

class TestDDManager(unittest.TestCase):
    
    def setUp(self):
        init_nusmv()
        
    def tearDown(self):
        deinit_nusmv()
        
    def model(self):
        fsm = BddFsm.from_filename("tests/pynusmv/models/constraints.smv")
        self.assertIsNotNone(fsm)
        return fsm
    
    
    def cardgame_post_fair(self):
        fsm = BddFsm.from_filename("tests/pynusmv/models/"
                                   "cardgame-post-fair.smv")
        self.assertIsNotNone(fsm)
        return fsm
    
    
    def counters_model(self):
        fsm = BddFsm.from_filename("tests/pynusmv/models/counters.smv")
        self.assertIsNotNone(fsm)
        return fsm
    
    def test_size(self):
        fsm = self.counters_model()
        ddmanager = fsm.bddEnc.DDmanager
        self.assertEqual(ddmanager.size, 10)
    
    def test_reorderings(self):
        fsm = self.counters_model()
        bddEnc = fsm.bddEnc
        ddmanager = bddEnc.DDmanager
        self.assertEqual(ddmanager.reorderings, 0)
        
        reorder(ddmanager)
        self.assertEqual(ddmanager.reorderings, 1)
    
    def test_dymanic_reordering(self):
        fsm = self.counters_model()
        bddEnc = fsm.bddEnc
        ddmanager = bddEnc.DDmanager
        enable_dynamic_reordering()
        enable_dynamic_reordering(ddmanager)
        self.assertTrue(dynamic_reordering_enabled(ddmanager))
        reorder()
        disable_dynamic_reordering()
        disable_dynamic_reordering(ddmanager)
        self.assertFalse(dynamic_reordering_enabled(ddmanager))
