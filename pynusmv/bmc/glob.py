'''
The module :mod:`pynusmv.bmc.glob` serves as a reference entry point for the
bmc-related functions (commands) and global objects.

It has explicitly not been integrated with :mod:`pynusmv.glob` in order to keep
a clear distinction between the functions that are BDD and BMC related. It 
however depends on some of the functions of that module and these could be merged
(or at least grouped under a common package) in the future.
'''
from pynusmv_lower_interface.nusmv.bmc import bmc as _bmc
from pynusmv_lower_interface.nusmv.compile import compile as _compile
from pynusmv_lower_interface.nusmv.compile.symb_table import symb_table as _symb_table
from pynusmv_lower_interface.nusmv.enc.base import base as _baseenc
from pynusmv_lower_interface.nusmv.trace import trace as _trace
from pynusmv_lower_interface.nusmv.trace.exec_ import exec_ as _trc_exec
from pynusmv_lower_interface.nusmv.prop import prop as _prop

from pynusmv_lower_interface.bmc_utils import bmc_utils as _lower

from pynusmv import glob
from pynusmv.be.fsm import BeFsm
from pynusmv.exception import NuSMVNeedBooleanModelError
from pynusmv.exception import NuSMVBmcAlreadyInitializedError
from pynusmv.exception import NuSMVNoReadModelError
from pynusmv.be.encoder import BeEnc

__be_fsm   = None

def bmc_setup(force=False):
    """
    Initializes the bmc sub-system, and builds the model in a Boolean Expression 
    format. This function must be called before the use of any other bmc-related
    functionalities. Only one call per session is required.
    
    If you don't intend to do anything special, you might consider using `go_bmc`
    which is a shortcut for the whole bmc initialization process.
    
    .. note::
        This function is subject to the following requirements:
            
            - a model must be loaded (:func:`pynusmv.glob.load`)
            - hierarchy must already be flattened (:func:`pynusmv.glob.flatten_hierarchy`)
            - encoding must be already built (:func:`pynusmv.glob.encode_variables`)
            - boolean model must be already built (:func:`pynusmv.glob.build_boolean_model`)
               except if cone of influence is enabled and force is false
    
    :param force: a flag telling whether or not the boolean model must exist
       despite the cone of influence being enabled
    
    :raises NuSMVNeedBooleanModelError: if the boolean model wasn't created
    """
    # enforce preconditions
    if not _compile.cmp_struct_get_build_bool_model(glob.global_compile_cmps()):
        if not force and glob.is_cone_of_influence_enabled():
            pass
        else:
            raise NuSMVNeedBooleanModelError("boolean model must be created")
    
    if _compile.cmp_struct_get_bmc_setup(glob.global_compile_cmps()):
        raise NuSMVBmcAlreadyInitializedError("Bmc sub system already set up")
    
    # Build the vars manager, initializes the package and all sub packages, 
    # but only if not previously called.
    _bmc.Bmc_Init()
    
    build_master_be_fsm()
    
    be_fsm  = BeFsm.global_master_instance()
    be_enc  = be_fsm.encoding
    bdd_enc = glob.bdd_encoding()
    
    complete = _trc_exec.SATCompleteTraceExecutor_create(
                                be_fsm._ptr, be_enc._ptr, bdd_enc._ptr)
    _trace.TraceManager_register_complete_trace_executor(
        _trace.TracePkg_get_global_trace_manager(), 
        "sat", "SAT complete trace execution",
        _trc_exec.SATCompleteTraceExecutor2completeTraceExecutor(complete))
    
    partial_norestart = _trc_exec.SATPartialTraceExecutor_create(
                                be_fsm._ptr, be_enc._ptr, bdd_enc._ptr,False)
    _trace.TraceManager_register_partial_trace_executor(
        _trace.TracePkg_get_global_trace_manager(), 
        "sat", "SAT partial trace execution (no restart)",
        _trc_exec.SATPartialTraceExecutor2partialTraceExecutor(partial_norestart))
    
    partial_restarting= _trc_exec.SATPartialTraceExecutor_create(
                                be_fsm._ptr, be_enc._ptr, bdd_enc._ptr,True)
    _trace.TraceManager_register_partial_trace_executor(
        _trace.TracePkg_get_global_trace_manager(), 
        "sat_r", "SAT partial trace execution (restart)",
        _trc_exec.SATPartialTraceExecutor2partialTraceExecutor(partial_restarting))
    
    _compile.cmp_struct_set_bmc_setup(glob.global_compile_cmps())

def bmc_exit():
    """
    Releases all resources associated to the bmc model manager. 
    If you want to do bmc again after calling this, you will have to call
    :func:`bmc_setup` or :func:`go_bmc` again.
    """  
    global __be_fsm
    _bmc.Bmc_Quit()
    __be_fsm = None
    
    _lower.MEMOIZER_clear()

def build_master_be_fsm():
    """
    Creates the BE fsm from the Sexpr FSM. Currently the be_enc is a singleton
    global private variable which is shared between all the BE FSMs. 
    If not previoulsy committed (because a boolean encoder was not available at 
    the time due to the use of coi) the determinization layer will be committed 
    to the be_encoder
    
    :raises NuSMVBeEncNotInitializedError: if the global BeEnc singleton is not
        initialized
    """
    global __be_fsm
    # raises the exception if necessary
    be_enc = BeEnc.global_singleton_instance()
    sym_table = be_enc.symbol_table
    
    if _symb_table.SymbTable_get_layer(sym_table._ptr, "inlining") is not None:
        # commits the determ layer if not previously committed
        if not _baseenc.BaseEnc_layer_occurs(be_enc._ptr, "determ"):
            _baseenc.BaseEnc_commit_layer(be_enc._ptr, "determ")
            
        # commits the inlining layer if not previously committed
        # note: I find this a little bit weird, but that's the way NuSMV proceeds
        if not _baseenc.BaseEnc_layer_occurs(be_enc._ptr, "inlining"):
            _baseenc.BaseEnc_commit_layer(be_enc._ptr, "inlining")
    
    # actual fsm creation
    __be_fsm = BeFsm.create_from_sexp(be_enc, glob.master_bool_sexp_fsm())
    
    propdb = _prop.PropPkg_get_prop_database()
    _prop.PropDb_master_set_be_fsm(propdb, __be_fsm._ptr);
    
def master_be_fsm():
    """
    :return: the boolean FSM in BE stored in the master prop. 
    :raises NuSMVBeFsmMasterInstanceNotInitializedError:
         when the global BE FSM is null in the global properties database 
         (ie when coi is enabled).
    """
    global __be_fsm
    if __be_fsm is None:
        __be_fsm = BeFsm.global_master_instance()
    return __be_fsm

def go_bmc(force=False):
    """
    Performs all the necessary steps to use loaded model and be able to perform
    bmc related operations on it.
    
    :raises NuSMVNoReadModelError: if no module was read (:func:`pynusmv.glob.load`) 
      before this method was called. 
    """
    cmp = glob.global_compile_cmps() 
    if not _compile.cmp_struct_get_read_model(cmp):
        raise NuSMVNoReadModelError("No read model.")

    # Check cmps and perform what is needed
    if not _compile.cmp_struct_get_flatten_hrc(cmp):
        glob.flatten_hierarchy()
    if not _compile.cmp_struct_get_encode_variables(cmp):
        glob.encode_variables()
    if not _compile.cmp_struct_get_build_bool_model(cmp):
        glob.build_boolean_model(force=force)
    if not _compile.cmp_struct_get_bmc_setup(cmp):
        bmc_setup(force=force)

class BmcSupport:
    """
    This class implements a context manager (an object that can be used with a 
    'with' statement) that initializes and deinitialises BMC and its submodules.
    
    .. note::
        
        The 'support' part in the name of this class does not bear the 
        sometimes used signification of 'what makes a formula true'. Instead, 
        it is present to make the code read easily (and be easily understood
        when read)
    
    Example::
    
        with init_nusmv():
            load(model)
             
            with BmcSupport():
                # do something smart like verifying LTL properties.
    """
    def __enter__(self):
        """Magic method for the initialisation"""
        go_bmc()
    
    def __exit__(self, typ, value, traceback):
        """Magic method for the de-initialisation"""
        bmc_exit()