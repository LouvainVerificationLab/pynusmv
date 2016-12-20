import unittest

from tests                import utils as tests
from pynusmv.init         import init_nusmv, deinit_nusmv
from pynusmv.glob         import load 
from pynusmv.bmc.glob     import go_bmc, bmc_exit
from pynusmv.be.fsm       import BeFsm  
from pynusmv.sat          import SatSolverFactory, Polarity, SatSolverResult

class TestSatSolver(unittest.TestCase):
      
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
         
    def test_name(self):
        solver = SatSolverFactory.create('MiniSat')
        self.assertEqual('MiniSat', solver.name)
     
    def test_last_solving_time(self):
        solver = SatSolverFactory.create('MiniSat')
        # didn't solve anything yet
        self.assertEqual(0, solver.last_solving_time)
        # any trivial problem is solved so fast that the last solving time
        # would be 0. This is why that second case is not tested.
        # (giving in a non trvial problem makes imho the test harder to follow)
     
    def test_permanent_group(self):
        solver = SatSolverFactory.create('MiniSat')
        # note: Zchaff returns 0 for its perm. group id
        self.assertEqual(-1, solver.permanent_group)
     
    def test_random_mode(self):
        solver= SatSolverFactory.create('MiniSat')
        solver.random_mode = 0.1
        # this property is write only: nothing can be verified except that the
        # solver did not crash
     
    def test_solve(self):
        """
        This function tests the following functionalities::
         
        - add (and __iadd__)
        - solve
        - polarity
         
        """
        v   = self.fsm.encoding.by_name['v'].boolean_expression
        ########################################################################
        # THIS IS THE INCREMENTAL WAY OF DOING IT
        ########################################################################
        # solver.add_to_group(unsat, solver.permanent_group)
        # solver.group_polarity(unsat, Polarity.POSITIVE, solver.permanent_group)
        # solution = solver.solve_all_groups()
        ########################################################################
        # Tests with a satisfiable problem
        solver= SatSolverFactory.create('MiniSat')
        sat   = (v + -v).to_cnf()
        solver.add(sat)
        solver.polarity(sat, Polarity.POSITIVE)
        self.assertEqual(SatSolverResult.SATISFIABLE, solver.solve())
         
        # test with a simple unsat problem
        solver= SatSolverFactory.create('MiniSat')
        unsat = (v * -v).to_cnf()
        solver.add(unsat)
        solver.polarity(unsat, Polarity.POSITIVE)
        self.assertEqual(SatSolverResult.UNSATISFIABLE, solver.solve())
         
        # another way to represent that same unsat problem
        solver= SatSolverFactory.create('MiniSat')
        sat   = (v).to_cnf()
        # add the clause V
        solver += sat
        solver.polarity(sat, Polarity.POSITIVE)
        # and its negation (the add it actually not necessary but clearer) 
        solver += sat
        solver.polarity(sat, Polarity.NEGATIVE)
        self.assertEqual(SatSolverResult.UNSATISFIABLE, solver.solve())
         
    def test_model(self):    
        beenc = self.fsm.encoding
        solver= SatSolverFactory.create('MiniSat')
        v     = beenc.by_name['v']
        w     = beenc.by_name['w']
        vexp  = v.boolean_expression
        wexp  = w.boolean_expression
        
        sat   = (vexp * -wexp).to_cnf()
         
        solver.add(sat)
        solver.polarity(sat, Polarity.POSITIVE)
        solver.solve()
        cnf_model = solver.model
         
        self.assertTrue( v.index in set(cnf_model), 'v must be true')        
        self.assertTrue(-w.index in set(cnf_model), 'w must be false')
 
