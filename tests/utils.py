'''
This module defines a few decorators and (potentially) other useful functions
that makes the writing/reading of test cases clearer and easier to track.
'''
import os
import sys

from pynusmv.init      import init_nusmv, deinit_nusmv
from pynusmv.glob      import load_from_file, master_bool_sexp_fsm
from pynusmv.bmc.glob  import go_bmc, master_be_fsm, bmc_exit

def todo(fn):
    """
    A decorator to tell a test was foreseen but not implemented
    """
    return _log(fn, "Foreseen but not implemented yet")

def skip(reason):
    """
    A decorator to disable a function and warn it has been manually disabled
    """
    return lambda fn: _log(fn, "Manually disabled : {}".format(reason))

def _log(fn, message):
    """
    Returns a function to log the given message
    """
    msg = "INFO : {}.{} -> {}".format(fn.__module__, fn.__name__, message)
    return lambda *x: print(msg, file=sys.stderr) 

def canonical_cnf(be):
    """
    Returns a canonical string representation of the clauses in `be` (enable 
    comparison of generated be's)
    
    :return: a canonical string representation of the clauses in `be` when converted
        in CNF
    """
    cnf = be.to_cnf()
    clit= cnf.formula_literal
    lst = [ sorted([ item for item in array if abs(item) != clit ]) for array in cnf.clauses_list ]
    return str(sorted(lst))

def current_directory(what):
    """
    Returns the current working directory (as of now, cwd) from which the 
    current test case is loaded. Thanks to the cwd, one can write portable test
    cases as the tests will be able to load a resource relative to themselves
    at any time.
    
    Example use::
    
        def setUp(self):
            init_nusmv()
            load_from_file(tests.current_directory(__file__)+"/example.smv")
    
    :param what: the __file__ variable of the ongoing test
    :return: the cwd
    """
    return os.path.dirname(os.path.realpath(what))

class Configure:
    """
    This class provides a convenient context manager to initialize BMC test 
    cases loading the model from a file and setting the most commonly used
    fields in the testcase
    """
    
    def __init__(self, testcase, location, model):
        """
        creates a new instance
        :param testcase: the test case to initialize
        :param location: the __file__ attribute of the module in which the 
            testcase runs
        :param model: a path relative to the testcase module from where to load
            an smv model.
        """
        self.testcase = testcase
        self.model    = current_directory(location)+model
        
    def __enter__(self):
        """Performs what one would usually do in setUp"""
        init_nusmv()
        load_from_file(self.model)
        go_bmc()
        self.testcase.sexpfsm = master_bool_sexp_fsm()
        self.testcase.befsm   = master_be_fsm()
        self.testcase.enc     = self.testcase.befsm.encoding
        self.testcase.mgr     = self.testcase.enc.manager
    
    def __exit__(self, type_, value, traceback):
        """Performs what one would usually do in tearDown"""
        bmc_exit()
        deinit_nusmv()
    