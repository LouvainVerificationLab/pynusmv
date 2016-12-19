"""
This module validates the behavior of the :class:`Wff` which serves to 
manipulate (and rewrite) formulas using the syntactic nodes of the AST.
"""
import unittest
from tests            import utils as tests 
from pynusmv          import glob 
from pynusmv.init     import init_nusmv, deinit_nusmv
from pynusmv.bmc.glob import go_bmc, bmc_exit, master_be_fsm
from pynusmv.wff      import Wff 
 
class TestWff(unittest.TestCase):
    def model(self):
        return tests.current_directory(__file__)+"/models/flipflops_wff.smv"
        
    def setUp(self):
        init_nusmv()
        glob.load(self.model())
        go_bmc()
        self.enc = master_be_fsm().encoding

    def tearDown(self):
        bmc_exit()
        deinit_nusmv()
    
    def test_true(self):
        self.assertEqual("TRUE", str(Wff.true()))
        self.assertEqual(0, Wff.true().depth)
         
    def test_false(self):
        self.assertEqual("FALSE", str(Wff.false()))
        self.assertEqual(0, Wff.false().depth)
     
    def test_decorate(self):
        for prop in glob.prop_database():
            # can decorate a property
            dec = Wff.decorate(prop.exprcore)
            self.assertEqual(str(dec), str(prop.exprcore))
             
            # can decorate a plain node
            x   = self.enc.by_name["x"]
            _x  = Wff.decorate(x.name)
            self.assertEqual("x", str(_x))
             
            # combination possible between plain nodes and specs
            self.assertEqual(str(dec | _x), '('+str(prop.exprcore)+" | x)")
             
    def test_depth(self):
        # raw symbol has no depth
        x   = self.enc.by_name["x"]
        y   = self.enc.by_name["y"]
         
        x_  = Wff.decorate(x.name)
        y_  = Wff.decorate(y.name)
         
        # propositional connectives do not increase the depth
        self.assertEqual(0, (x_ & y_).depth)
        self.assertEqual(0, (x_ | y_).depth)
        self.assertEqual(0, (- x_).depth)
        self.assertEqual(0, (x_.implies(y_)).to_negation_normal_form().depth)
        self.assertEqual(0, (x_.iff(y_)).to_negation_normal_form().depth)
         
        # temporal operators do increase the depth
        self.assertEqual(42, x_.next_times(42).depth) # 42 times X ( .. X(x))
        self.assertEqual( 1, x_.opnext().depth)       # X x
        self.assertEqual( 1, x_.opprec().depth)       # Y x
        self.assertEqual( 1, x_.opnotprecnot().depth) # Z x
        self.assertEqual( 1, x_.globally().depth)     # G x
        self.assertEqual( 1, x_.historically().depth) # H x
        self.assertEqual( 1, x_.eventually().depth)   # F x
        self.assertEqual( 1, x_.once().depth)         # O x
        self.assertEqual( 1, x_.until(y_).depth)      # x U y
        self.assertEqual( 1, x_.since(y_).depth)      # x S y
        self.assertEqual( 1, x_.releases(y_).depth)   # x V y
        self.assertEqual( 1, x_.triggered(y_).depth)  # x T y
     
    def test_to_negation_normal_form(self):
        x   = self.enc.by_name["x"]
        y   = self.enc.by_name["y"]
         
        x_  = Wff.decorate(x.name)
        y_  = Wff.decorate(y.name)
         
        self.assertEqual("(x -> y)", str(x_.implies(y_)))
        self.assertEqual("(!x | y)", str(x_.implies(y_).to_negation_normal_form()))
         
        self.assertEqual("(x <-> y)", str(x_.iff(y_)))
        self.assertEqual("((!x | y) & (x | !y))", str(x_.iff(y_).to_negation_normal_form()))
 
    def test_to_node(self):
        x   = self.enc.by_name["x"]
        x_  = Wff.decorate(x.name)
         
        self.assertEqual(x.name, x_.to_node())
         
    def test_to_boolean_wff(self):
        x   = self.enc.by_name["x"]
        x_  = Wff.decorate(x.name).to_boolean_wff(glob.bdd_encoding())
        # TODO: find something better to validate this
        self.assertIsNotNone(x_)
        
    def test_to_be(self):
        x   = self.enc.by_name["x"]
        x_  = Wff.decorate(x.name).to_be(self.enc)
        self.assertIsNotNone(self.enc.by_expr[x_], x.boolean_expression)
        
    def test_not_(self):
        x   = self.enc.by_name["x"]
        x_  = Wff.decorate(x.name)
        self.assertEqual("!x", str(x_.not_()))
        
    def test_and_(self):
        x   = self.enc.by_name["x"]
        y   = self.enc.by_name["y"]
         
        x_  = Wff.decorate(x.name)
        y_  = Wff.decorate(y.name)
        self.assertEqual("(x & y)", str(x_.and_(y_)))
        
    def test_or_(self):
        x   = self.enc.by_name["x"]
        y   = self.enc.by_name["y"]
         
        x_  = Wff.decorate(x.name)
        y_  = Wff.decorate(y.name)
        self.assertEqual("(x | y)", str(x_.or_(y_)))
        
    def test_implies(self):
        x   = self.enc.by_name["x"]
        y   = self.enc.by_name["y"]
         
        x_  = Wff.decorate(x.name)
        y_  = Wff.decorate(y.name)
        self.assertEqual("(x -> y)", str(x_.implies(y_)))
        
    def test_iff(self):
        x   = self.enc.by_name["x"]
        y   = self.enc.by_name["y"]
         
        x_  = Wff.decorate(x.name)
        y_  = Wff.decorate(y.name)
        self.assertEqual("(x <-> y)", str(x_.iff(y_)))
        
    def test_next(self):
        x   = self.enc.by_name["x"]
        x_  = Wff.decorate(x.name)
        self.assertEqual("next(x)", str(x_.next_()))
        
    def test_next_times(self):
        x   = self.enc.by_name["x"]
        x_  = Wff.decorate(x.name)
        self.assertEqual("x", str(x_.next_times(0)))
        self.assertEqual(" X x", str(x_.next_times(1)))
        self.assertEqual(" X ( X ( X x))", str(x_.next_times(3)))
        
    def test_opnext(self):
        x   = self.enc.by_name["x"]
        x_  = Wff.decorate(x.name)
        self.assertEqual(" X x", str(x_.opnext()))

    def test_opprec(self):
        x   = self.enc.by_name["x"]
        x_  = Wff.decorate(x.name)
        self.assertEqual(" Y x", str(x_.opprec()))
        
    def test_opnotprecnot(self):
        x   = self.enc.by_name["x"]
        x_  = Wff.decorate(x.name)
        self.assertEqual(" Z x", str(x_.opnotprecnot()))
        
    def test_globally(self):
        x   = self.enc.by_name["x"]
        x_  = Wff.decorate(x.name)
        self.assertEqual(" G x", str(x_.globally()))
        
    def test_historically(self):
        x   = self.enc.by_name["x"]
        x_  = Wff.decorate(x.name)
        self.assertEqual(" H x", str(x_.historically()))
        
    def test_eventually(self):
        x   = self.enc.by_name["x"]
        x_  = Wff.decorate(x.name)
        self.assertEqual(" F x", str(x_.eventually()))
        
    def test_once(self):
        x   = self.enc.by_name["x"]
        x_  = Wff.decorate(x.name)
        self.assertEqual(" O x", str(x_.once()))
        
    def test_until(self):
        x   = self.enc.by_name["x"]
        y   = self.enc.by_name["y"]
         
        x_  = Wff.decorate(x.name)
        y_  = Wff.decorate(y.name)
        self.assertEqual("(x U y)", str(x_.until(y_)))
        
    def test_since(self):
        x   = self.enc.by_name["x"]
        y   = self.enc.by_name["y"]
         
        x_  = Wff.decorate(x.name)
        y_  = Wff.decorate(y.name)
        self.assertEqual("(x S y)", str(x_.since(y_)))
        
    def test_releases(self):
        x   = self.enc.by_name["x"]
        y   = self.enc.by_name["y"]
         
        x_  = Wff.decorate(x.name)
        y_  = Wff.decorate(y.name)
        self.assertEqual("(x V y)", str(x_.releases(y_)))
        
    def test_triggered(self):
        x   = self.enc.by_name["x"]
        y   = self.enc.by_name["y"]
         
        x_  = Wff.decorate(x.name)
        y_  = Wff.decorate(y.name)
        self.assertEqual("(x T y)", str(x_.triggered(y_)))
        
    def test_magicmethod_and(self):
        x   = self.enc.by_name["x"]
        y   = self.enc.by_name["y"]
         
        x_  = Wff.decorate(x.name)
        y_  = Wff.decorate(y.name)
        self.assertEqual("(x & y)", str(x_ & y_))
        
    def test_magicmethod_or(self):
        x   = self.enc.by_name["x"]
        y   = self.enc.by_name["y"]
         
        x_  = Wff.decorate(x.name)
        y_  = Wff.decorate(y.name)
        self.assertEqual("(x | y)", str(x_ | y_))
        
    def test_magicmethod_neg(self):
        x   = self.enc.by_name["x"]
         
        x_  = Wff.decorate(x.name)
        self.assertEqual("!x", str( - x_ ))
        
    def test_magicmethod_invert(self):
        x   = self.enc.by_name["x"]
         
        x_  = Wff.decorate(x.name)
        self.assertEqual("!x", str(~x_))