"""
This module validates the behavior of the functions defined in `pynusmv.bmc.ltlspec`
"""
import unittest
from tests                 import utils as tests

from pynusmv.init          import init_nusmv, deinit_nusmv
from pynusmv.glob          import load_from_file, prop_database
from pynusmv.utils         import StdioFile

from pynusmv.bmc.glob      import go_bmc, bmc_exit, master_be_fsm
from pynusmv.bmc           import invarspec 
from pynusmv.bmc           import utils 
from pynusmv.bmc.utils     import DumpType , BmcModel

class TestBmcInvarSpec(unittest.TestCase):
    
    def setUp(self):
        init_nusmv()
        load_from_file(tests.current_directory(__file__)+"/models/dummy_invarspecs.smv")
        go_bmc()
        self.fsm = master_be_fsm()
        
        
    def tearDown(self):
        bmc_exit()
        deinit_nusmv()
        
        
    def test_check_invar_induction(self):
        for prop in prop_database():
            # consistency of fname and dump type
            with self.assertRaises(ValueError):
                invarspec.check_invar_induction(prop, fname_template="coucou")
            with self.assertRaises(ValueError):
                invarspec.check_invar_induction(prop, dump_type=DumpType.DIMACS)
                
            # must perform the verif
            invarspec.check_invar_induction(prop)
    
    def test_check_invar_een_sorensson(self):
        for prop in prop_database():
            # consistency of fname and dump type
            with self.assertRaises(ValueError):
                invarspec.check_invar_een_sorensson(prop, 2, fname_template="coucou")
            with self.assertRaises(ValueError):
                invarspec.check_invar_een_sorensson(prop, 2, dump_type=DumpType.DIMACS)
            # 
            with self.assertRaises(ValueError):
                invarspec.check_invar_een_sorensson(prop,-1)
                 
            invarspec.check_invar_een_sorensson(prop, 2)
            
    def test_check_invar_incrementally_dual(self):
        for prop in prop_database():
            
            with self.assertRaises(ValueError):
                invarspec.check_invar_incrementally_dual(prop,-1, invarspec.InvarClosureStrategy.FORWARD)
                 
            invarspec.check_invar_incrementally_dual(prop, 2, invarspec.InvarClosureStrategy.FORWARD)
            invarspec.check_invar_incrementally_dual(prop, 2, invarspec.InvarClosureStrategy.BACKWARD)
            
    def test_check_invar_incrementally_zigzag(self):
        for prop in prop_database():
            
            with self.assertRaises(ValueError):
                invarspec.check_invar_incrementally_zigzag(prop,-1)
                 
            invarspec.check_invar_incrementally_zigzag(prop, 2)
            invarspec.check_invar_incrementally_zigzag(prop, 2)
            
    def test_check_invar_incrementally_falsification(self):
        for prop in prop_database():
            
            with self.assertRaises(ValueError):
                invarspec.check_invar_incrementally_falsification(prop,-1)
                 
            invarspec.check_invar_incrementally_falsification(prop, 2)
            invarspec.check_invar_incrementally_falsification(prop, 2)
    
    def test_generate_invar_problem(self):
        # PROBLEM = BASE STEP & INDUCTION
        for prop in prop_database():
            expr    = utils.make_nnf_boolean_wff(prop.expr)
            problem = invarspec.generate_invar_problem(self.fsm, expr)
        
            manual  = (invarspec.generate_base_step(self.fsm, expr) & 
                       invarspec.generate_inductive_step(self.fsm, expr))
           
            self.assertEqual(problem.to_cnf().vars_list, manual.to_cnf().vars_list)
            
    def test_generate_base_step(self):
        # BASE STEP = (I0 -> P0 )  
        for prop in prop_database():
            expr  = utils.make_nnf_boolean_wff(prop.expr)
            gen   = invarspec.generate_base_step(self.fsm, expr)
        
            # 
            model = BmcModel()
            i0    = model.init[0] & model.invar[0]
            # recall: the prop has to be shifted to time 0
            p0    = self.fsm.encoding.shift_to_time(expr.to_be(self.fsm.encoding), 0)
            manual= i0.imply(p0)
            self.assertEqual(gen.to_cnf().vars_list, manual.to_cnf().vars_list)

    
    def test_generate_inductive_step(self):
        # INDUCT = (P0 and R01) -> P1
        for prop in prop_database():
            expr  = utils.make_nnf_boolean_wff(prop.expr)
            gen   = invarspec.generate_inductive_step(self.fsm, expr)
        
            # 
            model = BmcModel()
            r01   = model.unrolling(0, 1)
            # recall: the prop has to be shifted to time 0
            p     = expr.to_be(self.fsm.encoding)
            p0    = self.fsm.encoding.shift_to_time(p, 0)
            p1    = self.fsm.encoding.shift_to_time(p, 1)
            manual= (p0 & r01).imply(p1)
            self.assertEqual(gen.to_cnf().vars_list, manual.to_cnf().vars_list)
    
    def test_dump_dimacs(self):
        for prop in prop_database():
            expr    = utils.make_nnf_boolean_wff(prop.expr)
            problem = invarspec.generate_invar_problem(self.fsm, expr)
            invarspec.dump_dimacs(self.fsm.encoding, problem.to_cnf(), StdioFile.stdout())
    
    @tests.skip("No need to pollute workspace with test files")
    def test_dump_dimacs_filename(self):
        for prop in prop_database():
            expr    = utils.make_nnf_boolean_wff(prop.expr)
            problem = invarspec.generate_invar_problem(self.fsm, expr)
            invarspec.dump_dimacs_filename(self.fsm.encoding, problem.to_cnf(), "testit")
            
