import unittest

from tests                 import utils as tests

from pynusmv.utils         import StdioFile
from pynusmv.init          import init_nusmv, deinit_nusmv
from pynusmv.bmc.glob      import go_bmc, bmc_exit
from pynusmv               import glob 
from pynusmv.be.fsm        import BeFsm  
from pynusmv.be.expression import Be
from pynusmv.sat           import Polarity

class TestBeCnf(unittest.TestCase):
      
    def setUp(self):
        init_nusmv()
        glob.load(tests.current_directory(__file__)+"/models/flipflops_explicit_relation.smv")
        go_bmc()
        self._fsm = BeFsm.global_master_instance()
        self._manager = self._fsm.encoding.manager
 
    def tearDown(self):
        bmc_exit()
        deinit_nusmv()
        
    def test_print_stats(self):
        # TODO: use another output file and verify the output automatically
        with StdioFile.stdout() as out:
            # constant expr always have zero clauses zero vars
            true = Be.true(self._manager)
            false= Be.false(self._manager)
            TF = true or false
            TF.to_cnf(Polarity.NOT_SET ).print_stats(out, "T/F ? => ")
            TF.to_cnf(Polarity.POSITIVE).print_stats(out, "T/F + => ")
            TF.to_cnf(Polarity.NEGATIVE).print_stats(out, "T/F - => ")
             
            # with variables
            v = self._fsm.encoding.by_name['v'].boolean_expression
            # when polarity is not set, 2 clauses are present
            v.to_cnf(Polarity.NOT_SET).print_stats( out, "Vee ? => ")
            # when polarity is positive there is one single clause
            v.to_cnf(Polarity.POSITIVE).print_stats(out, "Vee + => ")
            # when polarity is negative there is one single clause
            v.to_cnf(Polarity.NEGATIVE).print_stats(out, "Vee - => ")
    
    def test_original_problem(self):
        # constant expr always have zero clauses zero vars
        true = Be.true(self._manager)
        false= Be.false(self._manager)
        TF = true or false
        self.assertEqual(TF, TF.to_cnf(Polarity.NOT_SET ).original_problem)
        self.assertEqual(TF, TF.to_cnf(Polarity.POSITIVE).original_problem)
        self.assertEqual(TF, TF.to_cnf(Polarity.NEGATIVE).original_problem)
        
        # with variables
        v = self._fsm.encoding.by_name['v'].boolean_expression
        self.assertEqual(v, v.to_cnf(Polarity.NOT_SET).original_problem)
        self.assertEqual(v, v.to_cnf(Polarity.POSITIVE).original_problem)
        self.assertEqual(v, v.to_cnf(Polarity.NEGATIVE).original_problem)
    
    def test_vars_list(self):
        # constant expr always have zero clauses zero vars
        true = Be.true(self._manager)
        false= Be.false(self._manager)
        TF = true or false
        self.assertEqual("Slist[]", str(TF.to_cnf(Polarity.NOT_SET ).vars_list))
        self.assertEqual("Slist[]", str(TF.to_cnf(Polarity.POSITIVE).vars_list))
        self.assertEqual("Slist[]", str(TF.to_cnf(Polarity.NEGATIVE).vars_list))
        
        # with variables
        v = self._fsm.encoding.by_name['v'].boolean_expression
        self.assertEqual("Slist[1]", str(v.to_cnf(Polarity.NOT_SET ).vars_list))
        self.assertEqual("Slist[1]", str(v.to_cnf(Polarity.POSITIVE).vars_list))
        self.assertEqual("Slist[1]", str(v.to_cnf(Polarity.NEGATIVE).vars_list))
        self.assertEqual(self._fsm.encoding.by_name['v'].index, 1)

    def test_clauses_list(self):
        # constant expr always have zero clauses zero vars
        true = Be.true(self._manager)
        false= Be.false(self._manager)
        TF = true or false
        self.assertEqual("Slist[]", str(TF.to_cnf(Polarity.NOT_SET ).clauses_list))
        self.assertEqual("Slist[]", str(TF.to_cnf(Polarity.POSITIVE).clauses_list))
        self.assertEqual("Slist[]", str(TF.to_cnf(Polarity.NEGATIVE).clauses_list))
        
        # with variables
        v = self._fsm.encoding.by_name['v'].boolean_expression
        self.assertEqual("Slist[[5, -1], [-5, 1]]", str(v.to_cnf(Polarity.NOT_SET ).clauses_list))
        self.assertEqual("Slist[[-6, 1]]", str(v.to_cnf(Polarity.POSITIVE).clauses_list))
        self.assertEqual("Slist[[7, -1]]", str(v.to_cnf(Polarity.NEGATIVE ).clauses_list))
        
    def test_vars_numbers(self):
        # constant expr always have zero clauses zero vars
        true = Be.true(self._manager)
        false= Be.false(self._manager)
        TF = true or false
        self.assertEqual(0, TF.to_cnf(Polarity.NOT_SET ).vars_number)
        self.assertEqual(0, TF.to_cnf(Polarity.POSITIVE).vars_number)
        self.assertEqual(0, TF.to_cnf(Polarity.NEGATIVE).vars_number)
        
        # with variables
        v = self._fsm.encoding.by_name['v'].boolean_expression
        self.assertEqual(1, v.to_cnf(Polarity.NOT_SET ).vars_number)
        self.assertEqual(1, v.to_cnf(Polarity.POSITIVE).vars_number)
        self.assertEqual(1, v.to_cnf(Polarity.NEGATIVE).vars_number)

    def test_clauses_number(self):
        # constant expr always have zero clauses zero vars
        true = Be.true(self._manager)
        false= Be.false(self._manager)
        TF = true or false
        self.assertEqual(0, TF.to_cnf(Polarity.NOT_SET ).clauses_number)
        self.assertEqual(0, TF.to_cnf(Polarity.POSITIVE).clauses_number)
        self.assertEqual(0, TF.to_cnf(Polarity.NEGATIVE).clauses_number)
        
        # with variables
        v = self._fsm.encoding.by_name['v'].boolean_expression
        self.assertEqual(2, v.to_cnf(Polarity.NOT_SET ).clauses_number)
        self.assertEqual(1, v.to_cnf(Polarity.POSITIVE).clauses_number)
        self.assertEqual(1, v.to_cnf(Polarity.NEGATIVE).clauses_number)
    
    def test_max_var_index(self):
        # constant expr always have zero clauses zero vars
        true   = Be.true(self._manager)
        false  = Be.false(self._manager)
        TF     = true or false
        TF_cnf = TF.to_cnf(Polarity.POSITIVE)
        
        v      = self._fsm.encoding.by_name['v'].boolean_expression
        v_cnf  = v.to_cnf(Polarity.POSITIVE)
        
        self.assertEqual(0, TF_cnf.max_var_index)
        self.assertEqual(5, v_cnf.max_var_index )
        
        TF_cnf.max_var_index = 5
        v_cnf.max_var_index  = 6
        
        self.assertEqual(5, TF_cnf.max_var_index)
        self.assertEqual(6, v_cnf.max_var_index )
        
    def test_formula_literal(self):
        # constant expr always have zero clauses zero vars
        true   = Be.true(self._manager)
        false  = Be.false(self._manager)
        TF     = true or false
        TF_cnf = TF.to_cnf(Polarity.POSITIVE)
        
        v      = self._fsm.encoding.by_name['v'].boolean_expression
        v_cnf  = v.to_cnf(Polarity.POSITIVE)
        
        self.assertEqual((2**31-1), TF_cnf.formula_literal)
        self.assertEqual(5        , v_cnf.formula_literal )
        
        # fiddling with the clause literal directly seems pretty risky
        TF_cnf.formula_literal = 42
        v_cnf.formula_literal  = 42
        
        self.assertEqual(42, TF_cnf.formula_literal)
        self.assertEqual(42, v_cnf.formula_literal )
        
    def test_remove_duplicates(self):
        # verifies that it at least does not crash.
        # TODO: figure out a better test
        v  = self._fsm.encoding.by_name['v'].boolean_expression
        (v or v and v and v).to_cnf(Polarity.POSITIVE).remove_duplicates()   
        
    def test_repr(self):
        v  = self._fsm.encoding.by_name['v'].boolean_expression
        w  = self._fsm.encoding.by_name['w'].boolean_expression
        
        cnf= (w.imply(v)).to_cnf(Polarity.POSITIVE)
        self.assertTrue(str(cnf) in ["formula literal = X5 <-> (X1 | !X3)", 
                                      "formula literal = X5 <-> (!X3 | X1)"])
        
        cnf= (w.imply(v)).to_cnf(Polarity.NEGATIVE)
        # ! ( w => v ) <=> ! ( !w | v)
        #              <=> w & !v
        self.assertTrue(str(cnf) in ["formula literal = X6 <-> (X3) & (!X1)", 
                                     "formula literal = X6 <-> (!X1) & (X3)"])
        
        cnf= (w.imply(v)).to_cnf(Polarity.NOT_SET)
        self.assertTrue(str(cnf) in ["formula literal = X7 <-> (X3) & (!X1) & (X1 | !X3)", 
                                     "formula literal = X7 <-> (!X1) & (X3) & (!X3 | X1)"])
        
        # by default the polarity is positive 
        cnf= (w.imply(v)).to_cnf()
        self.assertTrue(str(cnf) in ["formula literal = X8 <-> (X1 | !X3)", 
                                     "formula literal = X8 <-> (!X3 | X1)"])
        
        # negative polarity corresponds to a negation of the formula
        cnf= (-w.imply(v)).to_cnf()
        self.assertTrue(str(cnf) in ["formula literal = X9 <-> (X3) & (!X1)", 
                                     "formula literal = X9 <-> (!X1) & (X3)"])