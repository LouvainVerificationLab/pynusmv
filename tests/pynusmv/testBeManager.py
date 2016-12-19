"""
This module verifies the behavior of the BeRbcManager class
"""
import unittest

from tests                  import utils as tests

from pynusmv.init           import init_nusmv, deinit_nusmv
from pynusmv.glob           import load_from_file 
from pynusmv.bmc.glob       import go_bmc, bmc_exit

from pynusmv.utils          import StdioFile
from pynusmv.be.expression  import Be
from pynusmv.be.encoder     import BeEnc
from pynusmv.be.manager     import BeRbcManager
from pynusmv.sat            import SatSolverFactory, Polarity


class TestBeManager(unittest.TestCase):
    """
    This test case validates the behavior of the BeRbcManager in python
    
    Note: Because this class is 'write mostly', some tests are executed for the
    sole purpose of verifying that no runtime error happens when they are executed
    """
    
    def setUp(self):
        init_nusmv()
        load_from_file(tests.current_directory(__file__)+"/models/flipflops.smv")
        go_bmc()
        self.enc = BeEnc.global_singleton_instance()
        self.mgr = self.enc.manager
      
    def tearDown(self):
        bmc_exit()
        deinit_nusmv()
 
    ###########################################################################
    # RBC mabager specific services
    ###########################################################################
    def test_with_capacity(self):
        """This test verifies that no memory exception etc.. occur"""
        mgr = BeRbcManager.with_capacity(10)
        self.assertIsNotNone(mgr, "mgr should be defined")
        self.assertTrue(mgr._freeit)
        self.assertIsNotNone(mgr._ptr, "mgr _ptr should be defined")
           
    def test_reset(self):
        """
        Verifies that resetting the cache provokes no error
        -> verifies only the absence of runtime errors since it is who RBC does 
           the heavy lifting, not the manager
        """
        mgr = BeRbcManager.with_capacity(10)
        # test it doesn't hurt to call this method even though nothing is to
        # be done.
        mgr.reset()
        # conversion to CNF populates the hashes which are being reset so 
        # using this manager to perform cnf conversion makes sense if we want
        # to test the reset works when it actually does something.
        (Be.true(mgr) and Be.false(mgr)).to_cnf(Polarity.POSITIVE)
        mgr.reset()
        
    def test_reserve(self):
        """
        Verifies that reserve causes no runtime errors. reserve is only
        used to manipulate the underlying RBC layer which is not exposed 
        """
        mgr = BeRbcManager.with_capacity(10)
        # cannot be verified w/o exposing RBC internals 
        # (which makes little sense since BE already offers a sufficient
        # abstraction)
        mgr.reserve(12)
        
    def test_dump(self):
        with StdioFile.stdout() as out:
            a = self.enc.by_name["a"].at_time[2].boolean_expression
            self.mgr.dump_davinci(a, out)
            self.mgr.dump_gdl    (a, out)
            self.mgr.dump_sexpr  (a, out)

    def test_index_to_var(self):
        a   = self.enc.by_name["a"]
        exp = self.mgr.be_index_to_var(a.index)
        self.assertEqual(exp, a.boolean_expression)
    
    def test_var_to_index(self):
        a   = self.enc.by_name["a"]
        idx = self.mgr.be_var_to_index(a.boolean_expression)
        self.assertEqual(idx, a.index)
        
    def test_index_literal_correspondence(self):
        """
        This test validates the consistency of all the conversion methods
        provided by the manager 
        (from/to : be_index/cnf_index/be_var/be_lit/cnf_lit)
        """
        a   = self.enc.by_name["a"].boolean_expression
        # converting a BE to CNF is required for the manager to store the CNF
        # literals (otherwise, there is none)
        a.to_cnf(Polarity.POSITIVE)
         
        idx = self.mgr.be_var_to_index(a)
        blit= self.mgr.be_index_to_literal(idx)
        clit= self.mgr.be_literal_to_cnf_literal(blit)
         
        self.assertEqual(blit, self.mgr.cnf_literal_to_be_literal(clit))
        self.assertEqual(idx , self.mgr.be_literal_to_index(blit))
        self.assertEqual(self.mgr.be_index_to_cnf_literal(idx), clit)
 
    def test_cnf_to_be_model(self):
        solver= SatSolverFactory.create('MiniSat')
        a     = self.enc.by_name['a'].boolean_expression
        b     = self.enc.by_name['b'].boolean_expression
        sat   = (a and -b).to_cnf()
          
        solver.add(sat)
        solver.polarity(sat, Polarity.POSITIVE)
        solver.solve()
        cnf_model = solver.model
        be_model  = self.mgr.cnf_to_be_model(cnf_model)
        self.assertEqual("Slist[-4]", str(be_model))
