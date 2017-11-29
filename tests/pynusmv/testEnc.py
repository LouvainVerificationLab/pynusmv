import unittest

import io

from pynusmv.init import init_nusmv, deinit_nusmv
from pynusmv.fsm import BddFsm
from pynusmv.dd import BDD, Cube
from pynusmv.mc import eval_simple_expression as evalSexp
from pynusmv.exception import NuSMVBddPickingError, BDDDumpFormatError

class TestEnc(unittest.TestCase):
    
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
    
    
    def test_stateVars(self):
        fsm = self.counters_model()
        enc = fsm.bddEnc
        self.assertEqual(enc.stateVars, {"c1.c", "c2.c"})
    
    
    def test_inputsVars(self):
        fsm = self.counters_model()
        enc = fsm.bddEnc
        self.assertEqual(enc.inputsVars, {"run"})
    
    
    def test_definedVars(self):
        fsm = self.counters_model()
        enc = fsm.bddEnc
        self.assertEqual(enc.definedVars, {"start", "stop"})
    
        
    def test_statesMask(self):
        fsm = self.model()
        enc = fsm.bddEnc
        
        p = evalSexp(fsm, "p")
        q = evalSexp(fsm, "q")
        a = evalSexp(fsm, "a")
        
        self.assertEqual(enc.statesMask, (p | ~p) & (q | ~q))
    
        
    def test_inputsMask(self):
        fsm = self.model()
        enc = fsm.bddEnc
        
        p = evalSexp(fsm, "p")
        q = evalSexp(fsm, "q")
        a = evalSexp(fsm, "a")
        
        self.assertEqual(enc.inputsMask, a | ~a)
        
        
    def test_statesCube(self):
        fsm = self.model()
        enc = fsm.bddEnc
        
        p = evalSexp(fsm, "p")
        q = evalSexp(fsm, "q")
        a = evalSexp(fsm, "a")
        
        self.assertTrue(p & q <= enc.statesCube)
        self.assertFalse(a <= enc.statesCube)
        self.assertFalse(~a <= enc.statesCube)
    
    def test_var_cubes(self):
        fsm = self.model()
        enc = fsm.bddEnc
        
        p = evalSexp(fsm, "p")
        q = evalSexp(fsm, "q")
        a = evalSexp(fsm, "a")
        
        pq = fsm.pick_one_state(p & q)
        pnq = fsm.pick_one_state(p & ~q)
        
        pcube = enc.cube_for_state_vars({"p"})
        qcube = enc.cube_for_state_vars({"q"})
        false = BDD.false()
        
        self.assertEqual(pcube | qcube, pcube + qcube)
        self.assertTrue(pcube | qcube <= enc.statesCube)
        self.assertEqual(qcube & pcube, qcube * pcube)
        self.assertEqual(pcube - qcube, pcube)
        
        self.assertTrue(pcube & pq <= pcube)
        self.assertTrue(pcube | pq >= pcube)
        self.assertTrue(pcube - pq <= pcube)
    
        
    def test_inputsCube(self):
        fsm = self.model()
        enc = fsm.bddEnc
        
        p = evalSexp(fsm, "p")
        q = evalSexp(fsm, "q")
        a = evalSexp(fsm, "a")
        
        self.assertTrue(a <= enc.inputsCube)
        self.assertFalse(p & q <= enc.inputsCube)
        
    
    def test_inputs_vars_cube(self):
        fsm = self.model()
        enc = fsm.bddEnc
        
        p = evalSexp(fsm, "p")
        q = evalSexp(fsm, "q")
        a = evalSexp(fsm, "a")
        
        self.assertTrue(a <= enc.cube_for_inputs_vars({'a'}))
    
    
    def test_var_ordering(self):
        fsm = self.cardgame_post_fair()
        enc = fsm.bddEnc
        
        variables = {'player.action', 'player.played',
                     'dealer.action', 'dealer.played',
                     'step', 'pcard', 'dcard', 'ddcard'}
        bits = {'player.action.0', 'player.action.1',
                'player.played.0', 'player.played.1',
                'dealer.action.0', 'dealer.action.1', 'dealer.action.2',
                'dealer.played.0', 'dealer.played.1', 'dealer.played.2',
                'step.0', 'step.1',
                'pcard.0', 'pcard.1',
                'dcard.0', 'dcard.1',
                'ddcard.0', 'ddcard.1'}
        
        self.assertSetEqual(variables, set(enc.get_variables_ordering()))
        self.assertSetEqual(bits,
                            set(enc.get_variables_ordering(var_type="bits")))
    
    def test_force_var_ordering(self):
        fsm = self.model()
        
        new_order = ("a", "q", "p")
        fsm.bddEnc.force_variables_ordering(new_order)
        self.assertTupleEqual(new_order, fsm.bddEnc.get_variables_ordering())
        
        new_order = ("p", "a")
        fsm.bddEnc.force_variables_ordering(new_order)
        self.assertTupleEqual(new_order,
                              fsm.bddEnc.get_variables_ordering()
                              [:len(new_order)])
    
    def test_bdd_dump(self):
        fsm = self.cardgame_post_fair()
        
        # Dump
        with io.StringIO() as f:
            fsm.bddEnc.dump(fsm.reachable_states, f)
            content = f.getvalue()
        
        lines = content.split("\n")
        
        # Ignore variables lines
        index = 0
        while lines[index].strip():
            index += 1
        lines = lines[index+1:]
        
        # Check that every child is effectively in the dump
        for i, line in enumerate(lines):
            if line:
                # Get children IDs
                split = line.split(" ")
                if len(split) > 2:
                    _, _, left, right = split
                    self.assertTrue(int(left) < i)
                    self.assertTrue(int(right) < i)
    
    def test_bdd_dump_load(self):
        fsm = self.cardgame_post_fair()
        states = fsm.reachable_states
        
        with io.StringIO() as f:
            fsm.bddEnc.dump(states, f)
            f.seek(0)
            reconstructed = fsm.bddEnc.load(f)
            self.assertEqual(states, reconstructed)
    
    def test_bdd_load(self):
        fsm = self.cardgame_post_fair()
        with open("tests/pynusmv/bdds/"
                  "cardgame_post_fair.reachable.bdd") as f:
            reconstructed = fsm.bddEnc.load(f)
            self.assertEqual(fsm.reachable_states, reconstructed)
    
    def test_bdd_incorrect_load_unknown_var(self):
        fsm = self.model()
        with self.assertRaises(BDDDumpFormatError):
            with open("tests/pynusmv/bdds/"
                      "cardgame_post_fair.reachable.bdd") as f:
                reconstructed = fsm.bddEnc.load(f)
    
    def test_bdd_incorrect_load_var_index_error(self):
        fsm = self.model()
        with self.assertRaises(BDDDumpFormatError):
            with open("tests/pynusmv/bdds/"
                      "constraints.reachable.error.var.index.bdd") as f:
                reconstructed = fsm.bddEnc.load(f)
    
    def test_bdd_incorrect_load_left_child_error(self):
        fsm = self.model()
        with self.assertRaises(BDDDumpFormatError):
            with open("tests/pynusmv/bdds/"
                      "constraints.reachable.error.left.child.bdd") as f:
                reconstructed = fsm.bddEnc.load(f)
    
    def test_bdd_incorrect_load_right_child_error(self):
        fsm = self.model()
        with self.assertRaises(BDDDumpFormatError):
            with open("tests/pynusmv/bdds/"
                      "constraints.reachable.error.right.child.bdd") as f:
                reconstructed = fsm.bddEnc.load(f)
    
    def test_bdd_dump_load_simple_model(self):
        fsm = self.model()
        states = fsm.reachable_states
        
        with io.StringIO() as f:
            fsm.bddEnc.dump(states, f)
            f.seek(0)
            reconstructed = fsm.bddEnc.load(f)
            self.assertEqual(states, reconstructed)
    
    def test_bdd_dump_load_counters(self):
        fsm = self.counters_model()
        states = fsm.reachable_states
        
        with io.StringIO() as f:
            fsm.bddEnc.dump(states, f)
            f.seek(0)
            reconstructed = fsm.bddEnc.load(f)
            self.assertEqual(states, reconstructed)
    
    def test_bdd_dump_load_input_vars(self):
        fsm = self.model()
        
        p = evalSexp(fsm, "p")
        q = evalSexp(fsm, "q")
        a = evalSexp(fsm, "a")
        
        bdds = {a, p & a, q & ~a}
        
        for bdd in bdds:
            with io.StringIO() as f:
                fsm.bddEnc.dump(bdd, f)
                f.seek(0)
                reconstructed = fsm.bddEnc.load(f)
                self.assertEqual(bdd, reconstructed)
    
    def test_bdd_dump_load_monolithic_trans(self):
        fsm = self.model()
        trans = fsm.trans.monolithic
        
        with io.StringIO() as f:
            fsm.bddEnc.dump(trans, f)
            f.seek(0)
            reconstructed = fsm.bddEnc.load(f)
            self.assertEqual(trans, reconstructed)
        