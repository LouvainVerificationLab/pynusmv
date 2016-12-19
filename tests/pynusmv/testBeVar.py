"""
This module validates the behavior of the :class:`BeVar` <pynusmv.be.encoder.BeVar> 
"""

import unittest
from tests                 import utils as tests
from pynusmv.init          import init_nusmv, deinit_nusmv
from pynusmv.glob          import load_from_file
from pynusmv.bmc.glob      import go_bmc, bmc_exit, master_be_fsm 
from pynusmv.be.expression import Be
from pynusmv.be.encoder    import BeWrongVarType 

class TestBeVar(unittest.TestCase):
    
    def setUp(self):
        init_nusmv()
        load_from_file(tests.current_directory(__file__)+"/models/flipflops_vif.smv")
        go_bmc()
        self.enc = master_be_fsm().encoding
        self.v   = self.enc.by_name['v']
        self.f   = self.enc.by_name['f']
        self.i   = self.enc.by_name['i']
        self.n   = self.enc.by_name['next(v)']

    def tearDown(self):
        bmc_exit()
        deinit_nusmv()
        
    def test_boolean_expression(self):
        # this internal function serves only the purpose of shortening the
        # overall code dedicated to this test (no repetition)
        def verify_var_be(var):
            be = var.boolean_expression
            self.assertIsNotNone(be)
            self.assertEqual(Be, type(be))
            
            cnf_2_idx = lambda x: self.enc.manager.cnf_literal_to_index(x)
            lst = list(map(cnf_2_idx, list(be.to_cnf().vars_list)))
            self.assertEqual([var.index], lst)
        
        # it works for untimed variables
        verify_var_be(self.v)
        verify_var_be(self.f)
        verify_var_be(self.i)
        verify_var_be(self.n)
        
        # and for timed variables too
        verify_var_be(self.v.at_time[4])
        verify_var_be(self.f.at_time[4])
        verify_var_be(self.i.at_time[4])
        verify_var_be(self.n.at_time[4])
        
    def test_cnf_literal(self):
        # this internal function serves only the purpose of shortening the
        # overall code dedicated to this test (no repetition)
        def verify_var_be(var):
            be = var.boolean_expression
            self.assertIsNotNone(be)
            self.assertEqual(Be, type(be))

            self.assertEqual(var.cnf_literal, self.enc.manager.be_index_to_cnf_literal(var.index))
        
        # it works for untimed variables
        verify_var_be(self.v)
        verify_var_be(self.f)
        verify_var_be(self.i)
        verify_var_be(self.n)
        
        # and for timed variables too
        verify_var_be(self.v.at_time[4])
        verify_var_be(self.f.at_time[4])
        verify_var_be(self.i.at_time[4])
        verify_var_be(self.n.at_time[4])
        
    def test_name(self):
        # it works for untimed variables
        self.assertEqual("v",       str(self.v.name))
        self.assertEqual("f",       str(self.f.name))
        self.assertEqual("i",       str(self.i.name))
        self.assertEqual("next(v)", str(self.n.name))
        
        # and for timed variables too
        self.assertEqual("v",       str(self.v.at_time[2].name))
        self.assertEqual("f",       str(self.f.at_time[2].name))
        self.assertEqual("i",       str(self.i.at_time[2].name))
        # because manager doesn't know here if it is v at time 3 
        # or next(v) at time 2
        self.assertEqual("v",       str(self.n.at_time[2].name))
        
    def test_time(self):
        # it works for untimed variables
        # => -1 means untimed
        self.assertEqual(-1, self.v.time)
        self.assertEqual(-1, self.f.time)
        self.assertEqual(-1, self.i.time)
        self.assertEqual(-1, self.n.time)
        
        # and for timed variables too
        self.assertEqual( 2, self.v.at_time[2].time)
        # frozen are ALWAYS untimed !
        self.assertEqual(-1, self.f.at_time[2].time)
        self.assertEqual( 2, self.i.at_time[2].time)
        # next(v) at time 2 == v at time 3
        self.assertEqual( 3, self.n.at_time[2].time)
    
    def test_untimed(self):
        # it works for untimed variables
        self.assertEqual(self.v, self.v.untimed)
        self.assertEqual(self.f, self.f.untimed)
        self.assertEqual(self.i, self.i.untimed)
        self.assertEqual(self.n, self.n.untimed)
        
        # and for timed variables too
        self.assertEqual(self.v, self.v.at_time[4].untimed)
        self.assertEqual(self.f, self.f.at_time[4].untimed)
        self.assertEqual(self.i, self.i.at_time[4].untimed)
        # that's sad but normal : the system isn't able to make a difference
        # between next(v) at time 4 or v at time 5. Thus it believes that 
        # next(v).at_time[5].untimed is v
        self.assertEqual(self.v, self.n.at_time[4].untimed)
        
    def test_at_time(self):
        self.assertEqual("BeVar(v at time 2)" ,str(self.v.at_time[2]))
        self.assertEqual("BeVar(f at time -1)",str(self.f.at_time[2]))
        self.assertEqual("BeVar(i at time 2)" ,str(self.i.at_time[2]))
        # same remark as above
        self.assertEqual("BeVar(v at time 3)" ,str(self.n.at_time[2]))
        
    def test_next(self):
        # it must work only for v
        with self.assertRaises(BeWrongVarType):
            self.f.next
        with self.assertRaises(BeWrongVarType):
            self.i.next
        with self.assertRaises(BeWrongVarType):
            self.n.next
            
        self.assertEqual(self.n, self.v.next)
        
    def test_curr(self):
        # it must work for n only (thats the only untimed next var)
        # it must work only for v
        with self.assertRaises(BeWrongVarType):
            self.f.curr
        with self.assertRaises(BeWrongVarType):
            self.i.curr
        with self.assertRaises(BeWrongVarType):
            self.v.curr
            
        self.assertEqual(self.v, self.n.curr)
        
    def test_is_valid(self):
        # it works for untimed variables
        self.assertTrue(self.v.is_valid)
        self.assertTrue(self.f.is_valid)
        self.assertTrue(self.i.is_valid)
        self.assertTrue(self.n.is_valid)
        
        # and for timed variables too
        self.assertTrue(self.v.at_time[4].is_valid)
        self.assertTrue(self.f.at_time[4].is_valid)
        self.assertTrue(self.i.at_time[4].is_valid)
        self.assertTrue(self.n.at_time[4].is_valid)
        
    def test_is_state_var(self):
        # it works for untimed variables
        self.assertTrue(self.v.is_state_var)
        self.assertFalse(self.f.is_state_var)
        self.assertFalse(self.i.is_state_var)
        self.assertTrue(self.n.is_state_var)
        
        # and for timed variables too
        self.assertTrue(self.v.at_time[4].is_state_var)
        self.assertFalse(self.f.at_time[4].is_state_var)
        self.assertFalse(self.i.at_time[4].is_state_var)
        self.assertTrue(self.n.at_time[4].is_state_var)
        
    def test_is_frozen_var(self):
        # it works for untimed variables
        self.assertFalse(self.v.is_frozen_var)
        self.assertTrue (self.f.is_frozen_var)
        self.assertFalse(self.i.is_frozen_var)
        self.assertFalse(self.n.is_frozen_var)
        
        # and for timed variables too
        self.assertFalse(self.v.at_time[4].is_frozen_var)
        self.assertTrue (self.f.at_time[4].is_frozen_var)
        self.assertFalse(self.i.at_time[4].is_frozen_var)
        self.assertFalse(self.n.at_time[4].is_frozen_var)
        
    def test_is_input_var(self):
        # it works for untimed variables
        self.assertFalse(self.v.is_input_var)
        self.assertFalse(self.f.is_input_var)
        self.assertTrue (self.i.is_input_var)
        self.assertFalse(self.n.is_input_var)
        
        # and for timed variables too
        self.assertFalse(self.v.at_time[4].is_input_var)
        self.assertFalse(self.f.at_time[4].is_input_var)
        self.assertTrue (self.i.at_time[4].is_input_var)
        self.assertFalse(self.n.at_time[4].is_input_var)
        
    def test_is_untimed(self):
        # it works for untimed variables
        self.assertTrue(self.v.is_untimed)
        self.assertTrue(self.f.is_untimed)
        self.assertTrue(self.i.is_untimed)
        self.assertTrue(self.n.is_untimed)
        
        # and for timed variables too
        self.assertFalse(self.v.at_time[4].is_untimed)
        # frozen vars are ALWAYS untimed
        self.assertTrue (self.f.at_time[4].is_untimed)
        self.assertFalse(self.i.at_time[4].is_untimed)
        self.assertFalse(self.n.at_time[4].is_untimed)
        
    def test_is_untimed_current(self):                           
        self.assertTrue (self.v.is_untimed_current)               
        self.assertFalse(self.f.is_untimed_current)               
        self.assertFalse(self.i.is_untimed_current)               
        self.assertFalse(self.n.is_untimed_current)               
                                                         
        self.assertFalse(self.v.at_time[4].is_untimed_current)   
        self.assertFalse(self.f.at_time[4].is_untimed_current)   
        self.assertFalse(self.i.at_time[4].is_untimed_current)   
        self.assertFalse(self.n.at_time[4].is_untimed_current) 
        
    def test_is_untimed_frozen(self):
        # note: this is the exact same behavior as is_frozen
        # it works for untimed variables
        self.assertFalse(self.v.is_untimed_frozen)
        self.assertTrue (self.f.is_untimed_frozen)
        self.assertFalse(self.i.is_untimed_frozen)
        self.assertFalse(self.n.is_untimed_frozen)
        
        # and for timed variables too
        self.assertFalse(self.v.at_time[4].is_untimed_frozen)
        self.assertTrue (self.f.at_time[4].is_untimed_frozen)
        self.assertFalse(self.i.at_time[4].is_untimed_frozen)
        self.assertFalse(self.n.at_time[4].is_untimed_frozen)
        
    def test_is_untimed_curr_frozen_input(self):
        # note: this is the exact same behavior as is_frozen
        # it works for untimed variables
        self.assertTrue (self.v.is_untimed_curr_frozen_input)
        self.assertTrue (self.f.is_untimed_curr_frozen_input)
        self.assertTrue (self.i.is_untimed_curr_frozen_input)
        self.assertFalse(self.n.is_untimed_curr_frozen_input)
        
        # and for timed variables too
        self.assertFalse(self.v.at_time[4].is_untimed_curr_frozen_input)
        self.assertTrue (self.f.at_time[4].is_untimed_curr_frozen_input)
        self.assertFalse(self.i.at_time[4].is_untimed_curr_frozen_input)
        self.assertFalse(self.n.at_time[4].is_untimed_curr_frozen_input)
        
    def test_is_untimed_next(self):
        # note: this is the exact same behavior as is_frozen
        # it works for untimed variables
        self.assertFalse(self.v.is_untimed_next)
        self.assertFalse(self.f.is_untimed_next)
        self.assertFalse(self.i.is_untimed_next)
        self.assertTrue (self.n.is_untimed_next)
        
        # and for timed variables too
        self.assertFalse(self.v.at_time[4].is_untimed_next)
        self.assertFalse(self.f.at_time[4].is_untimed_next)
        self.assertFalse(self.i.at_time[4].is_untimed_next)
        self.assertFalse(self.n.at_time[4].is_untimed_next)
        
    def test_repr(self):
        # because it is very useful to debug
        self.assertEqual("BeVar(v at time -1)" ,str(self.v))
        self.assertEqual("BeVar(f at time -1)" ,str(self.f))
        self.assertEqual("BeVar(i at time -1)" ,str(self.i))
        self.assertEqual("BeVar(next(v) at time -1)" ,str(self.n))
        
        self.assertEqual("BeVar(v at time 2)" ,str(self.v.at_time[2]))
        self.assertEqual("BeVar(f at time -1)",str(self.f.at_time[2]))
        self.assertEqual("BeVar(i at time 2)" ,str(self.i.at_time[2]))
        self.assertEqual("BeVar(v at time 3)" ,str(self.n.at_time[2]))
        