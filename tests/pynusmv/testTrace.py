import unittest
from tests                 import utils as tests 
from pynusmv.init          import init_nusmv, deinit_nusmv
from pynusmv.glob          import load,                \
                                  master_bool_sexp_fsm                    
from pynusmv.parser        import parse_ltl_spec,      \
                                  parse_simple_expression
from pynusmv.node          import Node 
from pynusmv.collections   import NodeList 
from pynusmv.bmc.glob      import BmcSupport, master_be_fsm
from pynusmv.bmc.utils     import generate_counter_example
from pynusmv.bmc.ltlspec   import generate_ltl_problem 
from pynusmv.sat           import SatSolverFactory, Polarity
from pynusmv.trace         import Trace, TraceType , TraceStep


class TestTrace(unittest.TestCase):
    
    def model(self):
        return tests.current_directory(__file__)+"/models/dummy_input_frozen.smv"
    
    def setUp(self):
        init_nusmv()
        load(self.model())
        
    def tearDown(self):
        deinit_nusmv()
        
    # NOTE: No specific test is foreseen to validate the (python) properties of
    #       a Trace object instead, the properties are verified when testing
    #       the other behaviors that mutate the trace state.  

    def test_create(self):
        # This function may not provoke any segfault (even though) freeit is
        # manually set to True when creating a trace.
        # besides that, the trace must be thawed, empty and have length 0
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
            
            self.assertEquals(-1, trace.id)
            self.assertFalse (trace.is_registered)
            self.assertEquals("Dummy example", trace.description)
            self.assertEquals(TraceType.COUNTER_EXAMPLE, trace.type)
            self.assertEquals(0, trace.length)
            self.assertTrue  (trace.is_empty)
            self.assertTrue  (trace.is_volatile)
            self.assertFalse (trace.is_frozen)
            self.assertTrue  (trace.is_thawed)
            self.assertEquals(list(trace.symbols), list(sexp_fsm.symbols_list))
            
    def test_concat(self):
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            be_fsm   = master_be_fsm()
            
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
            
            spec    = Node.from_ptr(parse_ltl_spec("F (w <-> v)"))
            bound   = 2
            problem = generate_ltl_problem(be_fsm, spec, bound=bound)#.inline(True)
            cnf     = problem.to_cnf()
            solver  = SatSolverFactory.create()
            solver += cnf
            solver.polarity(cnf, Polarity.POSITIVE)
            solver.solve()
            
            other= generate_counter_example(be_fsm, problem, solver, bound)
            
            trace.concat(other)
            
            self.assertEquals(-1, trace.id)
            self.assertFalse (trace.is_registered)
            self.assertEquals("Dummy example", trace.description)
            self.assertEquals(TraceType.COUNTER_EXAMPLE, trace.type)
            self.assertTrue  (trace.is_volatile)
            self.assertEquals(2, trace.length)
            self.assertEquals(2, len(trace))
            self.assertFalse (trace.is_empty)
            self.assertFalse (trace.is_frozen)
            self.assertTrue  (trace.is_thawed)
            
    def test_register(self):
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
            trace.register(42)
            
            self.assertEquals(42, trace.id)
            self.assertTrue (trace.is_registered)
            
    def test_unregister(self):
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
            
            trace.register(42)
            self.assertEquals(42, trace.id)
            self.assertTrue (trace.is_registered)
            
            trace.unregister()
            self.assertEquals(-1, trace.id)
            self.assertFalse (trace.is_registered)
            
    def test_freeze(self):
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
            
            trace.freeze()
            self.assertTrue (trace.is_frozen)
            self.assertFalse(trace.is_thawed)
            
            # it may be called two times in a row
            trace.freeze()
            self.assertTrue (trace.is_frozen)
            self.assertFalse(trace.is_thawed)
    
    def test_thaw(self):
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
            
            trace.freeze()
            self.assertTrue (trace.is_frozen)
            self.assertFalse(trace.is_thawed)
            
            trace.thaw()
            self.assertFalse(trace.is_frozen)
            self.assertTrue (trace.is_thawed)
            
            # it may be called two times in a row
            trace.thaw()
            self.assertFalse(trace.is_frozen)
            self.assertTrue (trace.is_thawed)
            
    def test_append_step(self):
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
            
            self.assertEquals(0, len(trace))
            step = trace.append_step()
            self.assertIsNotNone(step)
            self.assertEquals(TraceStep, type(step))
            self.assertEquals(1, len(trace))
    
    def test_state_vars(self):
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
            
            self.assertEquals("NodeList[v, w]", str(trace.state_vars))
            
    def test_state_frozen_vars(self):
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
            
            self.assertEquals("NodeList[v, w, f]", str(trace.state_frozen_vars))
            
    def test_input_var(self):
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
            
            self.assertEquals("NodeList[i]", str(trace.input_vars))
            
    def test_language_contains(self):
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            be_fsm   = master_be_fsm()
            
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
            
            v = be_fsm.encoding.by_name['v']
            w = be_fsm.encoding.by_name['w']
            f = be_fsm.encoding.by_name['f']
            i = be_fsm.encoding.by_name['i']
            
            self.assertTrue(v.name in trace)
            self.assertTrue(w.name in trace)
            self.assertTrue(f.name in trace)
            self.assertTrue(i.name in trace)
            
            x = parse_simple_expression("x")
            self.assertFalse(Node.from_ptr(x) in trace)
    
    def test_is_complete(self):
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            be_fsm   = master_be_fsm()
            
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
            
            # vacuously true
            self.assertTrue(trace.is_complete(NodeList.from_list([])))
            

            v = be_fsm.encoding.by_name['v'].name
            self.assertFalse(trace.is_complete(NodeList.from_list([v])))
            
            step = trace.steps[1]
            yes  = Node.from_ptr(parse_simple_expression("TRUE"))
            step+= (v, yes)
            
            self.assertTrue (trace.is_complete(NodeList.from_list([v])))             

    def test_iter(self):
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
            
            self.assertEquals(list(trace.__iter__()), [trace.steps[1]])
            step2 = trace.append_step()
            self.assertEquals(list(trace.__iter__()), [trace.steps[1], step2])
            
    def test_steps(self):
        with BmcSupport():
            sexp_fsm = master_bool_sexp_fsm()
            
            trace    = Trace.create("Dummy example", 
                         TraceType.COUNTER_EXAMPLE, 
                         sexp_fsm.symbol_table,
                         sexp_fsm.symbols_list,
                         is_volatile=True)
            
            # must raise an exception when the indice is not valid
            with self.assertRaises(KeyError):
                trace.steps[-1]
            with self.assertRaises(KeyError):
                trace.steps[0]
            with self.assertRaises(KeyError):
                trace.steps[2]
            
            self.assertIsNotNone(trace.steps[1])
            
            # once a step is appended, we can access one offset further
            step2 = trace.append_step()
            self.assertEquals(step2, trace.steps[2])