import unittest

from pynusmv_lower_interface.nusmv.cinit import cinit
from pynusmv_lower_interface.nusmv.cmd import cmd
from pynusmv_lower_interface.nusmv.node import node as nsnode
from pynusmv_lower_interface.nusmv.parser import parser
from pynusmv_lower_interface.nusmv.prop import prop
from pynusmv_lower_interface.nusmv.fsm.bdd import bdd as nsfsm

from pynusmv.fsm import BddFsm

from pynusmv.init import init_nusmv, deinit_nusmv

class TestBuildModel(unittest.TestCase):
    
    def setUp(self):
        init_nusmv()
        
    def tearDown(self):
        deinit_nusmv()
    
    
    def test_build_model(self):
        # Initialize the model
        ret = cmd.Cmd_SecureCommandExecute("read_model -i"
                                           " tests/pynusmv/models/admin.smv")
        self.assertEqual(ret, 0)
        ret = cmd.Cmd_SecureCommandExecute("go")
        self.assertEqual(ret, 0)
        
        propDb = prop.PropPkg_get_prop_database()
        fsm_ptr = prop.PropDb_master_get_bdd_fsm(propDb)
        self.assertIsNotNone(fsm_ptr)
        fsm = BddFsm(fsm_ptr)
        enc = fsm.bddEnc
        self.assertIsNotNone(enc)
        init = fsm.init
        self.assertIsNotNone(init)