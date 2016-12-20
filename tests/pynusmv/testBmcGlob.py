import unittest
from tests              import utils as tests 
from pynusmv.init       import init_nusmv, deinit_nusmv

from pynusmv.glob       import (load, 
                                flatten_hierarchy, 
                                encode_variables,
                                build_boolean_model)

from pynusmv.bmc        import glob as bmcglob
from pynusmv.exception  import (NuSMVNeedBooleanModelError,
                                NuSMVBmcAlreadyInitializedError,
                                NuSMVNoReadModelError)
from pynusmv.be.fsm import BeFsm

class TestBmcGlob(unittest.TestCase):
    
    def setUp(self):
        init_nusmv()
        
    def tearDown(self):
        deinit_nusmv()
    
    def model(self):
        return tests.current_directory(__file__)+"/models/flipflops.smv"
    
    def test_bmc_setup(self):
        # pre conditions not satisfied
        # model must be loaded
        with self.assertRaises(NuSMVNeedBooleanModelError):
            bmcglob.bmc_setup()
        
        # vars need to be encoded
        load(self.model())
        with self.assertRaises(NuSMVNeedBooleanModelError):
            bmcglob.bmc_setup()
        
        # boolean model must be compiled out of the sexp
        flatten_hierarchy()
        with self.assertRaises(NuSMVNeedBooleanModelError):
            bmcglob.bmc_setup()

        # hierarchy must be flattened (actually, this is a requirement for the
        # boolean model too)
        encode_variables()
        with self.assertRaises(NuSMVNeedBooleanModelError):
            bmcglob.bmc_setup()
        
        # may not be called 2 times
        build_boolean_model()
        with self.assertRaises(NuSMVBmcAlreadyInitializedError):
            bmcglob.bmc_setup()
            bmcglob.bmc_setup()
            
        # even if the force flag is on (that's COI related)
        with self.assertRaises(NuSMVBmcAlreadyInitializedError):
            bmcglob.bmc_setup(force=True)
            
        bmcglob.bmc_exit()
            
    def test_build_master_be_fsm(self):
        load(self.model())
        flatten_hierarchy()
        encode_variables()
        build_boolean_model()
        bmcglob.bmc_setup()
        # may not provoke C assert failures
        bmcglob.build_master_be_fsm()
        
        bmcglob.bmc_exit()
        
    def test_master_be_fsm(self):
        load(self.model())
        flatten_hierarchy()
        encode_variables()
        build_boolean_model()
        bmcglob.bmc_setup()
        # may not provoke C assert failures
        bmcglob.build_master_be_fsm()
        self.assertEqual(bmcglob.master_be_fsm(), BeFsm.global_master_instance())
        bmcglob.bmc_exit()
        
    def test_go_bmc(self):
        # pre conditions not satisfied
        # model must be loaded
        with self.assertRaises(NuSMVNoReadModelError):
            bmcglob.go_bmc()
        
        # vars need to be encoded
        load(self.model())
        
        # it doesn't hurt to call it more than once
        bmcglob.go_bmc()
        bmcglob.go_bmc()
        
        # unless the force flag is on
        bmcglob.go_bmc(force=True)
            
        bmcglob.bmc_exit()
        
    def test_bmcSupport(self):
        # model MUST be loaded
        with self.assertRaises(NuSMVNoReadModelError):
            with bmcglob.BmcSupport():
                # may not provoke any error
                pass
            
        load(self.model())
        with bmcglob.BmcSupport():
            # may not provoke any error
            pass