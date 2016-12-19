import unittest

from tests import utils as tests

from pynusmv.init           import init_nusmv, deinit_nusmv
from pynusmv.glob           import load_from_file 
from pynusmv.bmc.glob       import go_bmc, bmc_exit
from pynusmv.be.fsm         import BeFsm
from pynusmv.be.expression  import Be
 
class TestBeFsm(unittest.TestCase):
    def model(self):
        return '''
                
                '''
    def setUp(self):
        init_nusmv()
        load_from_file(tests.current_directory(__file__)+"/models/flipflops_trans_invar_fairness.smv")
        go_bmc()
        
        self._TESTED = BeFsm.global_master_instance()

    def tearDown(self):
        bmc_exit()
        deinit_nusmv()

    # TODO : test create_from_sexp

    def test_encoding(self):
        """
        The point of this test is to verify the absence of memory mgt errors
        """
        self.assertIsNotNone(self._TESTED.encoding)

    def test_init(self):
        # It is not a simple expression so it's neither True or False
        self.assertFalse(self._TESTED.init.is_true())
        self.assertFalse(self._TESTED.init.is_false())
        
        # verify that init <=> !v
        enc = self._TESTED.encoding
        init = -enc.by_name['v'].boolean_expression
        self.assertEqual(init, self._TESTED.init)
        
    def test_invar(self):
        # It is not a simple expression so it's neither True or False
        self.assertFalse(self._TESTED.invariants.is_true())
        self.assertFalse(self._TESTED.invariants.is_false())
         
        # verify that invar <=> !v
        enc = self._TESTED.encoding
        invar = -enc.by_name['v'].boolean_expression
        self.assertEqual(invar, self._TESTED.invariants)
    
    def test_trans(self):
        # It is not a simple expression so it's neither True or False
        self.assertFalse(self._TESTED.trans.is_true())
        self.assertFalse(self._TESTED.trans.is_false())
        
        # verify that trans next(v) := ! v
        enc = self._TESTED.encoding
        v   = enc.by_name['v'].boolean_expression
        n   = enc.by_name['next(v)'].boolean_expression
        self.assertEqual(v.iff(-n), self._TESTED.trans)
        self.assertEqual(-v.iff(n), self._TESTED.trans)

    def test_fairness_list(self):
        self.assertEqual(1, len(self._TESTED.fairness_list))   
        # returned items are boolean expressions
        fairness = self._TESTED.fairness_list[0]
        # manually recoding v = True
        v        = self._TESTED.encoding.by_name['v'].boolean_expression
        manual   = Be.true(self._TESTED.encoding.manager).iff(v)
        self.assertEqual(fairness, manual)

    def test_fairness_iterator(self):
        lst = [ f for f in self._TESTED.fairness_iterator() ]
        self.assertEqual(1, len(lst))
        self.assertEqual(lst, self._TESTED.fairness_list)
        
    @tests.todo
    def test_synchronous_product(self):
        pass
    
    @tests.todo
    def test_synchronous_magic_method(self):
        pass
    
    @tests.todo
    def test_synchronous_magic_method_inplace(self):
        pass
