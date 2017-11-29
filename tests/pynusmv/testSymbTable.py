import unittest
from copy import deepcopy

from pynusmv.init import init_nusmv, deinit_nusmv
from pynusmv.fsm import BddFsm
from pynusmv.dd import BDD
from pynusmv.mc import eval_simple_expression as evalSexp
from pynusmv.exception import (NuSMVBddPickingError, NuSMVCannotFlattenError,
                               NuSMVSymbTableError)
from pynusmv import glob
from pynusmv import node
from pynusmv import model as smv

from pynusmv_lower_interface.nusmv.compile.symb_table import symb_table as nssymb_table
from pynusmv_lower_interface.nusmv.utils import utils as nsutils
from pynusmv_lower_interface.nusmv.node import node as nsnode

class TestFsm(unittest.TestCase):
    
    def setUp(self):
        init_nusmv()
        
    def tearDown(self):
        deinit_nusmv()
        
    def model(self):
        fsm = BddFsm.from_filename("tests/pynusmv/models/constraints.smv")
        self.assertIsNotNone(fsm)
        return fsm
        
    def deadlock_model(self):
        fsm = BddFsm.from_filename("tests/pynusmv/models/deadlock.smv")
        self.assertIsNotNone(fsm)
        return fsm
    
    def simple_model(self):
        class main(smv.Module):
            c = smv.Var(smv.Range(0, 3))
            INIT = [c == 0]
            TRANS = [c.next() == (c + 1)]
        fsm = BddFsm.from_modules(main)
        return fsm
    
    def test_symb_table_layer_names(self):
        fsm = BddFsm.from_filename("tests/pynusmv/models/counters.smv")
        symb_table = fsm.bddEnc.symbTable
        st_set = {symb_table}
        
        self.assertIsNotNone(symb_table)
        self.assertIsNotNone(symb_table._ptr)
        
        self.assertEqual(len(symb_table.layer_names), 2)
        self.assertIn("model", symb_table.layer_names)
        self.assertIn("model_bool", symb_table.layer_names)
    
    def test_symb_table_new_layer(self):
        fsm = BddFsm.from_filename("tests/pynusmv/models/counters.smv")
        symb_table = fsm.bddEnc.symbTable
        
        self.assertIsNotNone(symb_table)
        self.assertTrue("translation" not in symb_table.layer_names)
        
        symb_table.create_layer("translation")
        self.assertTrue("translation" in symb_table.layer_names)
        
        with self.assertRaises(NuSMVSymbTableError):
            symb_table.create_layer("translation")
    
    def test_symb_table_declare_state_variable(self):
        fsm = BddFsm.from_filename("tests/pynusmv/models/counters.smv")
        symb_table = fsm.bddEnc.symbTable
        
        self.assertIsNotNone(symb_table)
        
        var = node.Identifier.from_string("ran")
        type_ = node.Scalar(("rc1", "rc2"))
        
        self.assertTrue(symb_table.can_declare_var("model", var))
        symb_table.declare_state_var("model", var, type_)
        self.assertFalse(symb_table.can_declare_var("model", var))
        with self.assertRaises(NuSMVSymbTableError):
            symb_table.declare_state_var("model", var, type_)
        with self.assertRaises(NuSMVSymbTableError):
            symb_table.declare_var("model", var, type_,
                                   symb_table.SYMBOL_STATE_VAR)
        
        with self.assertRaises(NuSMVSymbTableError):
            symb_table.declare_var("test", var, type_,
                                   symb_table.SYMBOL_STATE_VAR)
    
    def test_symb_table_declare_inputs_variable(self):
        fsm = BddFsm.from_filename("tests/pynusmv/models/counters.smv")
        symb_table = fsm.bddEnc.symbTable
        
        self.assertIsNotNone(symb_table)
        
        var = node.Identifier.from_string("block")
        type_ = node.Boolean()
        
        self.assertTrue(symb_table.can_declare_var("model", var))
        symb_table.declare_input_var("model", var, type_)
        with self.assertRaises(NuSMVSymbTableError):
            symb_table.declare_input_var("model", var, type_)
        with self.assertRaises(NuSMVSymbTableError):
            symb_table.declare_var("model", var, type_,
                                   symb_table.SYMBOL_INPUT_VAR)
    
    def test_symb_table_declare_frozen_variable(self):
        fsm = BddFsm.from_filename("tests/pynusmv/models/counters.smv")
        symb_table = fsm.bddEnc.symbTable
        
        self.assertIsNotNone(symb_table)
        
        var = node.Identifier.from_string("block")
        type_ = node.Boolean()
        
        self.assertTrue(symb_table.can_declare_var("model", var))
        symb_table.declare_frozen_var("model", var, type_)
        with self.assertRaises(NuSMVSymbTableError):
            symb_table.declare_frozen_var("model", var, type_)
        with self.assertRaises(NuSMVSymbTableError):
            symb_table.declare_var("model", var, type_,
                                   symb_table.SYMBOL_FROZEN_VAR)
    
    def test_is_state_var(self):
        fsm = BddFsm.from_filename("tests/pynusmv/models/counters.smv")
        symb_table = fsm.bddEnc.symbTable
        
        var = node.Identifier.from_string("c1.c")
        self.assertTrue(symb_table.is_state_var(var))
        
        var = node.Identifier.from_string("run")
        self.assertFalse(symb_table.is_state_var(var))
        
        var = node.Identifier.from_string("blocked")
        with self.assertRaises(NuSMVSymbTableError):
                symb_table.is_state_var(var)
    
    def test_is_inputs_var(self):
        fsm = BddFsm.from_filename("tests/pynusmv/models/counters.smv")
        symb_table = fsm.bddEnc.symbTable
        
        var = node.Identifier.from_string("c1.c")
        self.assertFalse(symb_table.is_input_var(var))
        
        var = node.Identifier.from_string("run")
        self.assertTrue(symb_table.is_input_var(var))
        
        var = node.Identifier.from_string("blocked")
        with self.assertRaises(NuSMVSymbTableError):
                symb_table.is_input_var(var)
    
    def test_is_frozen_var(self):
        fsm = BddFsm.from_filename("tests/pynusmv/models/counters.smv")
        symb_table = fsm.bddEnc.symbTable
        
        var = node.Identifier.from_string("c1.c")
        self.assertFalse(symb_table.is_frozen_var(var))
        
        var = node.Identifier.from_string("blocked")
        with self.assertRaises(NuSMVSymbTableError):
                symb_table.is_frozen_var(var)
    
    def test_declare_types(self):
        fsm = BddFsm.from_filename("tests/pynusmv/models/counters.smv")
        symb_table = fsm.bddEnc.symbTable
        
        variables = {"v1": node.Boolean(),
                     "v2": node.UnsignedWord(node.Number(2)),
                     "v3": node.SignedWord(node.Number(3)),
                     "v4": node.Range(node.Number(0), node.Number(3)),
                     "v5": node.Scalar(("a", "b"))}
        for var, type_ in variables.items():
            var = node.Identifier.from_string(var)
            symb_table.declare_state_var("model", var, type_)
            # Should not raise any exception
        
        with self.assertRaises(NuSMVSymbTableError):
            var = node.Identifier.from_string("s")
            type_ = node.Identifier.from_string("test")
            symb_table.declare_state_var("model", var, type_)
    