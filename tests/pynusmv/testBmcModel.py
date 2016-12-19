import unittest

from tests import utils as tests

from pynusmv.init          import init_nusmv, deinit_nusmv
from pynusmv.glob          import load_from_file
from pynusmv.bmc.glob      import go_bmc, bmc_exit
from pynusmv.be.expression import Be
from pynusmv.be.fsm        import BeFsm
from pynusmv.bmc.utils     import BmcModel

from pynusmv.utils         import StdioFile 
 
class TestBmcModel(unittest.TestCase):
    
    def setUp(self):
        init_nusmv()
        load_from_file(tests.current_directory(__file__)+"/models/flipflops_trans_invar_fairness.smv")
        go_bmc()
        
        self.fsm = BeFsm.global_master_instance()
        self.enc = self.fsm.encoding

    def tearDown(self):
        bmc_exit()
        deinit_nusmv()

    def test_init(self):
        # time must be >= 0
        with self.assertRaises(ValueError):
            BmcModel(self.fsm).init[-1]
        
        # at time  0
        init0 = self.fsm.encoding.shift_to_time(self.fsm.init, 0)
        self.assertEqual(init0, BmcModel(self.fsm).init[0])
        
        # at time  4
        init4 = self.fsm.encoding.shift_to_time(self.fsm.init, 4)
        self.assertEqual(init4, BmcModel(self.fsm).init[4])
        
    def test_invar(self):
        # time must be >= 0
        with self.assertRaises(ValueError):
            BmcModel(self.fsm).invar[-1]
        
        # at time  0
        invar0 = self.fsm.encoding.shift_to_time(self.fsm.invariants, 0)
        self.assertEqual(invar0, BmcModel(self.fsm).invar[0])
        
        # at time  4
        invar4 = self.fsm.encoding.shift_to_time(self.fsm.invariants, 4)
        self.assertEqual(invar4, BmcModel(self.fsm).invar[4])
    
    def test_trans(self):
        # time must be >= 0
        with self.assertRaises(ValueError):
            BmcModel(self.fsm).trans[-1]
        
        # at time  0
        trans = self.fsm.encoding.shift_to_time(self.fsm.trans, 0)
        self.assertEqual(trans, BmcModel(self.fsm).trans[0])
        
        # at time  4
        trans = self.fsm.encoding.shift_to_time(self.fsm.trans, 4)
        self.assertEqual(trans, BmcModel(self.fsm).trans[4])
    
    def test_unrolling(self):
        # comparing the clauses list is not feasible because of the formula
        # literal which is embedded in the clauses and vary from one implem
        # to the next
        # Thus, this test lets us at least get some confidence about the 
        # equivalence between the two Be's
        
        def manual_unrolling(j, bound):
            trans  = Be.true(self.enc.manager)
            for k in range(j, bound):    
                trans = trans & self.enc.shift_to_time(self.fsm.trans, k)
            return trans
       
        model      = BmcModel(self.fsm)
        manual     = manual_unrolling(4, 5)
        tested     = model.unrolling(4,5)
        # because the var ordering does not matter at all
        manual_set = set(manual.to_cnf().vars_list)
        tested_set = set(tested.to_cnf().vars_list)
        
        self.assertEqual(manual_set, tested_set)
        
    def test_unrolling_fragment(self):
        # comparing the clauses list is not feasible because of the formula
        # literal which is embedded in the clauses and vary from one implem
        # to the next
        # Thus, this test lets us at least get some confidence about the 
        # equivalence between the two Be's
        
        model      = BmcModel(self.fsm)
        # time index starts at 1
        with self.assertRaises(ValueError):
            model.unrolling_fragment[-1]
        
        self.assertEquals(model.init[0], model.unrolling_fragment[0])
        
        manual = model.invar[1] & model.trans[1] & model.invar[2]    
        tested = model.unrolling_fragment[2]
        
        # because the var ordering does not matter at all
        manual_set = set(manual.to_cnf().vars_list)
        tested_set = set(tested.to_cnf().vars_list)
        self.assertEqual(manual_set, tested_set)

    def test_path(self):
        model      = BmcModel(self.fsm)
        noinit     = model.path(3, with_init=False)
        w_init     = model.path(3)
        
        self.assertEqual(w_init, (noinit & model.init[0]))
        self.assertEqual(noinit, model.unrolling(0, 3))
        
    def test_fairness(self):
        model = BmcModel(self.fsm)
        # K, L must be consistent with one another
        with self.assertRaises(ValueError):
            model.fairness(0, 1)
             
        self.assertIsNotNone(model.fairness(3, 0))
        self.assertEqual(Be, type(model.fairness(3, 0)))
        
        # Manual verification, this should output the following formula:
        # (NOT (AND (NOT X3) (AND (NOT X4) (NOT X5))))
        self.enc.manager.dump_sexpr(model.fairness(3, 0), StdioFile.stdout())
        
    @tests.todo
    def test_invar_dual_forward(self):
        print(BmcModel(self.fsm).unrolling(4,5))