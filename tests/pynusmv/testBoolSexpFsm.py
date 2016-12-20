"""
This module validates the behavior of the BoolSexpFsm class (and by extension, 
that of the SexpFsm class).
"""
import unittest
from tests            import utils as tests 
from pynusmv          import glob 
from pynusmv.init     import init_nusmv, deinit_nusmv
from pynusmv.bmc      import glob as bmcGlob 
from pynusmv.node     import FlatHierarchy
 
class TestBoolSexpFsm(unittest.TestCase):
    
    def setUp(self):
        init_nusmv()
        glob.load_from_file(tests.current_directory(__file__)+"/models/dummy_define_justice.smv")
        bmcGlob.go_bmc()
        self.fsm = glob.master_bool_sexp_fsm()

    def tearDown(self):
        bmcGlob.bmc_exit()
        deinit_nusmv()
        
    def test_symbol_table(self):
        self.assertEqual(self.fsm.symbol_table, glob.symb_table()) 
    
    def test_is_boolean(self):
        self.assertTrue(self.fsm.is_boolean)
    
    def test_hierarchy(self):
        self.assertIsNotNone(self.fsm.hierarchy)
        self.assertIsInstance(self.fsm.hierarchy, FlatHierarchy)
    
    def test_init(self):
        self.assertEqual("!v", str(self.fsm.init))
    
    def test_invariants(self):
        self.assertEqual("!v", str(self.fsm.invariants))
    
    def test_trans(self):
        self.assertEqual("(v <-> (x | !next(v)))", str(self.fsm.trans))
    
    #def test_input(self):
    # I don't get it : this always returns None
    #    print(self.fsm.input)
    
    def test_justice(self):
        cst = [str(x) for x in self.fsm.justice]
        self.assertEqual(cst, ["v, TRUE", "TRUE"])
    
    def test_compassion(self):
        cst = [str(x) for x in self.fsm.compassion]
        self.assertEqual(cst, [])
    
    def test_variable_list(self):
        variables = set([str(x) for x in self.fsm.variables_list])
        self.assertEqual(variables, {'v', 'w', 'x'})
    
    def test_symbols_list(self):
        # returns the variables as well as the defines
        symbols = set([str(x) for x in self.fsm.symbols_list])
        self.assertEqual(symbols, {'v', 'w', 'x', 'maybe'})
    
    def is_syntactically_universal(self):
        # would be true iff the model had no INIT, INVAR, TRANS, INPUT, 
        # JUSTICE, COMPASSION.  
        self.assertFalse(self.fsm.is_syntactically_universal)