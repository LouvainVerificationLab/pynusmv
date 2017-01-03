"""
The :mod:`pynusmv.bmc.invarspec` contains all the functionalities related to the
verification of INVARSPEC properties using a technique close to that of 
SAT-based bounded model checking for LTL.

Most of the techniques exposed in this module have been described
in [ES03]_. Therefore, the reading of this paper is highly 
recommended in order to understand the purpose, ins and outs of the algorithms 
exposed hereunder.

.. [ES03] Niklas Eén and Niklas Sörensson.
    "Temporal induction by incremental sat solving." 
    in Ofer Strichman and Armin Biere, editors, 
    Electronic Notes in Theoretical Computer Science, 
    volume 89. Elsevier, 2004.
 
"""
from enum                  import IntEnum

from pynusmv_lower_interface.nusmv.bmc     import bmc as _bmc

from pynusmv.be.expression import Be
from pynusmv.bmc           import utils
from pynusmv.exception     import NuSmvSatSolverError

##############################################################################
# PROBLEM GEN SOLVE
##############################################################################
def check_invar_induction(invar_prop, 
                          solve=True, 
                          dump_type=utils.DumpType.NONE, 
                          fname_template=None):
    """
    High level function that performs the verification of an INVAR property 
    (INVARSPEC property as obtained from the :class:`pynusmv.prop.PropDb`)
    using an inductive technique.
    
    This function performs an end to end verification of the given property
    and prints the outcome (satisfaction or violation result) to standard output

    :param invar_prop: the property to be verified. This should be an instance
        of Prop similar to what you obtain querying PropDb 
        (:func:`pynusmv.glob.prop_database()`)
    :param solve: a flag indicating whether or not the verification should 
        actually be performed. (when this flag is turned off, no sat solver is 
        not used to perform the verification and the function can serve to
        simply dump the problem to file). 
    :param dump_type: the format in which to perform a dump of the generated sat
        problem (ie dimacs). By default, this parameter takes the value 
        :data:`pynusmv.bmc.utils.DumpType.NONE` which means that the problem is
        not dumped to file. Should you want to change this behavior, then this
        parameter is used to specify a file format in conjunction with 
        `fname_template` which is used to specify the name of the location where
        the file will be output.
    :param fname_template: the file name template of the location where to output
        the dump file.
    :raises NuSmvSatSolverError: when the verification could not be
        performed because of a problem related to the sat solver
        (solver could not be created) 
    :raises ValueError: when the values of `dump_type` and `fname_template` are
        not consistent with each other (if one of them is None, both have to be
        None).
    """
    if dump_type is not utils.DumpType.NONE and fname_template is None:
        raise ValueError("a filename must be specified when dump_type is set")
    
    if fname_template is not None and dump_type is utils.DumpType.NONE:
        raise ValueError("a filename is specified but dump_type is not set")
    
    result = _bmc.Bmc_GenSolveInvar(invar_prop._ptr, 
                                   solve, 
                                   dump_type, 
                                   fname_template)
    if result == 1:
        raise NuSmvSatSolverError("The sat solver could not be created")


def check_invar_een_sorensson(invar_prop, max_bound, 
                              dump_type=utils.DumpType.NONE, 
                              fname_template=None,
                              use_extra_step=False):
    """
    High level function that performs the verification of an INVAR property 
    (INVARSPEC property as obtained from the :class:`pynusmv.prop.PropDb`)
    using a technique called 'temporal induction' proposed by N. Een and 
    N. Sorensson.
    
    This function performs an end to end verification of the given property
    and prints the outcome (satisfaction or violation result) to standard output

    .. note::
    
        This approach to invariant verification is described in [ES03]_ .
        
        This algorithm is *NOT* incremental and performs its verification by 
        the means of temporal induction.
        With this technique (as is the case for regular inductive proof), the
        proof depends on a base case and an induction step. However, in order
        to make this technique complete, the requirements are hardened with 
        two extra constraints:
         
            - all states encountered must be different.
            - the base case is assumed to hold for n consecutive steps

    :param invar_prop: the property to be verified. This should be an instance
        of Prop similar to what you obtain querying PropDb 
        (:func:`pynusmv.glob.prop_database()`)
    :param max_bound: the maximum length of a trace considered in the generated
        SAT problem.
    :param dump_type: the format in which to perform a dump of the generated sat
        problem (ie dimacs). By default, this parameter takes the value 
        :data:`pynusmv.bmc.utils.DumpType.NONE` which means that the problem is
        not dumped to file. Should you want to change this behavior, then this
        parameter is used to specify a file format in conjunction with 
        `fname_template` which is used to specify the name of the location where
        the file will be output.
    :param fname_template: the file name template of the location where to output
        the dump file.
    :raises NuSmvSatSolverError: when the verification could not be
        performed because of a problem related to the sat solver
        (solver could not be created) 
    :raises ValueError: when the values of `dump_type` and `fname_template` are
        not consistent with each other (if one of them is None, both have to be
        None).
    """
    if max_bound < 0:
        raise ValueError("Infeasible maximal bound")
    if dump_type is not utils.DumpType.NONE and fname_template is None:
        raise ValueError("a filename must be specified when dump_type is set")
    
    if fname_template is not None and dump_type is utils.DumpType.NONE:
        raise ValueError("a filename is specified but dump_type is not set")
    
    result = _bmc.Bmc_GenSolveInvar_EenSorensson(
                                invar_prop._ptr, max_bound, 
                                dump_type, fname_template, 
                                use_extra_step)
    if result == 1:
        raise NuSmvSatSolverError("The sat solver could not be created")


##############################################################################
# INCREMENTAL ALGORITHMS
##############################################################################
class InvarClosureStrategy(IntEnum):
    """
    An enumeration to parameterize the direction of the problem generation
    either forward or backward 
    """
    FORWARD = _bmc.BMC_INVAR_FORWARD_CLOSURE,
    BACKWARD= _bmc.BMC_INVAR_BACKWARD_CLOSURE
    
    
def check_invar_incrementally_dual(invar_prop, max_bound, closure_strategy):
    """
    High level function that performs the verification of an INVAR property 
    (INVARSPEC property as obtained from the :class:`pynusmv.prop.PropDb`)
    using one of the variants of a technique called 'temporal induction' 
    proposed by N. Een and N. Sorensson.
    
    This function performs an end to end verification of the given property
    and prints the outcome (satisfaction or violation result) to standard output

    Concretely, the dual algorithm is used an configure to 'increment' the SAT
    problem as specified by the `closure_strategy` which may either be forward
    or backward.

    .. note::
        
        This approach to invariant verification is described in [ES03]_ .
        
        This algorithm is incremental and performs its verification by 
        the means of temporal induction. With this technique (as is the case
        for regular inductive proof), the proof depends on a base case and an 
        induction step. However, in order to make this technique complete, the 
        requirements are hardened with two extra constraints:
         
            - all states encountered must be different.
            - the base case is assumed to hold for n consecutive steps

    :param invar_prop: the property to be verified. This should be an instance
        of Prop similar to what you obtain querying PropDb 
        (:func:`pynusmv.glob.prop_database()`)
    :param max_bound: the maximum length of a trace considered in the generated
        SAT problem.
    :param closure_strategy: an enum value that configures the way the problem
        generation is performed.
    :raises NuSmvSatSolverError: when the verification could not be
        performed because of a problem related to the sat solver
        (solver could not be created) 
    """
    if max_bound < 0:
        raise ValueError("Infeasible maximal bound")
    result = _bmc.Bmc_GenSolveInvarDual(invar_prop._ptr, max_bound, closure_strategy)
    
    if result == 1:
        raise NuSmvSatSolverError("The sat solver could not be created")


def check_invar_incrementally_zigzag(invar_prop, max_bound):
    """
    High level function that performs the verification of an INVAR property 
    (INVARSPEC property as obtained from the :class:`pynusmv.prop.PropDb`)
    using one of the variants of a technique called 'temporal induction' 
    proposed by N. Een and N. Sorensson in [ES03]_ .
    
    This function performs an end to end verification of the given property
    and prints the outcome (satisfaction or violation result) to standard output

    Concretely, the zigzag algorithm alternates between the two problem 
    expansion directions of the dual approach (either forward as in 
    Algorithm 2:'Extending Base' or backward as in Algorithm 3:'Extending Step' 

    .. note::
        
        This approach to invariant verification is described in [ES03]_ .
        
        This algorithm is incremental and performs its verification by 
        the means of temporal induction alternating between a forward and 
        backward strategy. With this technique (as is the case for regular 
        inductive proof), the proof depends on a base case and an induction 
        step. However, in order to make this technique complete, the 
        requirements are hardened with two extra constraints:
         
            - all states encountered must be different.
            - the base case is assumed to hold for n consecutive steps

    :param invar_prop: the property to be verified. This should be an instance
        of Prop similar to what you obtain querying PropDb 
        (:func:`pynusmv.glob.prop_database()`)
    :param max_bound: the maximum length of a trace considered in the generated
        SAT problem.
    :raises NuSmvSatSolverError: when the verification could not be
        performed because of a problem related to the sat solver
        (solver could not be created) 
    """
    if max_bound < 0:
        raise ValueError("Infeasible maximal bound")
    result = _bmc.Bmc_GenSolveInvarZigzag(invar_prop._ptr, max_bound)
    
    if result == 1:
        raise NuSmvSatSolverError("The sat solver could not be created")

def check_invar_incrementally_falsification(invar_prop, max_bound):
    """
    High level function that performs the verification of an INVAR property 
    (INVARSPEC property as obtained from the :class:`pynusmv.prop.PropDb`)
    using one of the variants of a technique called 'temporal induction' 
    proposed by N. Een and N. Sorensson.
    
    This function performs an end to end verification of the given property
    and prints the outcome (satisfaction or violation result) to standard output

    Concretely, the falsification algorithm is used which expands the base 
    case.

    .. note::
        
        This approach to invariant verification is described in [ES03]_ .
        
        This algorithm is incremental and performs its verification by 
        the means of temporal induction alternating between a forward and 
        backward strategy. With this technique (as is the case for regular 
        inductive proof), the proof depends on a base case and an induction 
        step. However, in order to make this technique complete, the 
        requirements are hardened with two extra constraints:
         
            - all states encountered must be different.
            - the base case is assumed to hold for n consecutive steps

    :param invar_prop: the property to be verified. This should be an instance
        of Prop similar to what you obtain querying PropDb 
        (:func:`pynusmv.glob.prop_database()`)
    :param max_bound: the maximum length of a trace considered in the generated
        SAT problem.
    :raises NuSmvSatSolverError: when the verification could not be
        performed because of a problem related to the sat solver
        (solver could not be created) 
    """
    if max_bound < 0:
        raise ValueError("Infeasible maximal bound")
    result = _bmc.Bmc_GenSolveInvarFalsification(invar_prop._ptr, max_bound)
    
    if result == 1:
        raise NuSmvSatSolverError("The sat solver could not be created")


##############################################################################
# PROBLEM GENERATION
##############################################################################
def generate_invar_problem(be_fsm, prop_node):
    """
    Builds and returns the invariant problem of the given propositional formula

    Concretely, this is the negation of (which needs to be satisfiable):
    
    .. math::
    
        (I0 \\implies P0) \\wedge \\left( \\left(P0 \\wedge R01\\right) \\implies P1 \\right)
        
    :param be_fsm: the BeFsm object that represents the model against which the 
        property will be verified. (if in doubt, it can be obtained via 
        :func:`pynusmv.bmc.glob.master_be_fsm()` )
    :param prop_node: the property for which to generate a verification problem
        represented in a 'node' format (subclass of :class:`pynusmv.node.Node`)
        which corresponds to the format obtained from the ast. (remark: if you
        need to manipulate [ie negate] the formula before passing it, it is
        perfectly valid to pass a node decorated by `Wff.decorate`).
    :return: the invariant problem of the given propositional formula
    """
    ptr = _bmc.Bmc_Gen_InvarProblem(be_fsm._ptr, prop_node._ptr)
    return Be(ptr, be_fsm.encoding.manager)

def generate_base_step(be_fsm, prop_node):
    """
    Builds and returns the boolean expression corresponding to the base step
    of the invariant problem to be generated for the given invar problem.

    Concretely, this is::
        
        I0 -> P0, where I0 is the init and invar at time 0, 
                  and   P0 is the given formula  at time 0
        
    :param be_fsm: the BeFsm object that represents the model against which the 
        property will be verified. (if in doubt, it can be obtained via 
        :func:`pynusmv.bmc.glob.master_be_fsm()` )
    :param prop_node: the property for which to generate a verification problem
        represented in a 'node' format (subclass of :class:`pynusmv.node.Node`)
        which corresponds to the format obtained from the ast. (remark: if you
        need to manipulate [ie negate] the formula before passing it, it is
        perfectly valid to pass a node decorated by `Wff.decorate`).
    :return: the invariant problem of the given propositional formula
    """
    ptr = _bmc.Bmc_Gen_InvarBaseStep(be_fsm._ptr, prop_node._ptr)
    return Be(ptr, be_fsm.encoding.manager)

def generate_inductive_step(be_fsm, prop_node):
    """
    Builds and returns the boolean expression corresponding to the inductive 
    step of the invariant problem to be generated for the given invar problem.

    Concretely, this is::
        
        (P0 and R01) -> P1, where P0 is the formula at time 0, 
                                  R01 is the transition (without init) from time 0 to 1,
                              and P1 is the formula at time 1
        
    :param be_fsm: the BeFsm object that represents the model against which the 
        property will be verified. (if in doubt, it can be obtained via 
        :func:`pynusmv.bmc.glob.master_be_fsm()` )
    :param prop_node: the property for which to generate a verification problem
        represented in a 'node' format (subclass of :class:`pynusmv.node.Node`)
        which corresponds to the format obtained from the ast. (remark: if you
        need to manipulate [ie negate] the formula before passing it, it is
        perfectly valid to pass a node decorated by `Wff.decorate`).
    :return: the invariant problem of the given propositional formula
    """
    ptr = _bmc.Bmc_Gen_InvarInductStep(be_fsm._ptr, prop_node._ptr)
    return Be(ptr, be_fsm.encoding.manager)

##############################################################################
# DUMP 
##############################################################################
def dump_dimacs_filename(be_enc, be_cnf, fname):
    """
    Opens a new file named filename, then dumps the given INVAR problem in 
    DIMACS format
    
    .. note::
        
        Calling this function is strictly equivalent to the following snippet:
        
            with StdioFile.for_name(fname) as f:
                dump_dimacs(be_enc, be_cnf, f.handle)
    
    :param be_enc: the encoding of the problem (typically fsm.encoding)
    :param be_cnf: the LTL problem represented in CNF
    :param  fname: the name of the file in which to dump the DIMACS output.
    """
    _bmc.Bmc_Dump_DimacsInvarProblemFilename(be_enc._ptr, 
                                        be_cnf._ptr,
                                        fname)

def dump_dimacs(be_enc, be_cnf, stdio_file):
    """
    Dumps the given INVAR problem in DIMACS format to the designated `stdio_file`
    
    :param be_enc: the encoding of the problem (typically fsm.encoding)
    :param be_cnf: the LTL problem represented in CNF
    :param stdio_file: the the file in which to dump the DIMACS output.
    """
    _bmc.Bmc_Dump_DimacsInvarProblem(be_enc._ptr, 
                                be_cnf._ptr,
                                stdio_file.handle)
