import unittest

from tests                 import utils as tests

from pynusmv.init          import init_nusmv, deinit_nusmv
from pynusmv.bmc.glob      import go_bmc, bmc_exit
from pynusmv               import glob 
from pynusmv.be.fsm        import BeFsm  
from pynusmv.be.expression import Be
from pynusmv.sat           import Polarity

class TestBe(unittest.TestCase):
      
    def setUp(self):
        init_nusmv()
        glob.load(tests.current_directory(__file__)+"/models/flipflops_explicit_relation.smv")
        go_bmc()
        self._fsm = BeFsm.global_master_instance()
        self._manager = self._fsm.encoding.manager
 
    def tearDown(self):
        bmc_exit()
        deinit_nusmv()
        
    def test_true(self):
        with self.assertRaises(Exception):
            Be.true(None)
        expr = Be.true(self._manager)
        self.assertTrue(expr.is_true())
        self.assertFalse(expr.is_false())
        self.assertTrue(expr.is_constant())
    
    def test_false(self):
        with self.assertRaises(Exception):
            Be.false(None)
        expr = Be.false(self._manager)
        self.assertFalse(expr.is_true())
        self.assertTrue(expr.is_false())
        self.assertTrue(expr.is_constant())
    
    
    # NOTE: is_true and is_false are tested many times since it is used in 
    #       assertions of other test cases
    
    def test_is_constant(self):
        # with a non constant expression
        v = self._fsm.encoding.by_name["v"].boolean_expression
        self.assertFalse(v.is_constant())
    
    def test_if_then_else(self):
        true  = Be.true(self._manager)
        false = Be.false(self._manager)

        with self.assertRaises(Exception):
            Be.if_then_else(None, true, true, false)
            
        # tautology
        expr = Be.if_then_else(self._manager, true, true, false)
        self.assertTrue(expr.is_true())
        self.assertFalse(expr.is_false())
        self.assertTrue(expr.is_constant())
        
        # antilogy
        expr = Be.if_then_else(self._manager, false, true, false)
        self.assertFalse(expr.is_true())
        self.assertTrue(expr.is_false())
        self.assertTrue(expr.is_constant())
        


    def test_not(self):
        expr = Be.true(self._manager)
        
        self.assertFalse(expr.not_().is_true())
        self.assertTrue(expr.not_().is_false()) 
        self.assertTrue(expr.not_().is_constant()) 
    
    def test_neg_(self):
        expr = Be.true(self._manager)
        
        self.assertFalse((-expr).is_true())
        self.assertTrue((-expr).is_false()) 
        self.assertTrue((-expr).is_constant()) 
    
    def test_invert_(self):
        expr = Be.true(self._manager)
        
        self.assertFalse((~expr).is_true())
        self.assertTrue((~expr).is_false()) 
        self.assertTrue((~expr).is_constant()) 
    
    def test_and(self):
        # using the function
        true  = Be.true(self._manager)
        false = Be.false(self._manager)
        
        self.assertFalse(true.and_(false).is_true())
        self.assertTrue(true.and_(false).is_false())
        self.assertTrue(true.and_(false).is_constant())
        
    def test__and_(self):
        # using the keyword
        true  = Be.true(self._manager)
        false = Be.false(self._manager)
        
        self.assertFalse((true and false).is_true())
        self.assertTrue((true and false).is_false())
        self.assertTrue((true and false).is_constant())
        
    def test__mul_(self):
        # using algebraic notation
        true  = Be.true(self._manager)
        false = Be.false(self._manager)
        
        self.assertFalse((true * false).is_true())
        self.assertTrue((true  * false).is_false())
        self.assertTrue((true  * false).is_constant())
        
        self.assertFalse((true & false).is_true())
        self.assertTrue((true  & false).is_false())
        self.assertTrue((true  & false).is_constant())
    
    def test_or(self):
        # using the function
        true  = Be.true(self._manager)
        false = Be.false(self._manager)
        
        self.assertTrue(true.or_(false).is_true())
        self.assertFalse(true.or_(false).is_false())
        self.assertTrue(true.or_(false).is_constant())
    
    def test_or_(self):
        # using the keyword
        true  = Be.true(self._manager)
        false = Be.false(self._manager)
        
        self.assertTrue((true or false).is_true())
        self.assertFalse((true or false).is_false())
        self.assertTrue((true or false).is_constant())
        
        self.assertTrue((true  | false).is_true())
        self.assertFalse((true | false).is_false())
        self.assertTrue((true  | false).is_constant())
    
    def test_add_(self):
        # using the algebraic notation
        true  = Be.true(self._manager)
        false = Be.false(self._manager)
        
        self.assertTrue((true  + false).is_true())
        self.assertFalse((true + false).is_false())
        self.assertTrue((true  + false).is_constant())
    
    def test_sub_(self):
        # and not
        true  = Be.true(self._manager)
        false = Be.false(self._manager)
        
        self.assertTrue((true  - false).is_true())
        self.assertFalse((true - false).is_false())
        self.assertTrue((true  - false).is_constant())
    
    def test_xor(self):
        # using the function
        true  = Be.true(self._manager)
        false = Be.false(self._manager)
        
        self.assertTrue(true.xor(false).is_true())
        self.assertFalse(true.xor(false).is_false())
        self.assertTrue(true.xor(false).is_constant())
        
        self.assertTrue(false.xor(true).is_true())
        self.assertFalse(false.xor(true).is_false())
        self.assertTrue(false.xor(true).is_constant())
        
        self.assertFalse(true.xor(true).is_true())
        self.assertTrue(true.xor(true).is_false())
        self.assertTrue(true.xor(true).is_constant())
        
        self.assertFalse(false.xor(false).is_true())
        self.assertTrue(false.xor(false).is_false())
        self.assertTrue(false.xor(false).is_constant())
    
    def test_xor_(self):
        # using the operator
        true  = Be.true(self._manager)
        false = Be.false(self._manager)
        
        self.assertTrue((true  ^  false).is_true())
        self.assertFalse((true ^  false).is_false())
        self.assertTrue((true  ^  false).is_constant())
        
        self.assertTrue((false ^  true).is_true())
        self.assertFalse((false^  true).is_false())
        self.assertTrue((false ^  true).is_constant())
        
        self.assertFalse((true ^  true).is_true())
        self.assertTrue((true  ^  true).is_false())
        self.assertTrue((true  ^  true).is_constant())
        
        self.assertFalse((false^  false).is_true())
        self.assertTrue((false ^  false).is_false())
        self.assertTrue((false ^  false).is_constant())
    
    def test_imply(self):
        true  = Be.true(self._manager)
        false = Be.false(self._manager)
        
        # antecedent always true
        self.assertFalse(true.imply(false).is_true())
        self.assertTrue( true.imply(false).is_false())
        self.assertTrue( true.imply(false).is_constant())
        
        # antecedent always false
        self.assertTrue( false.imply(true).is_true())
        self.assertFalse(false.imply(true).is_false())
        self.assertTrue( false.imply(true).is_constant())
        
    def test_iff(self):
        true  = Be.true(self._manager)
        false = Be.false(self._manager)
        
        
        self.assertFalse(true.iff(false).is_true())
        self.assertTrue( true.iff(false).is_false())
        self.assertTrue( true.iff(false).is_constant())
        
        self.assertFalse(false.iff(true).is_true())
        self.assertTrue( false.iff(true).is_false())
        self.assertTrue( false.iff(true).is_constant())
        
        self.assertTrue( true.iff(true).is_true())
        self.assertFalse(true.iff(true).is_false())
        self.assertTrue( true.iff(true).is_constant())
        
        self.assertTrue( false.iff(false).is_true())
        self.assertFalse(false.iff(false).is_false())
        self.assertTrue( false.iff(false).is_constant())
    
            
    ############################################################################
    # The behavior of the features tested is not verifiable without a sat solver
    # hence the following test cases only serve the purpose of validating the
    # absence of runtime (technical faults)
    ############################################################################
    
    def test_inline(self):
        true  = Be.true(self._manager)
        self.assertIsNotNone(true.inline(True))
        self.assertIsNotNone(true.inline(False))
        
        # with a non constant expression
        v = self._fsm.encoding.by_name["v"].boolean_expression
        self.assertIsNotNone(v.inline(True))
        self.assertIsNotNone(v.inline(False))
        
    def test_to_cnf(self):
        true  = Be.true(self._manager)
        self.assertIsNotNone(true.to_cnf(Polarity.NOT_SET))
        self.assertIsNotNone(true.to_cnf(Polarity.NEGATIVE))
        self.assertIsNotNone(true.to_cnf(Polarity.POSITIVE))
        
        # with a non constant expression
        v = self._fsm.encoding.by_name["v"].boolean_expression
        self.assertIsNotNone(v.to_cnf(Polarity.NOT_SET))
        self.assertIsNotNone(v.to_cnf(Polarity.NEGATIVE))
        self.assertIsNotNone(v.to_cnf(Polarity.POSITIVE))
    