import unittest

from tests                import utils as tests

from pynusmv              import glob
from pynusmv.init         import init_nusmv, deinit_nusmv
from pynusmv.exception    import (NuSMVNeedVariablesEncodedError,
                                  NuSMVModelAlreadyBuiltError,
                                  NuSMVNeedBooleanModelError)
 
class TestBuildBooleanModel(unittest.TestCase):
    def model(self):
        return tests.current_directory(__file__)+"/models/flipflops_trans_invar_fairness.smv"
    
    def setUp(self):
        init_nusmv()
        glob.load_from_file(self.model())

    def tearDown(self):
        deinit_nusmv()
        
    def test_hierarchy_must_be_flattened(self):
        with self.assertRaises(NuSMVNeedVariablesEncodedError):
            glob.build_boolean_model()
    
    def test_vars_must_be_encoded(self):
        glob.flatten_hierarchy()
        with self.assertRaises(NuSMVNeedVariablesEncodedError):
            glob.build_boolean_model()
            
    def test_must_not_be_already_built(self):
        glob.flatten_hierarchy()
        glob.encode_variables()
        glob.build_boolean_model()
        with self.assertRaises(NuSMVModelAlreadyBuiltError):
            glob.build_boolean_model()

    def test_must_not_be_already_built_unless_force_flag(self):
        glob.flatten_hierarchy()
        glob.encode_variables()
        glob.build_boolean_model()
        glob.build_boolean_model(force=True)

    def test_sets_the_global_values(self):
        glob.flatten_hierarchy()
        glob.encode_variables()
        
        with self.assertRaises(NuSMVNeedBooleanModelError):
            glob.master_bool_sexp_fsm()
        
        glob.build_boolean_model()
        self.assertIsNotNone(glob.master_bool_sexp_fsm())
        
