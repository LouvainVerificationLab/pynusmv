import unittest
from copy import deepcopy

from pynusmv.init import init_nusmv, deinit_nusmv
from pynusmv.fsm import BddFsm, BddTrans
from pynusmv import model as smv
from pynusmv.dd import BDD
from pynusmv.mc import eval_simple_expression
from pynusmv.exception import NuSMVFlatteningError

class TestBddTrans(unittest.TestCase):
    
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
    
    def test_create_trans(self):
        fsm = self.model()
        p = eval_simple_expression(fsm, "p")
        new_trans = BddTrans.from_string(fsm.bddEnc.symbTable,
                                         "next(p) = !p")
        self.assertEqual(new_trans.post(p), ~p)
        
        with self.assertRaises(NuSMVFlatteningError):
            new_trans = BddTrans.from_string(fsm.bddEnc.symbTable,
                                             "next(p) = !p",
                                             strcontext="main")
    
    def test_pre(self):
        fsm = self.model()
        trans = fsm.trans
        
        true = BDD.true()
        false = BDD.false()
        p = eval_simple_expression(fsm, "p")
        q = eval_simple_expression(fsm, "q")
        a = eval_simple_expression(fsm, "a")
        
        self.assertEqual(trans.pre(p & q), false)
        self.assertEqual(trans.pre(p & ~q, inputs=a), p & ~q)
    
    def test_post(self):
        fsm = self.model()
        trans = fsm.trans
        
        true = BDD.true()
        false = BDD.false()
        p = eval_simple_expression(fsm, "p")
        q = eval_simple_expression(fsm, "q")
        a = eval_simple_expression(fsm, "a")
        
        self.assertEqual(trans.post(p & q), ~p & q | p & ~q)
        self.assertEqual(trans.post(p & q, inputs=a), ~p & q)
        