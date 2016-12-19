"""
This module validates the behavior of the functions defined in `pynusmv.bmc.ltlspec`
"""
import unittest
from tests                 import utils as tests

from pynusmv.init          import init_nusmv, deinit_nusmv
from pynusmv.glob          import load_from_file, prop_database
from pynusmv.parser        import parse_ltl_spec
from pynusmv.node          import Node
from pynusmv.utils         import StdioFile

from pynusmv.be.expression import Be 
from pynusmv.bmc.glob      import go_bmc, bmc_exit, master_be_fsm
from pynusmv.bmc           import ltlspec 
from pynusmv.bmc           import utils 
from pynusmv.bmc.utils     import DumpType , BmcModel

from pynusmv.sat           import SatSolverFactory, Polarity, SatSolverResult

from pynusmv.wff import Wff

class TestBmcLTLSpec(unittest.TestCase):

    def setUp(self):
        init_nusmv()
        load_from_file(tests.current_directory(__file__)+"/models/dummy_ltlspecs.smv")
        go_bmc()
        self.fsm = master_be_fsm()
        
        
    def tearDown(self):
        bmc_exit()
        deinit_nusmv()
    
    def do_verify(self, problem):
        cnf    = problem.to_cnf()
        solver = SatSolverFactory.create()
        solver+= cnf
        solver.polarity(cnf, Polarity.POSITIVE)
        
        if solver.solve() == SatSolverResult.UNSATISFIABLE:
            return "No counter example"
        else:
            return "Violation found"
    
    def test_check_ltl(self):
        for prop in prop_database():
            # it must raise exception when the bound is not feasible
            with self.assertRaises(ValueError):
                ltlspec.check_ltl(prop, bound=-1)
            # it must raise exception when the bound and loop are not consistent
            with self.assertRaises(ValueError):
                ltlspec.check_ltl(prop, bound=5, loop=6)
            # it must raise exception when dump_type and fname_template are not 
            # consistent
            with self.assertRaises(ValueError):
                ltlspec.check_ltl(prop, dump_type=DumpType.DIMACS)
            with self.assertRaises(ValueError):
                ltlspec.check_ltl(prop, fname_template="should_fail")
                
            ######### Verified manually (because of the E2E nature) ###########
            # it can perform simple end to end verification
            ltlspec.check_ltl(prop)
            # it can perform verif for one single problem
            ltlspec.check_ltl(prop, one_problem=True)
            # it can do everything but solving the problem
            ltlspec.check_ltl(prop, solve=False)
            # it can be used to dump the output 
            # (works but i dont like to write a file each time I run the tests)
            #ltlspec.check_ltl(prop, 
            #                  solve=False, 
            #                  dump_type=DumpType.DIMACS, 
            #                  fname_template="test",
            #                  bound=1)
            
    def test_check_ltl_incrementally(self):
        for prop in prop_database():
            # it must raise exception when the bound is not feasible
            with self.assertRaises(ValueError):
                ltlspec.check_ltl_incrementally(prop, bound=-1)
            # it must raise exception when the bound and loop are not consistent
            with self.assertRaises(ValueError):
                ltlspec.check_ltl_incrementally(prop, bound=5, loop=6)
                
            ######### Verified manually (because of the E2E nature) ###########
            # it can perform simple end to end verification
            ltlspec.check_ltl_incrementally(prop)
            # it can perform verif for one single problem
            ltlspec.check_ltl_incrementally(prop, one_problem=True)
    
    def test_generate_ltl_problem(self):
        # parse the ltl property
        spec = Node.from_ptr(parse_ltl_spec("G ( y <= 7 )"))
        
        # it must raise exception when the bound is not feasible
        with self.assertRaises(ValueError):
            ltlspec.generate_ltl_problem(self.fsm, spec, bound=-1)
        # it must raise exception when the bound and loop are not consistent
        with self.assertRaises(ValueError):
            ltlspec.generate_ltl_problem(self.fsm, spec, bound=5, loop=6)
        
        problem = ltlspec.generate_ltl_problem(self.fsm, spec, bound=10)
        self.assertEqual("No counter example", self.do_verify(problem))
        
        # verify that the generated problem corresponds to what is announced
        model   = BmcModel().path(10)
        negspec = utils.make_negated_nnf_boolean_wff(spec)
        formula = ltlspec.bounded_semantics(self.fsm, negspec, bound=10)
        self.assertEqual(problem, model & formula)
        
    def test_bounded_semantics(self):
        # parse the ltl property
        spec = Node.from_ptr(parse_ltl_spec("G ( y <= 7 )"))
        
        # it must raise exception when the bound is not feasible
        with self.assertRaises(ValueError):
            ltlspec.bounded_semantics(self.fsm, spec, bound=-1)
        # it must raise exception when the bound and loop are not consistent
        with self.assertRaises(ValueError):
            ltlspec.bounded_semantics(self.fsm, spec, bound=5, loop=6)
        
        # verify that the generated expression corresponds to what is announced
        formula = ltlspec.bounded_semantics(self.fsm, spec, bound=10)
        no_loop = ltlspec.bounded_semantics_without_loop(self.fsm, spec, 10)
        all_loop= ltlspec.bounded_semantics_all_loops(self.fsm, spec, 10, 0)
        self.assertEqual(formula, no_loop | all_loop)
        
    def test_bounded_semantics_without_loop(self):
        # parse the ltl property
        spec = Node.from_ptr(parse_ltl_spec("G ( y <= 7 )"))
        
        # it must raise exception when the bound is not feasible
        with self.assertRaises(ValueError):
            ltlspec.bounded_semantics_without_loop(self.fsm, spec, bound=-1)
        
        # verify that the generated expression corresponds to what is announced
        no_loop = ltlspec.bounded_semantics_without_loop(self.fsm, spec, 10)
        
        # globally w/o loop is false (this is just a test)
        self.assertEqual(no_loop, Be.false(self.fsm.encoding.manager)) 
        
        # an other more complex generation
        spec = Node.from_ptr(parse_ltl_spec("F (y <= 7)"))
        no_loop = ltlspec.bounded_semantics_without_loop(self.fsm, spec, 10)
        
        #
        # The generated expression is [[f]]^{0}_{k} so (! L_{k}) is not taken 
        # care of. And actually, NuSMV does not generate that part of the 
        # formula: it only enforce the loop condition when the semantics with 
        # loop is used 
        # 
        handcrafted = Be.false(self.fsm.encoding.manager)
        y_le_seven  = Wff(parse_ltl_spec("y <= 7")).to_boolean_wff().to_be(self.fsm.encoding)
        for time_x in reversed(range(11)): # 11 because range 'eats' up the last step
            handcrafted |= self.fsm.encoding.shift_to_time(y_le_seven, time_x)
        
        #### debuging info #####
        #print("noloop  = {}".format(no_loop.to_cnf()))
        #print("hancraft= {}".format(handcrafted.to_cnf()))
        #print(self.fsm.encoding)
        self.assertEqual(no_loop, handcrafted)
    
    def test_bounded_semantics_with_loop(self):
        # parse the ltl property
        spec = Node.from_ptr(parse_ltl_spec("G ( y <= 7 )"))
        
        # it must raise exception when the bound is not feasible
        with self.assertRaises(ValueError):
            ltlspec.bounded_semantics_single_loop(self.fsm, spec, -1, -2)
        # it must raise exception when the bound and loop are not consistent
        with self.assertRaises(ValueError):
            ltlspec.bounded_semantics_single_loop(self.fsm, spec, 5, 6)
        
        # verify that the generated problem corresponds to what is announced
        # without optimisation, the all loops is built as the conjunction of all
        # the possible 'single_loops'
        all_loops = ltlspec.bounded_semantics_all_loops(self.fsm, spec, 10, 0, optimized=False)
        
        acc_loops = Be.false(self.fsm.encoding.manager)
        for time_t in range(10):
            acc_loops |= ltlspec.bounded_semantics_single_loop(self.fsm, spec, 10, time_t)
        self.assertEqual(acc_loops, all_loops)
        
        # with optimisation, it's different
        all_loops = ltlspec.bounded_semantics_all_loops(self.fsm, spec, 10, 0, optimized=True)
        self.assertNotEqual(acc_loops, all_loops)
    
    def test_bounded_semantics_with_loop_optimized_depth1(self):
        spec = Node.from_ptr(parse_ltl_spec("G ( y <= 7 )")) # depth == 1
        
        # it must raise exception when the bound is not feasible
        with self.assertRaises(ValueError):
            ltlspec.bounded_semantics_all_loops_optimisation_depth1(self.fsm, spec, -1)
        
        # should yield the same result (w/ opt) as regular all loops when depth is one   
        optimized = ltlspec.bounded_semantics_all_loops_optimisation_depth1(self.fsm, spec, 5)
        regular   = ltlspec.bounded_semantics_all_loops(self.fsm, spec, bound=5, loop=0)
        self.assertEqual(regular, optimized)
        
        # but not when the optim is turned off on 'all loops'
        regular   = ltlspec.bounded_semantics_all_loops(self.fsm, spec, bound=5, loop=0, optimized=False)
        self.assertNotEqual(regular, optimized)
        
        # and it should only be applied when the depth is equal to one
        spec = Node.from_ptr(parse_ltl_spec("F G ( y <= 7 )")) # depth == 2
        self.assertEqual(2, Wff.decorate(spec).depth)
        optimized = ltlspec.bounded_semantics_all_loops_optimisation_depth1(self.fsm, spec, 5)
        regular   = ltlspec.bounded_semantics_all_loops(self.fsm, spec, bound=5, loop=0)
        self.assertNotEqual(regular, optimized)
        
    def test_dump_dimacs(self):
        # parse the ltl property
        spec    = Node.from_ptr(parse_ltl_spec("G ( y <= 7 )"))
        problem = ltlspec.generate_ltl_problem(self.fsm, spec, bound=10)
        ltlspec.dump_dimacs(self.fsm.encoding, problem.to_cnf(), 10, StdioFile.stdout())
    
    @tests.skip("No need to pollute workspace with test files")
    def test_dump_dimacs_filename(self):
        # parse the ltl property
        spec    = Node.from_ptr(parse_ltl_spec("G ( y <= 7 )"))
        problem = ltlspec.generate_ltl_problem(self.fsm, spec, bound=10)
        ltlspec.dump_dimacs_filename(self.fsm.encoding, problem.to_cnf(), 10, "test.dimacs")