'''
The module :mod:`pynusmv.bmc.utils` contains bmc related utility functions.
These are roughly organized in six categories:

    - loop related utility functions (include the generation of loop condition)
    - inlining of boolean expressions
    - ast nodes manipulations and normalization
    - BMC model / unrolling
    - problem dumping to file
    - counter example (trace) generation.
'''

from enum import IntEnum

from pynusmv_lower_interface.nusmv.bmc    import bmc    as _bmc
from pynusmv_lower_interface.nusmv.parser import parser as _parser
from pynusmv_lower_interface.bmc_utils    import bmc_utils as _lower

from pynusmv.utils          import indexed
from pynusmv                import glob
from pynusmv.wff            import Wff
from pynusmv.trace          import Trace 
from pynusmv.be.expression  import Be 
from pynusmv.bmc            import glob as bmcglob

__all__ = [# loop related stuffs
           'all_loopbacks', 'no_loopback', 'is_all_loopbacks', 'is_no_loopback',
           'loop_from_string', 'convert_relative_loop_to_absolute', 
           'check_consistency', 'loop_condition', 'successor', 'fairness_constraint',
           # inlining
           'apply_inlining', 'apply_inlining_for_incremental_algo',
           # nodes/normalization
           'make_nnf_boolean_wff', 'make_negated_nnf_boolean_wff',
           'is_constant_expr', 'is_variable', 'is_past_operator', 
           'is_binary_operator', 'OperatorType', 'operator_class', 
           # model / unrolling
           'BmcModel',
           # dumping of problem to file
           'DumpType', 'dump_problem',
           # counter examples
           'print_counter_example', 'generate_counter_example', 
           'fill_counter_example'
           ]

###############################################################################
# LOOP related functionalities
###############################################################################
def all_loopbacks():
    """
    :return: the integer value corresponding to the all loopback specification.
    """
    # returns limits.h / INT_MAX
    return _bmc.Bmc_Utils_GetAllLoopbacks()

def no_loopback():
    """
    :return: the integer value corresponding to the no loopback specification.
    """
    # returns limits.h / INT_MAX - 1
    return _bmc.Bmc_Utils_GetNoLoopback()

def is_all_loopbacks(loop):
    """
    :return: true iff the given loop number corresponds to `all_loopbacks()`
    """
    return _bmc.Bmc_Utils_IsAllLoopbacks(loop)

def is_no_loopback(loop):
    """
    :return: true iff the given loop number corresponds to `no_loopback()`
    """
    return _bmc.Bmc_Utils_IsNoLoopback(loop)

def loop_from_string(loop_text):
    """
    Given a string representing a possible loopback specification (an integer
    value, * (all) or x (none), returns the corresponding integer.
    
    :return: the integer value corresponding to the given loop spec.
    """
    if loop_text is None:
        raise ValueError("cannot convert None loop_text to something meaningful")
    
    normalized = loop_text.lower()
    
    if normalized in ["*", "all", "all loops"]:
        return all_loopbacks()
    if normalized in ["x", "no", "none", "no loop"]:
        return no_loopback()
    
    return int(loop_text)

def check_consistency(bound, loop):
    """
    This function raises an exception ValueError when the given bound and loop
    are not consistent: either bound is negative or the loop is greater than
    the bound and is none of the special values for the loop (all_loopbacks or
    no_loopbacks)
    
    :param bound: the bound of the problem, that is to say the maximum number of 
        times the problem will be unrolled. This parameter corresponds to the 
        value `k` used in the formal definitions of a bmc problem.
    :param loop: a loop definition. This is an integer value corresponding to 
        the moment in time where the loop might be starting (the parameter `l`
        in the formal definitions). However, this value is not as 'crude' as an
        absolute moment in time since it may indicate:
        
            - an absolute moment in time (obviously) when the value is positive
            - indicate a relative moment in time (when it is a negative number
              (for instance value -2 indicates that the loops are supposed to
              start 2 states ago)
            - that NO loop at all must be considered (ignore infinite behaviors)
              when this parameter takes the special value defined in 
              :func:`pynusmv.bmc.utils.no_loopback()`
            - that ALL possible loops in the model must be taken into account
              when this parameter takes the special value defined in
              :func:`pynusmv.bmc.utils.all_loopback()` (this is the default)
              
    :raises ValueError: when the `bound` and `loop` are not consistent with one
        another.
    """
    if bound < 0:
        raise ValueError("The bound value must be greater or equal to zero")
    # if the loop is greater than the bound but is none of the special values
    # raise an exception (this is inconsistent)
    if loop > bound \
       and not is_all_loopbacks(loop) \
       and not is_no_loopback(loop):
        raise ValueError("The bound and loop value are inconsistent")

def convert_relative_loop_to_absolute(l, k):
    """
    Converts a relative loop value (wich can also be an absolute loop value) 
    to an absolute loop value.

    Example::
    
      For example the -4 value when k is 10 is the value 6,
      but the value 4 (absolute loop value) is still 4


    .. note::
    
        No check is made to prevent you from entering inconsistent values.
        For instance l=-12 and k=10 will get you -2 which does not mean anything
        Similarly, l=12 and k=10 will get you 12 which should be forbidden by
        BMC semantics.
        
        If you need such consistency, check :func:`check_consistency`

    :param l: the relative loop value (which may actually be absolute)
    :param k: the bound on the considered problem
    
    :return: the absolute value for the loop
    :raises ValueError: when the given `k` and `l` are not consistent with each 
        other or when the bound `k` is negative.
    """
    check_consistency(k, l)
    
    return _bmc.Bmc_Utils_RelLoop2AbsLoop(l, k)

def loop_condition(enc, k, l):
    """
    This function generates a Be expression representing the loop condition
    which is necessary to determine that k->l is a backloop.
    
    Formally, the returned constraint is denoted :math:`{}_{l}L_{k}`
    
    Because the transition relation is encoded in Nusmv as formula (and not as
    a relation per-se), we determine the existence of a backloop between 
    l < k and forall var, var(i) == var(k)
     
    That is to say: if it is possible to encounter two times the same state
    (same state being all variables have the same value in both states) we know
    there is a backloop on the path
    
    .. note::
    
        This code was first implemented in Python with PyNuSMV but, since
        the Python implementation proved to be a huge performance bottleneck
        (profiling revealed that useless memory management was dragging the
        whole system behind), it has been translated back to C to deliver much
        better perf. results.
    
    :param fsm: the fsm on which the condition will be evaluated
    :param k: the highest time
    :param l: the time where the loop is assumed to start
    :return: a Be expression representing the loop condition that verifies that
        k-l is a loop path.
    :raises ValueError: when the given `k` and `l` are not consistent with each 
        other or when the bound `k` is negative.
    """
    check_consistency(k, l)
    
    # Note: this code was first implemented in Python with PyNuSMV but, since
    #       the Python implementation proved to be a huge performance bottleneck
    #       (profiling revealed that useless memory management was dragging the
    #       whole system behind).
    return Be(_lower.loop_condition(enc._ptr, k, l), enc.manager)

def fairness_constraint(fsm, k, l):
    """
    Computes a step of the constraint to be added to the loop side of the BE 
    when one wants to take fairness into account for the case where we consider 
    the existence of a k-l loop (between k and l obviously).
    
    .. note::
    
        This code was first implemented in Python with PyNuSMV but, since
        the Python implementation proved to be a huge performance bottleneck
        (profiling revealed that useless memory management was dragging the
        whole system behind), it has been translated back to C to deliver much
        better perf. results.
    
    :param fsm: the fsm whose transition relation must be unrolled
    :param k: the maximum (horizon/bound) time of the problem
    :param l: the time where the loop starts 
    :return: a step of the fairness constraint to force fair execution on the
        k-l loop.
    :raises ValueError: when the given `k` and `l` are not consistent with each 
        other or when the bound `k` is negative.
    """
    check_consistency(k, l)
    
    # Note: this code was first implemented in Python with PyNuSMV but, since
    #       the Python implementation proved to be a huge performance bottleneck
    #       (profiling revealed that useless memory management was dragging the
    #       whole system behind).
    return Be(_lower.fairness_constraint(fsm._ptr, k, l), fsm.encoding.manager)

def successor(time, k, l):
    """
    Returns the successor time of `time` in the context of a (loopy) trace 
    (k-l loop) on the interval [loop; bound].
    
    For a complete definition of the successor relation, check defintion 6 in
    [BCC+03]_ .
    
    .. note::
        
        In the particular case where the value of `l` equal to `no_loopback()`, 
        then the sucessor is simply `time` + 1. If on top of that, `time` is 
        equal to `k`. Then there is no sucessor and the value None is returned.  

    .. warning::
        To be consistent with the way the loop condition is implemented (equiv
        of all the state variables). In the case of a loopy path (k-l loop)
        we have that walking 'k' steps means to be back at step 'l'. Hence, the
        value of i can only vary from 0 to k-1 (and will repeat itself in the 
        range [l; k-1])
    
    .. [BCC+03] 
        A. Biere, A. Cimatti, E. Clarke, O. Strichman, and Y. Zhu. 
        "Bounded model checking."
        In Ad- vances in Computers, 
        volume 58. Academic Press, 2003.
    
    :param time: the time whose successor needs to be computed.
    :param k: the highest time
    :param l: the time where the loop is assumed to start
    :return: the successor of `time` in the context of a k-l loop.
    :raises ValueError: when the `time` or the bound `k` is negative
    """
    if time < 0:
        raise ValueError("time must be a non negative integer")
    
    check_consistency(k, l)
    
    if l == no_loopback():
        if time + 1 <= k:
            return time+1
        else:
            return None
    else:
        if time < k-1:
            return time + 1
        else:
            return l 

###############################################################################
# Inlining of boolean expressions
###############################################################################
def apply_inlining(be_expr):
    """
    Performs the inlining of `be_expr` (same effect as :func:`pynusmv.be.expression.Be.inline`)
    but uses the global user's settings in order to determine the value that 
    should be given to the `add_conj` parameter.
    
    :param be_expr: a Be expression (:class:`pynusmv.be.expression.Be`) that 
        needs to be inlined.
    :return: a boolean expression (:class:`pynusmv.be.expression.Be`) 
        equivalent to `be_expr` but inlined according to the user's preferences.
    """
    ptr = _bmc.Bmc_Utils_apply_inlining(be_expr._manager._ptr, be_expr._ptr)
    return Be(ptr, be_expr._manager)

def apply_inlining_for_incremental_algo(be_expr):
    """
    Performs the inlining of `be_expr` in a way that guarantees soundness of
    incremental algorithms. 
    
    .. note::
        
        Calling this function is strictly equivalent to calling 
        `be_expr.inline(True)`.
    
    :param be_expr: a Be expression (:class:`pynusmv.be.expression.Be`) that 
        needs to be inlined.
    :return: a boolean expression (:class:`pynusmv.be.expression.Be`) 
        equivalent to `be_expr` but inlined according to the user's preferences.
    """
    ptr = _bmc.Bmc_Utils_apply_inlining4inc(be_expr._manager._ptr, be_expr._ptr)
    return Be(ptr, be_expr._manager)

###############################################################################
# Nodes/Normalisation
###############################################################################
def get_symbol(name):
    """
    Conveniency method to retrieve a symbol (not necessarily a variable, it can
    also be a DEFINE) by its name.
    
    :param name: a string version of the name of the symbol to retrieve
    :return: a Node standing for the looked up symbol or None if it could not 
        be found.
    :raises ValueError: when the requested name cannot be found in the symbol
        table
    """
    try:
        sexpfsm = glob.master_bool_sexp_fsm()
        return next(x for x in sexpfsm.symbols_list if str(x) == name)
    except StopIteration:
        #raised when the 'name' key could not be found, rethrow
        raise ValueError("{} not found in the symbol table".format(name))
    
def booleanize(name):
    """
    Returns the list of boolean variables names standing for the symbol 
    identified by `name` in the compiled boolean model.
    
    .. note::
    
        Obviously, if `name` denotes a boolean variable, the `name` symbol is
        returned.
    
    :param name: the name of the symbol whose boolean representatives are wanted
    :return: a list of variable names (in Node format) that are used to 
        represent `name` in the encoded boolean model. 
    :raises ValueError: when the requested name cannot be found in the symbol
        table
    """
    symbol  = get_symbol(name)  
    return bmcglob.master_be_fsm().encoding.encode_to_bits(symbol)

def make_nnf_boolean_wff(prop_node):
    """
    Decorates the property identified by `prop_node` to become a boolean WFF,
    and converts the resulting formula to negation normal form. (negation sign 
    on literals only).    
    """
    return Wff.decorate(prop_node).\
                  to_boolean_wff().\
                  to_negation_normal_form()

def make_negated_nnf_boolean_wff(prop_node):
    """
    Decorates the property identified by `prop_node` to become a boolean WFF,
    negates it and converts the resulting formula to negation normal form.
    (negation sign on literals only).    
    """
    return Wff.decorate(prop_node).\
                  to_boolean_wff().\
                  not_().\
                  to_negation_normal_form()

# note: these are translations of the macros defined in bmcutils.h
def is_constant_expr(node):
    """
    Returns True iff the given node type corresponds to a constant expression
    (true or false).
    
    :param node: the expression in node format (that is to say, the format 
        obtained after parsing an expression :class:`pynusmv.node.Node`) 
        for which we want to determinate whether or not it is a constant 
        expression.
    :return: True iff the given node represents a constant expression.
    """
    return node.type in [ _parser.TRUEEXP, _parser.FALSEEXP ]

def is_variable(node):
    """
    Returns True iff the given node type corresponds to a variable expression.
    
    :param node: the expression in node format (that is to say, the format 
        obtained after parsing an expression :class:`pynusmv.node.Node`) 
        for which we want to determinate whether or not it denotes a variable.
    :return: True iff the given node represents a variable.
    """
    return node.type in [ _parser.DOT, _parser.BIT ]

def is_past_operator(node):
    """
    Returns True iff the given node type corresponds to a expression using a
    past operator.
    
    :param node: the expression in node format (that is to say, the format 
        obtained after parsing an expression :class:`pynusmv.node.Node`) 
        for which we want to determinate whether or not it denotes an expression
        using a past operator.
    :return: True iff the given node represents a past operator expression.
    """
    return node.type in [ _parser.OP_PREC, _parser.OP_NOTPRECNOT,
                          _parser.OP_ONCE, _parser.OP_HISTORICAL,
                          _parser.SINCE,   _parser.TRIGGERED]

def is_binary_operator(node):
    """
    Returns True iff the given node denotes a binary expression.
    
    :param node: the expression in node format (that is to say, the format 
        obtained after parsing an expression :class:`pynusmv.node.Node`) 
        for which we want to determinate whether or not it denotes binary
        expression.
    :return: True iff the given node represents a binary expression.
    """
    return node.type in [ _parser.AND,     _parser.OR,      _parser.IFF, 
                          _parser.IMPLIES, _parser.UNTIL,   _parser.SINCE, 
                          _parser.RELEASES,_parser.TRIGGERED ]

class OperatorType(IntEnum):
    """
    An enumeration to classify the kind of operator we are dealing with.
    """
    UNKNOWN_OP      = _bmc.UNKNOWN_OP,
    CONSTANT_EXPR   = _bmc.CONSTANT_EXPR,
    LITERAL         = _bmc.LITERAL,
    PROP_CONNECTIVE = _bmc.PROP_CONNECTIVE,
    TIME_OPERATOR   = _bmc.TIME_OPERATOR

def operator_class(node):
    """
    Determines the kind of expression represented by the given `node`.
    
    .. note::
        
        In this context, NOT is considered as negated literal and receives thus
        the LITERAL class. It is therefore not considered as as propositional
        connective.
    
    :param node: the expression in node format (that is to say, the format 
        obtained after parsing an expression :class:`pynusmv.node.Node`) 
        for whose kind needs to be determined.
    :return: the :class:`OperatorType` corresponding to the expression represented
        by `node`.
    """
    if is_constant_expr(node): 
        return OperatorType.CONSTANT_EXPR
    
    if is_variable(node) or node.type == _parser.NOT:
        return OperatorType.LITERAL
    
    if node.type in [ _parser.AND, _parser.OR, _parser.IFF, _parser.IMPLIES]:
        return OperatorType.PROP_CONNECTIVE
    
    if node.type in [ _parser.OP_PREC,  _parser.OP_NEXT,  _parser.OP_NOTPRECNOT, 
                      _parser.OP_ONCE,  _parser.OP_FUTURE,_parser.OP_HISTORICAL,
                      _parser.OP_GLOBAL,_parser.SINCE,    _parser.UNTIL, 
                      _parser.TRIGGERED,_parser.RELEASES ]:
        return OperatorType.TIME_OPERATOR
    
    return OperatorType.UNKNOWN_OP

###############################################################################
# Linear time model, useful for LTL and invariant verification
###############################################################################
class BmcModel:
    """
    The :class:`BmcModel` defines a wrapper providing an higher level interface
    to the BeFsm object. This is the object that must be used to generate the 
    LTL problems.
    """
    
    def __init__(self, be_fsm=None):
        """
        Creates a new instance from a given BeFsm.
        
        If `be_fsm` is None, the global master be_fsm is used.
        
        :param be_fsm: the fsm to wrap.
        """
        self._fsm = be_fsm if be_fsm is not None else bmcglob.master_be_fsm()
    
    @indexed.getter
    def init(self, time):
        """
        Retrieves the init states and compiles them into a BE at time `time`
        
        :param time: the time at which to consider the init.
        :return: a Be corresponding to the init states at time `time`
        :raises ValueError: if the specified time is negative.
        """
        if time < 0 :
            raise ValueError("Time cannot be negative")
        if time == 0:
            return Be(_bmc.Bmc_Model_GetInit0(self._fsm._ptr), self._fsm.encoding.manager)
        else:
            return Be(_bmc.Bmc_Model_GetInitI(self._fsm._ptr, time), self._fsm.encoding.manager)
       
    @indexed.getter 
    def invar(self, time):
        """
        Retrieves the invars and compiles them into a BE at the given time.
        
        :param time: the time at which to consider the invars.
        :return: a Be corresponding to the invar states at time `time`
        :raises ValueError: if the specified time is negative.
        """
        if time < 0 :
            raise ValueError("Time cannot be negative")
        return Be(_bmc.Bmc_Model_GetInvarAtTime(self._fsm._ptr, time), self._fsm.encoding.manager)
    
    @indexed.getter 
    def trans(self, time):
        """
        Retrieves the trans and compiles them into a BE at the given time.
        
        :param time: the time at which to consider the trans.
        :return: a Be corresponding to the trans at time `time`
        :raises ValueError: if the specified time is negative.
        """
        if time < 0 :
            raise ValueError("Time cannot be negative")
        return Be(_bmc.Bmc_Model_GetTransAtTime(self._fsm._ptr, time), self._fsm.encoding.manager)
    
    def unrolling(self, j, k):
        """
        Unrolls the transition relation from j to k, taking into account of 
        invars.
        
        :param j: the start time
        :param k: the end time
        :return: a Be representing the unrolling of the fsm from time i to k
        :raises ValueError: if one of the specified times (k,j) is negative and 
            when k < j
        """
        if j < 0 or k < 0: 
            raise ValueError("time must be positive")
        if k < j:
            raise ValueError("unrolling can only increase the amount of constraints")
        return Be(_bmc.Bmc_Model_GetUnrolling(self._fsm._ptr, j, k), self._fsm.encoding.manager)
    
    @indexed.getter
    def unrolling_fragment(self, i):
        """
        Generates the ith fragment of the transition relation unrolling. 
        (useful for incremental algorithms). Concretely, unrolls the transition 
        relation from i-1 to i
        
        :param i: the time index of the fragment to generate. 
        :return: a Be expression corresponding to the ith unrolling of the 
            transition relation.
        :raise ValueError: when `i` is negative
        """
        if i < 0:
            raise ValueError("time indices start at 0")
        ptr = _bmc.Bmc_Gen_UnrollingFragment(self._fsm._ptr, i)
        return Be(ptr, self._fsm.encoding.manager)
    
    def path(self, k, with_init=True):
        """
        Returns the path for the model from 0 to k. If the flag `with_init` is
        off, only the invariants are taken into account (and no init) otherwise
        both are taken into account.
        
        :param k: the end time
        :param with_init: a flag indicating whether or not to consider the init
        :retunr: a Be representing the paths in the model from times 0 to `k`.
        :raises ValueError: if the specified time k is negative.
        """
        if k < 0: 
            raise ValueError("time must be positive")
        if with_init:
            return Be(_bmc.Bmc_Model_GetPathWithInit(self._fsm._ptr, k), self._fsm.encoding.manager)
        else:
            return Be(_bmc.Bmc_Model_GetPathNoInit(self._fsm._ptr, k), self._fsm.encoding.manager)
    
    def fairness(self, k, l):
        """
        Generates and returns an expression representing all fairnesses in a 
        conjunctioned form.
        
        :param k: the maximum length of the considered problem
        :param l: the time when a loop may start
        
        :return:  an expression representing all fairnesses in a conjunctioned form.
        :raises ValueError: when the k and l parameters are incorrect (namely, when
            one says the loop must start after the problem bound).
        """
        if k < 0:
            raise ValueError("time (k) must be positive")
        if l >= k:
            raise ValueError("loop may not start after the problem bound hence l<k")
        return Be(_bmc.Bmc_Model_GetFairness(self._fsm._ptr, k, l), self._fsm.encoding.manager)
    
    
    ###########################################################################
    # This is specific to the verification of INVARSPEC (so not LTL)
    ###########################################################################
    
    def invar_dual_forward_unrolling(self, invarspec, i):
        """
        Performs one step in the unrolling of the invarspec property.
        
        In terms of pseudo code, this corresponds to::
        
            if i == 0 : 
                return Invar[0]
            else
                return Trans[i-1] & Invar[i] & Property[i-1]
        
        .. note:: 
            
            this is specific to the INVARSPEC verification
            
        :param invarspec: a booleanized, NNF formula representing an invariant 
            property.
        :param i: the time step for which the unrolling is generated.
        :return: Trans[i-1] & Invar[i] & Property[i-1]
        :raise ValueError: in case the given parameters are incorrect.
        """
        if invarspec is None:
            raise ValueError("an invarspec is expected")
        if i < 0:
            raise ValueError("Time must be a non negative integer")
        
        return Be(_bmc.Bmc_Model_Invar_Dual_forward_unrolling(
                                                    self._fsm._ptr,
                                                    invarspec._ptr,
                                                    i), self._fsm.encoding.manager)
    

###############################################################################
# Dumping utilities
###############################################################################
class DumpType(IntEnum):
    """
    An enumeration to specify the format in which a dump should be performed
    """
    NONE     = _bmc.BMC_DUMP_NONE,
    DIMACS,  = _bmc.BMC_DUMP_DIMACS,
    DA_VINCI = _bmc.BMC_DUMP_DA_VINCI,
    GDL      = _bmc.BMC_DUMP_GDL

def dump_problem(be_enc, be_cnf, prop, bound, loop, dump_type, fname):
    """
    Dumps the given problem (LTL or INVAR) in the specified format to the 
    designated file.
    
    .. warning::
    
        In order to call this function, `prop` *MUST* be a property as returned
        from the `PropDb` (:class:`pynusmv.prop.PropDb`). That is to say, it
        should correspond to a property which was specified in the SMV input
        text as LTLSPEC or INVARSPEC.
    
    :param be_enc: the encoding of the problem (typically fsm.encoding)
    :param be_cnf: the problem represented in CNF (may be LTL or INVAR problem)
    :param prop_node: the property being verified (the translation of be_cnf)
        represented in a 'Prop' format (subclass of :class:`pynusmv.prop.Prop`)
        which corresponds to the format obtained from the `PropDb`
        (:func:`pynusmv.glob.prop_database`)
    :param bound: the bound of the problem
    :param loop: a loop definition. This is an integer value corresponding to 
        the moment in time where the loop might be starting (the parameter `l`
        in the formal definitions). However, this value is not as 'crude' as an
        absolute moment in time since it may indicate:
        
            - an absolute moment in time (obviously) when the value is positive
            - indicate a relative moment in time (when it is a negative number
              (for instance value -2 indicates that the loops are supposed to
              start 2 states ago)
            - that NO loop at all must be considered (ignore infinite behaviors)
              when this parameter takes the special value defined in 
              :func:`pynusmv.bmc.utils.no_loopback()`
            - that ALL possible loops in the model must be taken into account
              when this parameter takes the special value defined in
              :func:`pynusmv.bmc.utils.all_loopback()` (this is the default)
              
    :param dump_type: the format in which to output the data. (:class:`DumpType`)
    :param fname: a template of the name of the file where the information will
        be dumped.
    :raise ValueError: in case the given parameters are incorrect.
    """
    if be_enc is None:
        raise ValueError("a boolean encoding is required")
    if be_cnf is None:
        raise ValueError("a boolean CNF formula is required")
    if prop is None:
        raise ValueError("a property node is required (must correspond to cnf)")
    if dump_type is None:
        raise ValueError("a dump type is required")
    if fname is None:
        raise ValueError("a file name is required")
    
    check_consistency(bound, loop)
    
    _bmc.Bmc_Dump_WriteProblem(be_enc._ptr, 
                               be_cnf._ptr, 
                               prop._ptr, 
                               bound, loop, 
                               dump_type, fname)

###############################################################################
# Counter examples utilities
###############################################################################
def print_counter_example(fsm, problem, solver, k, descr="BMC counter example"):
    """
    Prints a counter example for `problem` evaluated against `fsm` as identified
    by `solver` (problem has a length `k`) to standard output.
    
    .. note::
        
        If you are looking for something more advanced, you might want to look
        at :func:`pynusmv.be.encoder.BeEnc.decode_sat_model` which does the same
        thing but is more complete.
    
    :param fsm: the FSM against which problem was evaluated
    :param problem: the SAT problem used to identify a counter example
    :param solver: the SAT solver that identified a counter example
    :param k: the length of the generated problem (length in terms of state)
    :param descr: a description of what the generated counter example is about
    :raises ValueError: whenever the problem or the solver is None or when the 
        problem bound `k` is negative.
    """
    if problem is None:
        raise ValueError("a problem must be given")
    if solver is None:
        raise ValueError("a solver must be given")
    if k < 0:
        raise ValueError("the problem bound `k` must be non negative")
    
    print("Property is violated for path of length {}".format(k))
    ptr = _bmc.Bmc_Utils_generate_and_print_cntexample(
            fsm.encoding._ptr, solver._as_SatSolver_ptr(),
            problem._ptr, k, descr,
            glob.master_bool_sexp_fsm().symbols_list._ptr)
    return Trace(ptr)


def generate_counter_example(fsm, problem, solver, k, descr="BMC counter example"):
    """
    Generates a counter example for `problem` evaluated against `fsm` as 
    identified by `solver` (problem has a length `k`) but prints nothing.
    
    .. note::
        
        If you are looking for something more advanced, you might want to look
        at :func:`pynusmv.be.encoder.BeEnc.decode_sat_model` which does the same
        thing but is more complete.
    
    :param fsm: the FSM against which problem was evaluated
    :param problem: the SAT problem used to identify a counter example
    :param solver: the SAT solver that identified a counter example
    :param k: the length of the generated problem (length in terms of state)
    :param descr: a description of what the generated counter example is about
    :raises ValueError: whenever the problem or the solver is None or when the 
        problem bound `k` is negative.
    """
    if problem is None:
        raise ValueError("a problem must be given")
    if solver is None:
        raise ValueError("a solver must be given")
    if k < 0:
        raise ValueError("the problem bound `k` must be non negative")
    
    ptr = _bmc.Bmc_Utils_generate_cntexample(
            fsm.encoding._ptr, solver._as_SatSolver_ptr(),
            problem._ptr, k, descr,
            glob.master_bool_sexp_fsm().symbols_list._ptr)
    return Trace(ptr)

def fill_counter_example(fsm, solver, k, trace):
    """
    Uses the given sat solver instance to fill the details of the trace and
    store it all in `trace`.
    
    .. note::
        
        If you are looking for something more advanced, you might want to look
        at :func:`pynusmv.be.encoder.BeEnc.decode_sat_model` which does the same
        thing but is more complete.
    
    .. note::
    
        The given `trace` *must* be empty, otherwise an exception is raised.
    
    :param fsm: the FSM against which problem was evaluated
    :param solver: the SAT solver that identified a counter example
    :param k: the length of the generated problem (length in terms of state)
    :param trace: the trace to be populated with the details read from the sat
        solver.
    :return: `trace` but populated with the counter example extracted from the
        solver model.
    :raise NuSmvIllegalTraceStateError: if the given `trace` is not empty.
    :raises ValueError: whenever the fsm, solver or trace is None or when the 
        problem bound `k` is negative.
    """
    if fsm is None:
        raise ValueError("an fsm must be given")
    if solver is None:
        raise ValueError("a solver must be given")
    if trace is None:
        raise ValueError("a trace must be given")
    if k < 0:
        raise ValueError("the problem bound `k` must be non negative")
    
    _bmc.Bmc_Utils_fill_cntexample(
            fsm.encoding._ptr, solver._as_SatSolver_ptr(), k, trace._ptr)
    return trace
