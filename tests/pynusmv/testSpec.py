import unittest

from pynusmv_lower_interface.nusmv.cinit import cinit
from pynusmv_lower_interface.nusmv.cmd import cmd
from pynusmv_lower_interface.nusmv.parser import parser

from pynusmv.prop import Spec
from pynusmv.node import Node, find_hierarchy
from pynusmv.prop import (true as sptrue, false as spfalse, imply, iff,
                               ex, eg, ef, eu, ew, ax, ag, af, au, aw, atom,
                               x, f, g, u, and_, or_, not_)

from pynusmv.init import init_nusmv, deinit_nusmv
from pynusmv.parser import parse_ctl_spec

class TestSpec(unittest.TestCase):
    
    def setUp(self):
        init_nusmv()
        
    def tearDown(self):
        deinit_nusmv()
        
    
    def test_types(self):
        spec = au(ex(sptrue()), ag(spfalse() & sptrue()))
        self.assertEqual(spec.type, parser.AU)
        
        exspec = spec.car
        self.assertEqual(exspec.type, parser.EX)
        self.assertIsNone(exspec.cdr)
        self.assertEqual(exspec.car.type, parser.TRUEEXP)
        
        agspec = spec.cdr
        self.assertEqual(agspec.type, parser.AG)
        self.assertIsNone(agspec.cdr)
        
        andspec = agspec.car
        self.assertEqual(andspec.type, parser.AND)
        self.assertEqual(andspec.car.type, parser.FALSEEXP)
        self.assertEqual(andspec.cdr.type, parser.TRUEEXP)
        
    
    def test_true(self):
        true = sptrue()
        self.assertEqual(true.type, parser.TRUEEXP)
        self.assertIsNone(true.car)
        self.assertIsNone(true.cdr)
        
    
    def test_false(self):
        false = spfalse()
        self.assertEqual(false.type, parser.FALSEEXP)
        self.assertIsNone(false.car)
        self.assertIsNone(false.cdr)
        
        
    def test_not(self):
        notspec = ~(sptrue())
        self.assertEqual(notspec.type, parser.NOT)
        self.assertIsNotNone(notspec.car)
        self.assertIsNone(notspec.cdr)
        self.assertEqual(notspec, not_(sptrue()))
        
        with self.assertRaises(ValueError):
            notspec = not_(None)
        
        
    def test_and(self):
        andspec = sptrue() & spfalse()
        self.assertEqual(andspec.type, parser.AND)
        self.assertIsNotNone(andspec.car)
        self.assertIsNotNone(andspec.cdr)
        self.assertEqual(andspec, and_(sptrue(), spfalse()))
        
        with self.assertRaises(ValueError):
            andspec = sptrue() & None
        with self.assertRaises(ValueError):
            andspec = and_(None, None)
        

    def test_or(self):
        orspec = sptrue() | spfalse()
        self.assertEqual(orspec.type, parser.OR)
        self.assertIsNotNone(orspec.car)
        self.assertIsNotNone(orspec.cdr)
        self.assertEqual(orspec, or_(sptrue(), spfalse()))
        
        with self.assertRaises(ValueError):
            orspec = sptrue() | None
        with self.assertRaises(ValueError):
            orspec = or_(None, None)
        
        
    def test_imply(self):
        impspec = imply(sptrue(), spfalse())
        self.assertEqual(impspec.type, parser.IMPLIES)
        self.assertIsNotNone(impspec.car)
        self.assertIsNotNone(impspec.cdr)
        
        with self.assertRaises(ValueError):
            impspec = imply(sptrue(), None)
        
        
    def test_iff(self):
        iffspec = iff(sptrue(), spfalse())
        self.assertEqual(iffspec.type, parser.IFF)
        self.assertIsNotNone(iffspec.car)
        self.assertIsNotNone(iffspec.cdr)
        
        with self.assertRaises(ValueError):
            iffspec = iff(sptrue(), None)
        
        
    def test_ex(self):
        exspec = ex(sptrue())
        self.assertEqual(exspec.type, parser.EX)
        self.assertIsNotNone(exspec.car)
        self.assertIsNone(exspec.cdr)
        
        with self.assertRaises(ValueError):
            exspec = ex(None)
        

    def test_ef(self):
        efspec = ef(sptrue())
        self.assertEqual(efspec.type, parser.EF)
        self.assertIsNotNone(efspec.car)
        self.assertIsNone(efspec.cdr)
        
        with self.assertRaises(ValueError):
            efspec = ef(None)
        

    def test_eg(self):
        egspec = eg(sptrue())
        self.assertEqual(egspec.type, parser.EG)
        self.assertIsNotNone(egspec.car)
        self.assertIsNone(egspec.cdr)
        
        with self.assertRaises(ValueError):
            egspec = eg(None)
        
        
    def test_eu(self):
        euspec = eu(sptrue(), spfalse())
        self.assertEqual(euspec.type, parser.EU)
        self.assertIsNotNone(euspec.car)
        self.assertIsNotNone(euspec.cdr)
        
        with self.assertRaises(ValueError):
            euspec = eu(None, None)
        
        
    def test_ew(self):
        ewspec = ew(sptrue(), spfalse())
        self.assertEqual(ewspec.type, parser.EW)
        self.assertIsNotNone(ewspec.car)
        self.assertIsNotNone(ewspec.cdr)
        
        with self.assertRaises(ValueError):
            ewspec = ew(None, None)
        
        
    def test_ax(self):
        axspec = ax(sptrue())
        self.assertEqual(axspec.type, parser.AX)
        self.assertIsNotNone(axspec.car)
        self.assertIsNone(axspec.cdr)
        
        with self.assertRaises(ValueError):
            axspec = ax(None)
        

    def test_af(self):
        afspec = af(sptrue())
        self.assertEqual(afspec.type, parser.AF)
        self.assertIsNotNone(afspec.car)
        self.assertIsNone(afspec.cdr)
        
        with self.assertRaises(ValueError):
            afspec = af(None)
        

    def test_ag(self):
        agspec = ag(sptrue())
        self.assertEqual(agspec.type, parser.AG)
        self.assertIsNotNone(agspec.car)
        self.assertIsNone(agspec.cdr)
        
        with self.assertRaises(ValueError):
            agspec = ag(None)
        
        
    def test_au(self):
        auspec = au(sptrue(), spfalse())
        self.assertEqual(auspec.type, parser.AU)
        self.assertIsNotNone(auspec.car)
        self.assertIsNotNone(auspec.cdr)
        
        with self.assertRaises(ValueError):
            auspec = au(None, None)
        
        
    def test_aw(self):
        awspec = aw(sptrue(), spfalse())
        self.assertEqual(awspec.type, parser.AW)
        self.assertIsNotNone(awspec.car)
        self.assertIsNotNone(awspec.cdr)
        
        with self.assertRaises(ValueError):
            awspec = aw(None, None)
        
        
    def test_x(self):
        xspec = x(sptrue())
        self.assertEqual(xspec.type, parser.OP_NEXT)
        self.assertIsNotNone(xspec.car)
        self.assertIsNone(xspec.cdr)
        
        with self.assertRaises(ValueError):
            xspec = x(None)
        

    def test_f(self):
        fspec = f(sptrue())
        self.assertEqual(fspec.type, parser.OP_FUTURE)
        self.assertIsNotNone(fspec.car)
        self.assertIsNone(fspec.cdr)
        
        with self.assertRaises(ValueError):
            fspec = f(None)
        

    def test_gg(self):
        gspec = g(sptrue())
        self.assertEqual(gspec.type, parser.OP_GLOBAL)
        self.assertIsNotNone(gspec.car)
        self.assertIsNone(gspec.cdr)
        
        with self.assertRaises(ValueError):
            gspec = g(None)
        
        
    def test_u(self):
        uspec = u(sptrue(), spfalse())
        self.assertEqual(uspec.type, parser.UNTIL)
        self.assertIsNotNone(uspec.car)
        self.assertIsNotNone(uspec.cdr)
        
        with self.assertRaises(ValueError):
            uspec = u(None, None)
    
    def test_car_cdr(self):
        spec = au(atom("s", type_checking=False),
                  atom("t", type_checking=False))
        self.assertEqual(spec.car, spec.car)
        self.assertNotEqual(spec.car, spec.cdr)
        
        parsed_spec = parse_ctl_spec("A [s U s]")
        spec = Spec(parsed_spec)
        self.assertNotEqual(spec.car, spec.cdr)
        self.assertEqual(spec.car, spec.car)
        
        newspec = au(spec.car, spec.cdr)
        self.assertEqual(spec.car, newspec.car)
        self.assertEqual(spec.cdr, newspec.cdr)
        self.assertNotEqual(spec, newspec)
        
        newspec2 = au(spec.car, spec.cdr)
        self.assertEqual(newspec, newspec2)
        
        s = {spec.car, spec.car, spec.cdr}
        self.assertEqual(len(s), 2)