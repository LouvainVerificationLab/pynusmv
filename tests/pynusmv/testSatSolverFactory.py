import unittest

import pynusmv.init as init
from pynusmv.sat   import SatSolverFactory
from pynusmv.sat   import SatSolver
from pynusmv.sat   import SatProofSolver
from pynusmv.sat   import SatIncSolver
from pynusmv.sat   import SatIncProofSolver

class TestSatSolverFactory(unittest.TestCase):
    
    def setUp(self):
        init.init_nusmv()

    def tearDown(self):
        init.deinit_nusmv()

    def test_getAvailableSolvers(self):
        self.assertEqual({'ZChaff', 'MiniSat'}, SatSolverFactory.available_solvers())
    
    def test_printAvailableSolvers(self):
        SatSolverFactory.print_available_solvers()
    
    def test_normalize_name(self):
        normalized = SatSolverFactory.normalize_name("minisat")
        self.assertEquals(normalized, 'MiniSat')
        
        normalized = SatSolverFactory.normalize_name("MINISAT")
        self.assertEquals(normalized, 'MiniSat')
        
        normalized = SatSolverFactory.normalize_name("mInIsAt")
        self.assertEquals(normalized, 'MiniSat')
        
        normalized = SatSolverFactory.normalize_name("MiniSat")
        self.assertEquals(normalized, 'MiniSat')
        
        normalized = SatSolverFactory.normalize_name("zchaff")
        self.assertEquals(normalized, 'ZChaff')
        
        normalized = SatSolverFactory.normalize_name("ZCHAFF")
        self.assertEquals(normalized, 'ZChaff')
        
        normalized = SatSolverFactory.normalize_name("ZcHaFf")
        self.assertEquals(normalized, 'ZChaff')
        
        normalized = SatSolverFactory.normalize_name("ZChaff")
        self.assertEquals(normalized, 'ZChaff')
        
        with self.assertRaises(ValueError):
            SatSolverFactory.normalize_name("bonjour")
            
    def test_create_minisat(self):
        solver = SatSolverFactory.create('minisat', True, True)
        self.assertIsNotNone(solver)
        self.assertEquals(type(solver), SatIncProofSolver)
        
        solver = SatSolverFactory.create('minisat', True, False)
        self.assertIsNotNone(solver)
        self.assertEquals(type(solver), SatIncSolver)
        
        solver = SatSolverFactory.create('minisat', False, True)
        self.assertIsNotNone(solver)
        self.assertEquals(type(solver), SatProofSolver)
        
        solver = SatSolverFactory.create('minisat', False, False)
        self.assertIsNotNone(solver)
        self.assertEquals(type(solver), SatSolver)
    
    def test_create_zchaff(self):
        with self.assertRaises(ValueError):
            SatSolverFactory.create('zchaff', True, True)
        
        with self.assertRaises(ValueError):
            SatSolverFactory.create('zchaff', False, True)
        
        solver = SatSolverFactory.create('zchaff', True, False)
        self.assertIsNotNone(solver)
        self.assertEquals(type(solver), SatIncSolver)
        
        solver = SatSolverFactory.create('zchaff', False, False)
        self.assertIsNotNone(solver)
        self.assertEquals(type(solver), SatSolver)
