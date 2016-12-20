from unittest          import TestCase
from tests.utils       import Configure
 
from pynusmv.bmc.utils import get_symbol 
from pynusmv.sat       import SatSolverFactory , Polarity
 
class TestMultiBitsVariables(TestCase):
    
    def test_encode_to_bits(self):
        """
        Tests the encode_to_bits method in BeEnc
        """
        with Configure(self, __file__, "/models/multibit.smv"):
            # When its a plain boolean var
            name_node = get_symbol("__bool__")
            bits      = self.enc.encode_to_bits(name_node)
            bits      = sorted(bits, key=lambda x:str(x))
            self.assertEqual("[__bool__]", str(bits))
            
            # When its not boolean but one bit is enough
            name_node = get_symbol("one_bit")
            bits      = self.enc.encode_to_bits(name_node)
            bits      = sorted(bits, key=lambda x:str(x))
            self.assertEqual("[one_bit.0]", str(bits))
            
            # When two bits are needed
            name_node = get_symbol("two_bits")
            bits      = self.enc.encode_to_bits(name_node)
            bits      = sorted(bits, key=lambda x:str(x))
            self.assertEqual("[two_bits.0, two_bits.1]", str(bits))
            
    def test_scalar(self):
        """
        Tests the scalar property in BeVar
        """
        with Configure(self, __file__, "/models/multibit.smv"):
            # When its a plain boolean var, nothing changes
            var = self.enc.by_name["__bool__"]
            self.assertEqual("__bool__", str(var.scalar))
            
            # When there are multiple bits
            var = self.enc.by_name["two_bits.0"]
            self.assertEqual("two_bits", str(var.scalar))
            
    def test_is_bit(self):
        """
        Tests the `ìs_bit` property in BeVar
        """
        with Configure(self, __file__, "/models/multibit.smv"):
            # When its a plain boolean var, nothing changes
            var = self.enc.by_name["__bool__"]
            self.assertFalse(var.is_bit)
            # When its not boolean but one bit is enough
            var = self.enc.by_name["one_bit.0"]
            self.assertTrue(var.is_bit)
            # When there are multiple bits
            var = self.enc.by_name["two_bits.0"]
            self.assertTrue(var.is_bit)
            
    def test_decode_value(self):
        """
        Tests the `ìs_bit` property in BeVar
        """
        with Configure(self, __file__, "/models/multibit.smv"):
            # It must raise an exception when there is no value
            with self.assertRaises(ValueError):
                self.enc.decode_value([])
                
            with self.assertRaises(ValueError):
                self.enc.decode_value(None)
            
            # When its a plain boolean var, nothing changes
            var = self.enc.by_name["__bool__"]
            self.assertTrue (self.enc.decode_value([(var, True)]))
            self.assertFalse(self.enc.decode_value([(var, False)]))
            
            # When its not boolean but one bit is enough
            var = self.enc.by_name["one_bit.0"]
            self.assertEqual("Ok", str(self.enc.decode_value([(var, False)])))
            self.assertEqual("Ko", str(self.enc.decode_value([(var, True)])))
            
            # When there are multiple bits
            b0 = self.enc.by_name["two_bits.0"]
            b1 = self.enc.by_name["two_bits.1"]
            
            value = [(b0, False), (b1, False)]
            self.assertEqual("Ok", str(self.enc.decode_value(value)))
            
            value = [(b0, False), (b1, True)]
            self.assertEqual("Ko", str(self.enc.decode_value(value)))
            
            value = [(b0, True), (b1, False)]
            self.assertEqual("DontKnow", str(self.enc.decode_value(value)))
            
            # Note: this is a 'weird' behavior although perfectly normal: it
            # wraps around the max value
            value = [(b0, True), (b1, True)]
            self.assertEqual("Ko", str(self.enc.decode_value(value)))
            
    def test_decode_sat_model(self):
        """
        Tests the behavior of BeEnc.decode_sat_model which may be used to build
        counter examples for complex logics
        """
        with Configure(self, __file__, "/models/multibit.smv"):
            b0 = self.enc.by_name["two_bits.0"]
            b1 = self.enc.by_name["two_bits.1"]
            
            # Dummy expression satisfied iff Ko at time 0 and Ok at time 1
            expr= b0.at_time[0].boolean_expression  &\
                  b1.at_time[0].boolean_expression  &\
                  -b0.at_time[1].boolean_expression &\
                  -b1.at_time[1].boolean_expression
            
            cnf    = expr.to_cnf()      
            solver = SatSolverFactory.create()
            solver+= cnf
            # this is not required though
            solver.polarity(cnf, polarity=Polarity.POSITIVE)
            solver.solve()
            
            decoded= self.enc.decode_sat_model(solver.model)
            # it's true iff all bits are on, that is to day Ko at both times
            expect = "{0: {'two_bits': Ko}, 1: {'two_bits': Ok}}"
            
            self.assertEqual(expect, str(decoded))
        