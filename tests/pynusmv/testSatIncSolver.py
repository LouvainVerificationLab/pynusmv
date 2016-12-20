import unittest
from tests                import utils as tests
from pynusmv.init         import init_nusmv, deinit_nusmv
from pynusmv.glob         import load 
from pynusmv.bmc.glob     import go_bmc, bmc_exit
from pynusmv.be.fsm       import BeFsm  
from pynusmv.sat          import SatSolverFactory, Polarity, SatSolverResult

class TestSatIncSolver(unittest.TestCase):
      
    def model(self):
        return tests.current_directory(__file__)+"/models/flipflops_explicit_relation.smv"

    def setUp(self):
        init_nusmv()
        load(self.model())
        go_bmc()
        self.fsm = BeFsm.global_master_instance()
 
    def tearDown(self):
        bmc_exit()
        deinit_nusmv()
        
    def test_create_group(self):
        solver = SatSolverFactory.create("MiniSat", incremental=True)
        gp     = solver.create_group()
        self.assertEqual(gp, 1)
        self.assertNotEqual(gp, solver.permanent_group)
        
    def test_destroy_group(self):
        solver = SatSolverFactory.create("MiniSat", incremental=True)
        gp     = solver.create_group()
        solver.destroy_group(gp)
        
        with self.assertRaises(Exception):
            solver.destroy_group(solver.permanent_group)
            
    def test_group_features(self):
        solver = SatSolverFactory.create("MiniSat", incremental=True)
        var    = self.fsm.encoding.by_name["v"].boolean_expression
        clause = var.to_cnf()
        nclause= (-var).to_cnf()
        
        # TEST create group
        group  = solver.create_group()
        
        # TEST add to group
        solver.add_to_group(clause, group)
        solver.polarity(clause, Polarity.POSITIVE, group)
        solver.add_to_group(nclause, group)
        solver.polarity(nclause, group)
        
        # solve all groups
        solution = solver.solve_all_groups()
        self.assertEqual(SatSolverResult.UNSATISFIABLE, solution)
        
        # solve all but group
        solution = solver.solve_without_groups([group])
        self.assertEqual(SatSolverResult.SATISFIABLE, solution)
        
        # solve all but group cannot exclude permanent
        with self.assertRaises(ValueError):
            solver.solve_without_groups([group, solver.permanent_group])
        
        # move to perm
        solver.move_to_permanent(group)
        solution = solver.solve()
        self.assertEqual(SatSolverResult.UNSATISFIABLE, solution)
    