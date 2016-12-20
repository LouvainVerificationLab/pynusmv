"""
This module validates the behavior of the 'pynusmv.be.encoder' module
"""
import unittest

from tests import utils as tests 

from pynusmv.init       import init_nusmv, deinit_nusmv
from pynusmv.glob       import load_from_file 
from pynusmv.bmc.glob   import go_bmc, bmc_exit
from pynusmv.be.encoder import BeEnc, BeVarType
from pynusmv.node       import Node
from pynusmv.parser     import parse_simple_expression

class TestBeEnc(unittest.TestCase):
    
    def node_from_expr(self, expr):
        return Node.from_ptr(parse_simple_expression(expr))
    
    def setUp(self):
        init_nusmv()
        load_from_file(tests.current_directory(__file__)+"/models/flipflops_vif.smv")
        go_bmc()
        self._TESTED = BeEnc.global_singleton_instance()

    def tearDown(self):
        bmc_exit()
        deinit_nusmv()
        
    def test_symb_table(self):
        self.assertIsNotNone(self._TESTED.symbol_table)
        self.assertEqual(
            ('model', 'model_bool', 'determ', 'determ_bool'),
            self._TESTED.symbol_table.layer_names)
        
    def test_manager(self):
        self.assertIsNotNone(self._TESTED.manager)
        
    def test_max_time(self):
        self.assertEqual(self._TESTED.max_time, -1)
        
        # shift v to time 3
        self._TESTED.by_name['v'].at_time[3] 
        
        # hence the max allocated time is 3
        self.assertEqual(self._TESTED.max_time, 3)
        
    def test_num_of_vars(self):
        self.assertEqual(self._TESTED.num_of_vars, 3)
    
    def test_num_of_state_vars(self):
        self.assertEqual(self._TESTED.num_of_state_vars, 1)
        
    def test_num_of_input_vars(self):
        self.assertEqual(self._TESTED.num_of_input_vars, 1)
        
    def test_num_of_frozen_vars(self):
        self.assertEqual(self._TESTED.num_of_frozen_vars, 1)
        
    def test_iterator_not_random(self):
        _all= [ v for v in self._TESTED.iterator(BeVarType.ALL) ]
        self.assertEqual(4, len(_all), "4 vars because of next state")
        
        curr= [ v for v in self._TESTED.iterator(BeVarType.CURR) ]
        self.assertEqual(1, len(curr),"Other are not bound to a time")
        
        nxt = [ v for v in self._TESTED.iterator(BeVarType.NEXT) ]
        self.assertEqual(1, len(nxt),"Other are not bound to a time")
        
        state=[ v for v in self._TESTED.iterator(BeVarType.CURR|BeVarType.NEXT)]
        self.assertEqual(2, len(state),"Other are not bound to a time")
        
        inpt= [ v for v in self._TESTED.iterator(BeVarType.INPUT) ]
        self.assertEqual(1, len(inpt))
        
        frzn= [ v for v in self._TESTED.iterator(BeVarType.FROZEN) ]
        self.assertEqual(1, len(frzn))
        
        combo=[ v for v in self._TESTED.iterator(BeVarType.FROZEN|BeVarType.INPUT) ]
        self.assertEqual(2, len(combo))
        
        combo=[ v for v in self._TESTED.iterator(BeVarType.FROZEN&BeVarType.INPUT) ]
        self.assertEqual(0, len(combo))
    
    def test_iterator_randomized(self):
        _all= [ v for v in self._TESTED.iterator(BeVarType.ALL, randomized=True, rnd_offset=5) ]
        self.assertEqual(4, len(_all), "4 vars because of next state")
        
        curr= [ v for v in self._TESTED.iterator(BeVarType.CURR, randomized=True, rnd_offset=5) ]
        self.assertEqual(1, len(curr),"Other are not bound to a time")
        
        nxt = [ v for v in self._TESTED.iterator(BeVarType.NEXT, randomized=True, rnd_offset=5) ]
        self.assertEqual(1, len(nxt),"Other are not bound to a time")
        
        state=[ v for v in self._TESTED.iterator(BeVarType.CURR|BeVarType.NEXT, randomized=True, rnd_offset=5) ]
        self.assertEqual(2, len(state),"Other are not bound to a time")
        
        inpt= [ v for v in self._TESTED.iterator(BeVarType.INPUT, randomized=True, rnd_offset=5) ]
        self.assertEqual(1, len(inpt))
        
        frzn= [ v for v in self._TESTED.iterator(BeVarType.FROZEN, randomized=True, rnd_offset=5) ]
        self.assertEqual(1, len(frzn))
        
        combo=[ v for v in self._TESTED.iterator(BeVarType.FROZEN|BeVarType.INPUT, randomized=True, rnd_offset=5) ]
        self.assertEqual(2, len(combo))
        
        combo=[ v for v in self._TESTED.iterator(BeVarType.FROZEN&BeVarType.INPUT, randomized=True, rnd_offset=5) ]
        self.assertEqual(0, len(combo)) 

    def test_iterator_magic_method(self):
        _all= [ v for v in self._TESTED ]
        self.assertEqual(4, len(_all), "4 vars because of next state")

    def test_untimed_var(self):
        _vars = self._TESTED.untimed_variables
        self.assertEqual(len(_vars), 4)
        
    def test_curr_var(self):
        _vars = self._TESTED.curr_variables
        self.assertEqual(len(_vars), 1)
     
    def test_frozen_var(self):
        _vars = self._TESTED.frozen_variables
        self.assertEqual(len(_vars), 1)
         
    def test_input_var(self):
        _vars = self._TESTED.input_variables
        self.assertEqual(len(_vars), 1)
         
    def test_next_var(self):
        _vars = self._TESTED.next_variables
        self.assertEqual(len(_vars), 1)
     
    def test_at_index(self):
        # index 2 is the untimed index of 'v'
        v= self._TESTED.at_index[2]
        self.assertEqual('v', str(v.name))
        self.assertEqual(2, v.index)
        
        with self.assertRaises(ValueError):
            self._TESTED.at_index[-1]
    
    def test_by_name(self):
        v= self._TESTED.by_name['v']
        self.assertEqual('v', str(v.name))
        self.assertEqual(2, v.index)
        
        with self.assertRaises(KeyError):
            self._TESTED.by_name["doesnt_exist"]
    
    def test_by_expr(self):
        v = self._TESTED.by_name['v']
        self.assertEqual(v, self._TESTED.by_expr[v.boolean_expression])    
    
    def test_shift_curr_to_next(self):
        v   = self._TESTED.by_name['v']
        nxt = self._TESTED.shift_curr_to_next(v.boolean_expression)
        self.assertEqual('BeVar(next(v) at time -1)', str(self._TESTED.by_expr[nxt]))
    
    def test_shift_to_time(self):
        v   = self._TESTED.by_name['v']
        sht = self._TESTED.shift_to_time(v.boolean_expression, 3)
        self.assertEqual('BeVar(v at time 3)', str(self._TESTED.by_expr[sht]))
        
        n   = self._TESTED.by_name['next(v)']
        sht = self._TESTED.shift_to_time(n.boolean_expression, 3)
        self.assertEqual('BeVar(v at time 4)', str(self._TESTED.by_expr[sht]))
    
    def test_shift_to_times(self):
        v   = self._TESTED.by_name['v'].boolean_expression
        f   = self._TESTED.by_name['f'].boolean_expression
        i   = self._TESTED.by_name['i'].boolean_expression
        n   = self._TESTED.by_name['next(v)'].boolean_expression
        
        # verify it works ok for current state vars
        e = self._TESTED.shift_to_times(v, 3, 0, 0, 0)
        self.assertEqual("BeVar(v at time 3)", str(self._TESTED.by_expr[e]))
        e = self._TESTED.shift_to_times(v, 0, 3, 0, 0)
        self.assertEqual("BeVar(v at time 0)", str(self._TESTED.by_expr[e]))
        e = self._TESTED.shift_to_times(v, 0, 0, 3, 0)
        self.assertEqual("BeVar(v at time 0)", str(self._TESTED.by_expr[e]))
        e = self._TESTED.shift_to_times(v, 0, 0, 0, 3)
        self.assertEqual("BeVar(v at time 0)", str(self._TESTED.by_expr[e]))
        
        # for frozen vars. Recall, a frozen var is ALWAYS untimed
        e = self._TESTED.shift_to_times(f, 3, 0, 0, 0)
        self.assertEqual("BeVar(f at time -1)", str(self._TESTED.by_expr[e]))
        e = self._TESTED.shift_to_times(f, 0, 3, 0, 0)
        self.assertEqual("BeVar(f at time -1)", str(self._TESTED.by_expr[e]))
        e = self._TESTED.shift_to_times(f, 0, 0, 3, 0)
        self.assertEqual("BeVar(f at time -1)", str(self._TESTED.by_expr[e]))
        e = self._TESTED.shift_to_times(f, 0, 0, 0, 3)
        self.assertEqual("BeVar(f at time -1)", str(self._TESTED.by_expr[e]))
        
        # for input vars
        e = self._TESTED.shift_to_times(i, 3, 0, 0, 0)
        self.assertEqual("BeVar(i at time 0)", str(self._TESTED.by_expr[e]))
        e = self._TESTED.shift_to_times(i, 0, 3, 0, 0)
        self.assertEqual("BeVar(i at time 0)", str(self._TESTED.by_expr[e]))
        e = self._TESTED.shift_to_times(i, 0, 0, 3, 0)
        self.assertEqual("BeVar(i at time 3)", str(self._TESTED.by_expr[e]))
        e = self._TESTED.shift_to_times(i, 0, 0, 0, 3)
        self.assertEqual("BeVar(i at time 0)", str(self._TESTED.by_expr[e]))
        
        # for next state vars
        e = self._TESTED.shift_to_times(n, 3, 0, 0, 0)
        self.assertEqual("BeVar(v at time 0)", str(self._TESTED.by_expr[e]))
        e = self._TESTED.shift_to_times(n, 0, 3, 0, 0)
        self.assertEqual("BeVar(v at time 0)", str(self._TESTED.by_expr[e]))
        e = self._TESTED.shift_to_times(n, 0, 0, 3, 0)
        self.assertEqual("BeVar(v at time 0)", str(self._TESTED.by_expr[e]))
        #######################################################################
        # This is imho not correct, but that is a problem in the C code, not
        # the python wrapper. I think it would be more correct if the following
        # two expressions were equivalent:
        #     e = self._TESTED.shift_to_times(n, 0, 0, 0, 3)
        #     e = self._TESTED.by_name['next(v)'].at_time[3].boolean_expression
        #
        # However, it turns out that the first one (shift_to_times) yields a 
        # variable whic is at index 11 (thus v at time 3) instead of 13
        # (v at time 4) which would be more correct.
        #
        # Therefore, my expectations for this test would be the following:
        # self.assertEqual("BeVar(v at time 4)", str(self._TESTED.by_expr[e]))
        # but this is not the way it (currently works).
        #
        # Note, my expected behavior would be consistent with that of 
        # shift_to_time which is also implemented directly in C (see previous 
        # test)
        #######################################################################
        e = self._TESTED.shift_to_times(n, 0, 0, 0, 3)
        self.assertEqual("BeVar(v at time 3)", str(self._TESTED.by_expr[e]))
    
    def test_str(self):
        # to make sure there is at least one time block
        self._TESTED.by_name['v'].at_time[0]
        string_repr  = ""
        string_repr += "+--------------+----------------+---------------+\n"
        string_repr += "| Time steps from 0 to      0                   |\n"
        string_repr += "+--------------+----------------+---------------+\n"
        string_repr += "| # State Vars |  # Frozen Vars |  # Input Vars |\n"
        string_repr += "+--------------+----------------+---------------+\n"
        string_repr += "|            1 |              1 |             1 |\n"
        string_repr += "+--------------+----------------+---------------+\n"
        string_repr += "@@@@@@@@@@@@@@@@@@@ Time   0 @@@@@@@@@@@@@@@@@@@@\n"
        string_repr += "+----------+-----------+-------+----------------+\n"
        string_repr += "| Be index | Cnf index |  Time | Model variable |\n"
        string_repr += "+----------+-----------+-------+----------------+\n"
        string_repr += "|        5 |         0 |     0 | v              |\n"
        string_repr += "|        4 |         0 |    -1 | f              |\n"
        string_repr += "|        6 |         0 |     0 | i              |\n"
        string_repr += "|        7 |         0 |     1 | next(v)        |\n"
        string_repr += "+----------+-----------+-------+----------------+\n"
        self.assertEquals(string_repr, str(self._TESTED))
        
    def test__bool_enc(self):
        # the point of this test is only to verify it doesn't crash
        self.assertIsNotNone(self._TESTED._bool_enc)
    