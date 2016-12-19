import unittest
from tests                 import utils as tests
from pynusmv_lower_interface.nusmv.parser  import parser as _parser

from pynusmv.be.expression import Be
from pynusmv.bmc.glob      import BmcSupport, master_be_fsm
from pynusmv.bmc.ltlspec   import generate_ltl_problem 
from pynusmv.bmc           import utils as bmcutils
from pynusmv.init          import init_nusmv, deinit_nusmv
from pynusmv.glob          import load_from_string, prop_database, master_bool_sexp_fsm
from pynusmv.node          import Node 
from pynusmv.parser        import parse_ltl_spec 
from pynusmv.trace         import Trace, TraceType
from pynusmv.sat           import SatSolverFactory , Polarity, SatSolverResult
from pynusmv.wff           import Wff


class TestBmcUtils(unittest.TestCase):
    
    def setUp(self):    
        init_nusmv()
    
    def tearDown(self):
        deinit_nusmv()
        
    def test_all_loopbacks(self):
        self.assertTrue (bmcutils.is_all_loopbacks(bmcutils.all_loopbacks()))
        self.assertFalse(bmcutils.is_all_loopbacks(1000))
        self.assertFalse(bmcutils.is_all_loopbacks(bmcutils.no_loopback()))
        
    def test_no_loopback(self):
        self.assertTrue (bmcutils.is_no_loopback(bmcutils.no_loopback()))
        self.assertFalse(bmcutils.is_no_loopback(1000))
        self.assertFalse(bmcutils.is_no_loopback(bmcutils.all_loopbacks()))
        self.assertFalse(bmcutils.is_no_loopback(-1*bmcutils.all_loopbacks()))
        self.assertFalse(bmcutils.is_no_loopback(-10000))
        
    def test_loop_from_string(self):
        self.assertEqual( 4, bmcutils.loop_from_string("4"))
        self.assertEqual(-1, bmcutils.loop_from_string("-1"))
        self.assertEqual(bmcutils.all_loopbacks(), bmcutils.loop_from_string("*"))
        self.assertEqual(bmcutils.all_loopbacks(), bmcutils.loop_from_string("All"))
        self.assertEqual(bmcutils.all_loopbacks(), bmcutils.loop_from_string("All Loops"))
        self.assertEqual(bmcutils.all_loopbacks(), bmcutils.loop_from_string("all"))
        self.assertEqual(bmcutils.all_loopbacks(), bmcutils.loop_from_string("all loops"))
        
        self.assertEqual(bmcutils.no_loopback(), bmcutils.loop_from_string("x"))
        self.assertEqual(bmcutils.no_loopback(), bmcutils.loop_from_string("No"))
        self.assertEqual(bmcutils.no_loopback(), bmcutils.loop_from_string("None"))
        self.assertEqual(bmcutils.no_loopback(), bmcutils.loop_from_string("No Loop"))
        self.assertEqual(bmcutils.no_loopback(), bmcutils.loop_from_string("no"))
        self.assertEqual(bmcutils.no_loopback(), bmcutils.loop_from_string("none"))
        self.assertEqual(bmcutils.no_loopback(), bmcutils.loop_from_string("no loop"))
        
    def test_convert_relative_loop_to_absolute(self):
        self.assertEqual(4, bmcutils.convert_relative_loop_to_absolute( 4, 10))
        self.assertEqual(6, bmcutils.convert_relative_loop_to_absolute(-4, 10))
        # loop and bound must be consistent (bound >= 0)
        with self.assertRaises(ValueError):
            bmcutils.convert_relative_loop_to_absolute(5, -2)
        # loop and bound must be consistent (loop <= bound)
        with self.assertRaises(ValueError):
            bmcutils.convert_relative_loop_to_absolute(5, 2)
    
    def test_check_consistency(self):
        # when the bound is not meaningful
        with self.assertRaises(ValueError):
            bmcutils.check_consistency(-1, 2)
            
        # when the loop is greater than the bound
        with self.assertRaises(ValueError):
            bmcutils.check_consistency(1, 2)
        
        # unless it is a special value    
        bmcutils.check_consistency(4, bmcutils.all_loopbacks())
        bmcutils.check_consistency(4, bmcutils.no_loopback())
    
    def test_loop_condition_single_var(self):
        # test case 1: model with one single var
        load_from_string(
            """
            MODULE main
            VAR     v : boolean;
            ASSIGN  init(v) := TRUE; 
                    next(v) := !v;
            """)
        with BmcSupport():
            mdl  = bmcutils.BmcModel()
            enc  = mdl._fsm.encoding
            cond = bmcutils.loop_condition(enc, 3, 1)
            
            v3   = enc.by_name['v'].at_time[3].boolean_expression
            v1   = enc.by_name['v'].at_time[1].boolean_expression
            
            cond2= v1.iff(v3)
            
            self.assertEqual(cond, cond2)
            
    def test_loop_condition_two_var(self):
        # test case 1: model with one more variables
        load_from_string(
            """
            MODULE main
            VAR     v : boolean;
                    w : boolean;
            ASSIGN  init(v) := TRUE; 
                    next(v) := !v;
            """)
        with BmcSupport():
            mdl  = bmcutils.BmcModel()
            enc  = mdl._fsm.encoding
            cond = bmcutils.loop_condition(enc, 3, 1)
            
            v = enc.by_name['v']
            w = enc.by_name['w']
            
            cond2 = ( v.at_time[1].boolean_expression.iff(v.at_time[3].boolean_expression)
                    & w.at_time[1].boolean_expression.iff(w.at_time[3].boolean_expression))
            
            self.assertEqual(cond, cond2)
            
    def test_loop_condition_not_only_state(self):
        # test case 3: only the state variables are considered
        load_from_string(
            """
            MODULE main
            IVAR    i : boolean;
            VAR     v : boolean;
                    w : boolean;
            ASSIGN  init(v) := TRUE; 
                    next(v) := !v;
            """)
        with BmcSupport():
            mdl  = bmcutils.BmcModel()
            enc  = mdl._fsm.encoding
            cond = bmcutils.loop_condition(enc, 3, 1)
            
            v = enc.by_name['v']
            w = enc.by_name['w']
            
            cond2 = ( v.at_time[1].boolean_expression.iff(v.at_time[3].boolean_expression)
                    & w.at_time[1].boolean_expression.iff(w.at_time[3].boolean_expression))
            
            self.assertEqual(cond, cond2)
    
    def test_loop_condition_consistent_values(self):
        # test case 3: only the state variables are considered
        load_from_string(
            """
            MODULE main
            IVAR    i : boolean;
            VAR     v : boolean;
                    w : boolean;
            ASSIGN  init(v) := TRUE; 
                    next(v) := !v;
            """)
        with BmcSupport():
            mdl  = bmcutils.BmcModel()
            enc  = mdl._fsm.encoding
            # loop and bound must be consistent (bound >= 0)
            with self.assertRaises(ValueError):
                bmcutils.loop_condition(enc, -5, 1)
            # loop and bound must be consistent (loop <= bound)
            with self.assertRaises(ValueError):
                bmcutils.loop_condition(enc, 2, 5)
    
    def test_successor(self):
        # case where there is a loop
        self.assertEqual( 2, bmcutils.successor( 1, 10, 0))
        self.assertEqual( 9, bmcutils.successor( 8, 10, 0))
        self.assertEqual( 0, bmcutils.successor( 9, 10, 0))
        # case when there is none
        self.assertEqual( 2, bmcutils.successor( 1, 10, bmcutils.no_loopback()))
        self.assertEqual(10, bmcutils.successor( 9, 10, bmcutils.no_loopback()))
        self.assertIsNone(bmcutils.successor(10, 10, bmcutils.no_loopback()))
        
        # time cannot be negative
        with self.assertRaises(ValueError):
            bmcutils.successor(-5, 10, 0)
        # bound cannot be negative
        with self.assertRaises(ValueError):
            bmcutils.successor(5, -5, 0)
        
        # bound and value must be consistent
        with self.assertRaises(ValueError):
            bmcutils.successor(5, 10, 20)
        
    def test_apply_inlining(self):
        load_from_string(
            """
            MODULE main
            VAR     v : boolean;
            ASSIGN  init(v) := TRUE; 
                    next(v) := !v;
            """)
        with BmcSupport():
            mdl  = bmcutils.BmcModel()
            enc  = mdl._fsm.encoding
            mgr  = enc.manager 
            v    = enc.by_name['v'].boolean_expression
            
            cond = v & v & v | v
            self.assertEqual(v, bmcutils.apply_inlining(cond))
            
            cond = v | -v
            self.assertEqual(Be.true(mgr), bmcutils.apply_inlining(cond))
            
            cond = v & -v
            self.assertEqual(Be.false(mgr), bmcutils.apply_inlining(cond))
            
    def test_apply_inlining_for_incremental_algo(self):
        load_from_string(
            """
            MODULE main
            VAR     v : boolean;
            ASSIGN  init(v) := TRUE; 
                    next(v) := !v;
            """)
        with BmcSupport():
            mdl  = bmcutils.BmcModel()
            enc  = mdl._fsm.encoding
            v    = enc.by_name['v'].boolean_expression
            
            cond = v & v & v | v
            self.assertEqual(cond.inline(True), bmcutils.apply_inlining_for_incremental_algo(cond))
            
            cond = v | -v
            self.assertEqual(cond.inline(True), bmcutils.apply_inlining_for_incremental_algo(cond))
            
            cond = v & -v
            self.assertEqual(cond.inline(True), bmcutils.apply_inlining_for_incremental_algo(cond))
            
    def test_make_nnf_boolean_wff(self):
        load_from_string(
            """
            MODULE main
            VAR     v : boolean;
                    w : boolean;
            ASSIGN  init(v) := TRUE; 
                    next(v) := !v;
            """)
        with BmcSupport():
            expr = Node.from_ptr(parse_ltl_spec("F G ( w <-> v )"))
            wff  = bmcutils.make_nnf_boolean_wff(expr)
            self.assertEquals(" F ( G (w <-> v))", str(expr))
            self.assertEquals(" F ( G ((!v | w) & (v | !w)))", str(wff))
            self.assertEquals(Wff, type(wff))
    
    def test_make_negated_nnf_boolean_wff(self):
        load_from_string(
            """
            MODULE main
            VAR     v : boolean;
                    w : boolean;
            ASSIGN  init(v) := TRUE; 
                    next(v) := !v;
            """)
        with BmcSupport():
            expr = Node.from_ptr(parse_ltl_spec("F G ( w <-> v )"))
            wff  = bmcutils.make_negated_nnf_boolean_wff(expr)
            self.assertEquals(" F ( G (w <-> v))", str(expr))
            # Via De Morgan Laws
            self.assertEquals(" G ( F ((v & !w) | (!v & w)))", str(wff))
            
    def test_is_constant_expr(self):
        expr = Node.from_ptr(parse_ltl_spec("F G ( w <-> v )"))
        self.assertFalse(bmcutils.is_constant_expr(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("some_variable"))
        self.assertFalse(bmcutils.is_constant_expr(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("TRUE"))
        self.assertTrue(bmcutils.is_constant_expr(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("FALSE"))
        self.assertTrue(bmcutils.is_constant_expr(expr))
        
    def test_is_variable(self):
        expr = Node.from_ptr(parse_ltl_spec("F G ( w <-> v )"))
        self.assertFalse(bmcutils.is_variable(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("some_variable"))
        expr.type = _parser.DOT # just to make sure it is seen as a variable, not an atom
        self.assertTrue(bmcutils.is_variable(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("TRUE"))
        self.assertFalse(bmcutils.is_variable(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("FALSE"))
        self.assertFalse(bmcutils.is_variable(expr))
        
    def test_is_past_operator(self):
        expr = Node.from_ptr(parse_ltl_spec("F G ( w <-> v )"))
        self.assertFalse(bmcutils.is_past_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("some_variable"))
        self.assertFalse(bmcutils.is_past_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("TRUE"))
        self.assertFalse(bmcutils.is_past_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("FALSE"))
        self.assertFalse(bmcutils.is_past_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("H variable"))
        self.assertTrue(bmcutils.is_past_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("Y variable"))
        self.assertTrue(bmcutils.is_past_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("O var"))
        self.assertTrue(bmcutils.is_past_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("v1 S v2"))
        self.assertTrue(bmcutils.is_past_operator(expr))
        
        # skipped : TRIGGER (because it is directly converted to an S negation)
    
    def test_is_binary_operator(self):
        expr = Node.from_ptr(parse_ltl_spec("F G ( w <-> v )"))
        self.assertFalse(bmcutils.is_binary_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("some_variable"))
        self.assertFalse(bmcutils.is_binary_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("TRUE"))
        self.assertFalse(bmcutils.is_binary_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("FALSE"))
        self.assertFalse(bmcutils.is_binary_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("H variable"))
        self.assertFalse(bmcutils.is_binary_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("Y variable"))
        self.assertFalse(bmcutils.is_binary_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("O var"))
        self.assertFalse(bmcutils.is_binary_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("v1 & v2"))
        self.assertTrue(bmcutils.is_binary_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("v1 | v2"))
        self.assertTrue(bmcutils.is_binary_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("v1 <-> v2"))
        self.assertTrue(bmcutils.is_binary_operator(expr))
        
        # this is something I added over the NuSMV macro (but it makes sense)
        expr = Node.from_ptr(parse_ltl_spec("v1 -> v2"))
        self.assertTrue(bmcutils.is_binary_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("v1 U v2"))
        self.assertTrue(bmcutils.is_binary_operator(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("v1 S v2"))
        self.assertTrue(bmcutils.is_binary_operator(expr))


    def test_operator_class(self):
        expr = Node.from_ptr(parse_ltl_spec("F G ( w <-> v )"))
        self.assertEqual(bmcutils.OperatorType.TIME_OPERATOR, bmcutils.operator_class(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("some_variable"))
        expr.type = _parser.DOT
        self.assertEqual(bmcutils.OperatorType.LITERAL, bmcutils.operator_class(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("TRUE"))
        self.assertEqual(bmcutils.OperatorType.CONSTANT_EXPR, bmcutils.operator_class(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("FALSE"))
        self.assertEqual(bmcutils.OperatorType.CONSTANT_EXPR, bmcutils.operator_class(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("H variable"))
        self.assertEqual(bmcutils.OperatorType.TIME_OPERATOR, bmcutils.operator_class(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("Y variable"))
        self.assertEqual(bmcutils.OperatorType.TIME_OPERATOR, bmcutils.operator_class(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("O var"))
        self.assertEqual(bmcutils.OperatorType.TIME_OPERATOR, bmcutils.operator_class(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("v1 & v2"))
        self.assertEqual(bmcutils.OperatorType.PROP_CONNECTIVE, bmcutils.operator_class(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("v1 | v2"))
        self.assertEqual(bmcutils.OperatorType.PROP_CONNECTIVE, bmcutils.operator_class(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("!v1"))
        self.assertEqual(bmcutils.OperatorType.LITERAL, bmcutils.operator_class(expr))
        
        # this is something I added over the NuSMV macro (but it makes sense)
        expr = Node.from_ptr(parse_ltl_spec("v1 -> v2"))
        self.assertEqual(bmcutils.OperatorType.PROP_CONNECTIVE, bmcutils.operator_class(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("v1 <-> v2"))
        self.assertEqual(bmcutils.OperatorType.PROP_CONNECTIVE, bmcutils.operator_class(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("v1 U v2"))
        self.assertEqual(bmcutils.OperatorType.TIME_OPERATOR, bmcutils.operator_class(expr))
        
        expr = Node.from_ptr(parse_ltl_spec("v1 S v2"))
        self.assertEqual(bmcutils.OperatorType.TIME_OPERATOR, bmcutils.operator_class(expr))
    
    @tests.skip("No need to actually dump that file")    
    def test_dump_problem(self):
        load_from_string(
            """
            MODULE main
            VAR     v : boolean;
                    w : boolean;
            ASSIGN  init(v) := TRUE; 
                    next(v) := !v;
            LTLSPEC F G ( w <-> v )
            """)
        with BmcSupport():
            fsm  = master_be_fsm()
            for prop in prop_database():
                pb   = generate_ltl_problem(fsm, prop.expr)
                bmcutils.dump_problem(fsm.encoding, 
                                      pb.to_cnf(),
                                      prop, 
                                      10, 0, 
                                      bmcutils.DumpType.DIMACS, "dimacs_dump")
                
    def test_print_counter_example(self):
        load_from_string(
            """
            MODULE main
            VAR     v : boolean;
                    w : boolean;
            ASSIGN  init(v) := TRUE; 
                    next(v) := !v;
                    init(w) := FALSE;
                    next(w) := !w;
            """)
        with BmcSupport():
            bound  = 2
            fsm    = master_be_fsm()
            expr   = Node.from_ptr(parse_ltl_spec("F ( w <-> v )"))
            
            pb     = generate_ltl_problem(fsm, expr, bound=bound)
            cnf    = pb.inline(True).to_cnf()

            solver = SatSolverFactory.create()
            solver+= cnf
            solver.polarity(cnf, Polarity.POSITIVE)
            self.assertEqual(SatSolverResult.SATISFIABLE, solver.solve())
            
            trace = bmcutils.print_counter_example(fsm, pb, solver, bound, "bmc")
            self.assertIsNotNone(trace)
            self.assertEqual(2, len(trace))
            
    def test_generate_counter_example(self):
        load_from_string(
            """
            MODULE main
            VAR     v : boolean;
                    w : boolean;
            ASSIGN  init(v) := TRUE; 
                    next(v) := !v;
                    init(w) := FALSE;
                    next(w) := !w;
            """)
        with BmcSupport():
            bound  = 2
            fsm    = master_be_fsm()
            expr   = Node.from_ptr(parse_ltl_spec("F ( w <-> v )"))
            
            pb     = generate_ltl_problem(fsm, expr, bound=bound)
            cnf    = pb.inline(True).to_cnf()

            solver = SatSolverFactory.create()
            solver+= cnf
            solver.polarity(cnf, Polarity.POSITIVE)
            self.assertEqual(SatSolverResult.SATISFIABLE, solver.solve())
            
            trace = bmcutils.generate_counter_example(fsm, pb, solver, bound, "GENERATED")
            self.assertIsNotNone(trace)
            self.assertEqual(2, len(trace))
            print(trace)
            
    def test_fill_counter_example(self):
        load_from_string(
            """
            MODULE main
            VAR     v : boolean;
                    w : boolean;
            ASSIGN  init(v) := TRUE; 
                    next(v) := !v;
                    init(w) := FALSE;
                    next(w) := !w;
            """)
        with BmcSupport():
            bound  = 2
            fsm    = master_be_fsm()
            sexpfsm= master_bool_sexp_fsm()
            expr   = Node.from_ptr(parse_ltl_spec("F ( w <-> v )"))
            
            pb     = generate_ltl_problem(fsm, expr, bound=bound)
            cnf    = pb.inline(True).to_cnf()

            solver = SatSolverFactory.create()
            solver+= cnf
            solver.polarity(cnf, Polarity.POSITIVE)
            self.assertEqual(SatSolverResult.SATISFIABLE, solver.solve())
            
            trace = Trace.create("FILLED", 
                                 TraceType.COUNTER_EXAMPLE, 
                                 sexpfsm.symbol_table, 
                                 sexpfsm.symbols_list, 
                                 True) 
            
            bmcutils.fill_counter_example(fsm, solver, bound, trace)
            self.assertIsNotNone(trace)
            self.assertEqual(2, len(trace))
            print(trace)
            
    def test_get_symbol(self):
        load_from_string(
            """
            MODULE main
            VAR       w : boolean;
            IVAR      x : boolean;
            FROZENVAR y : boolean;
            DEFINE  z := (x & w);
            """)
        with BmcSupport():
            # fails when not found
            with self.assertRaises(ValueError):
                bmcutils.get_symbol("a")
            # works for all types of vars
            self.assertEqual("w", str(bmcutils.get_symbol("w")))
            self.assertEqual("x", str(bmcutils.get_symbol("x")))
            self.assertEqual("y", str(bmcutils.get_symbol("y")))
            self.assertEqual("z", str(bmcutils.get_symbol("z")))
            
            
    def test_booleanize(self):
        load_from_string(
            """
            MODULE main
            VAR
                -- requires two bits
                i : 0..3;
                -- requires no transformation
                b : boolean;
            """)
        with BmcSupport():
            # fails for non existing symbols
            with self.assertRaises(ValueError):
                bmcutils.booleanize("c")
            # works as expected for existing vars
            self.assertEqual("[i.1, i.0]", str(bmcutils.booleanize("i")))
            self.assertEqual("[b]", str(bmcutils.booleanize("b")))
    
class TestBmcUtils2(unittest.TestCase):
    """Continues the same validation but allows the used of the test.Configure
    functionality"""
    
    def verify_fairness_constraint(self):
        # must be true
        tool = bmcutils.fairness_constraint(self.befsm, 0, 0)
        self.assertEqual(tool, Be.true(self.mgr))
          
        # loop position does not matter if not feasible
        with self.assertRaises(ValueError):
            bmcutils.fairness_constraint(self.befsm, 0, 1)
         
        model= bmcutils.BmcModel()
        # step 0
        tool = bmcutils.fairness_constraint(self.befsm, 1, 0)
        smv  = model.fairness(1, 0) 
        self.assertEqual(tool, smv)
          
        # step 1
        tool = bmcutils.fairness_constraint(self.befsm, 2, 1)
        smv  = model.fairness(2, 1) 
        self.assertEqual(tool, smv)
         
    def test_fairness_constraint(self):
        with tests.Configure(self, __file__, "/models/example.smv"):
            self.verify_fairness_constraint()
         
        with tests.Configure(self, __file__, "/models/philo.smv"):
            self.verify_fairness_constraint()