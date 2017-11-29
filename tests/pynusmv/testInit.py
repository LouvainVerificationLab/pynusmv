import unittest

from pynusmv.init import (init_nusmv, deinit_nusmv, reset_nusmv, is_nusmv_init)
from pynusmv.exception import NuSMVInitError
from pynusmv.fsm import BddFsm
from pynusmv import glob

class TestInit(unittest.TestCase):
    
    def test_init(self):
        init_nusmv()
        # Should not produce error
        fsm = BddFsm.from_filename("tests/pynusmv/models/admin.smv")
        reset_nusmv()
        # Should not produce error
        fsm = BddFsm.from_filename("tests/pynusmv/models/admin.smv")
        deinit_nusmv()
        
    
    def test_two_init(self):
        with self.assertRaises(NuSMVInitError):
            init_nusmv()
            init_nusmv()
        deinit_nusmv()
    
    
    def test_two_deinit(self):
        init_nusmv()
        deinit_nusmv()
        with self.assertRaises(NuSMVInitError):
            deinit_nusmv()
    
    def test_reset(self):
        init_nusmv()
        reset_nusmv()
        self.assertTrue(is_nusmv_init())
        deinit_nusmv()
    
    def test_init_deinit_stats(self):
        init_nusmv()
        glob.load_from_file("tests/pynusmv/models/counters.smv")
        glob.compute_model()
        deinit_nusmv(ddinfo=True)
        self.assertFalse(is_nusmv_init())
    
    def test_init_deinit_no_stats(self):
        init_nusmv()
        deinit_nusmv(ddinfo=True)
        self.assertFalse(is_nusmv_init())
    
    def test_context(self):
        with init_nusmv():
            self.assertTrue(is_nusmv_init())