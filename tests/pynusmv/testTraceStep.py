import unittest

from tests                 import utils as tests 
from pynusmv.init          import init_nusmv, deinit_nusmv
from pynusmv.glob          import load,                 \
                                  master_bool_sexp_fsm                    
from pynusmv.parser        import parse_simple_expression
from pynusmv.node          import Node 
from pynusmv.bmc.glob      import BmcSupport, master_be_fsm
from pynusmv.trace         import Trace, TraceType
from pynusmv.exception     import NuSmvIllegalTraceStateError

class TestTraceStep(unittest.TestCase):
    
    def model(self):
        return tests.current_directory(__file__)+"/models/dummy_input_frozen.smv"
    
    def setUp(self):
        init_nusmv()
        load(self.model())
        
    def tearDown(self):
        deinit_nusmv()
    
    def test_is_loopback_when_thawed(self):
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            be_fsm   = master_be_fsm()

            # empty trace
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
           
            step1 = trace.steps[1]
            self.assertFalse(step1.is_loopback)
            
            step2 = trace.append_step()
            self.assertTrue (step1.is_loopback)
            self.assertFalse(step2.is_loopback)
            
            yes = Node.from_ptr(parse_simple_expression("TRUE"))
            no  = Node.from_ptr(parse_simple_expression("FALSE"))
            v   = be_fsm.encoding.by_name['v'].name
            
            step1+= (v, yes)
            self.assertFalse(step1.is_loopback)
            self.assertFalse(step2.is_loopback)
            
            step2+= (v, no)
            self.assertFalse(step1.is_loopback)
            self.assertFalse(step2.is_loopback)
            
            step2+= (v, yes)
            self.assertTrue (step1.is_loopback)
            self.assertFalse(step2.is_loopback)
            
    def test_is_loopback_when_frozen(self):
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            be_fsm   = master_be_fsm()

            # empty trace
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
           
            step1 = trace.steps[1]
            step2 = trace.append_step()
            
            yes = Node.from_ptr(parse_simple_expression("TRUE"))
            no  = Node.from_ptr(parse_simple_expression("FALSE"))
            v   = be_fsm.encoding.by_name['v'].name
            
            step1+= (v, yes)
            step2+= (v, no)
            
            trace.freeze()
            step1.force_loopback()
            self.assertTrue (step1.is_loopback)
            self.assertFalse(step2.is_loopback)
            
            step2.force_loopback()
            self.assertTrue (step1.is_loopback)
            # last step is never a loopback
            self.assertFalse(step2.is_loopback)
            
            trace.thaw()
            self.assertFalse(step1.is_loopback)
            self.assertFalse(step2.is_loopback)

    def test_force_loopback(self):
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()

            # empty trace
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
           
            step1 = trace.steps[1]
            # because last step is never a loopback
            trace.append_step()
            
            # must fail when trace is thawed
            with self.assertRaises(NuSmvIllegalTraceStateError):
                step1.force_loopback()
                
            trace.freeze()
            self.assertFalse(step1.is_loopback)
            step1.force_loopback()
            self.assertTrue (step1.is_loopback)
            
    def test_assign_value(self):
        """tests the behavior of assign and value"""
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            be_fsm   = master_be_fsm()

            # empty trace
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
           
            step1 = trace.steps[1]
            
            yes = Node.from_ptr(parse_simple_expression("TRUE"))
            no  = Node.from_ptr(parse_simple_expression("FALSE"))
            v   = be_fsm.encoding.by_name['v'].name
            
            self.assertIsNone(step1.value[v])
            step1.assign(v, yes)
            self.assertEqual(yes, step1.value[v])
            step1.assign(v, no)
            self.assertEqual(no, step1.value[v])
            
    def test_assign_value__magicmethod__(self):
        """tests the behavior of assign and value"""
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            be_fsm   = master_be_fsm()

            # empty trace
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
           
            step1 = trace.steps[1]
            
            yes = Node.from_ptr(parse_simple_expression("TRUE"))
            no  = Node.from_ptr(parse_simple_expression("FALSE"))
            v   = be_fsm.encoding.by_name['v'].name
            
            self.assertIsNone(step1.value[v])
            step1 += (v, yes)
            self.assertEqual(yes, step1.value[v])
            step1 += (v, no)
            self.assertEqual(no, step1.value[v])
    
    def test_iter(self):
        """tests the behavior of assign and value"""
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            be_fsm   = master_be_fsm()

            # empty trace
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
           
            step1 = trace.steps[1]
            
            yes = Node.from_ptr(parse_simple_expression("TRUE"))
            no  = Node.from_ptr(parse_simple_expression("FALSE"))
            v   = be_fsm.encoding.by_name['v'].name
            
            self.assertEqual([], list(step1))
            
            step1 += v,yes
            self.assertEqual([(v,yes)], list(step1))
            
            # += really ASSIGNS a value, not append
            step1 += v,no
            self.assertEqual([(v,no)], list(step1))
