"""
The :mod:`pynusmv.bmc.ltlspec` contains all the functionalities related to the
bounded model checking of LTL properties: from end to end property verification
to the translation of formulas to boolean expressions corresponding to the 
SAT problem necessary to verify these using LTL bounded semantics of the dumping
of problem to file (in DIMACS format)
"""
from pynusmv_lower_interface.nusmv.bmc  import bmc as _bmc
from pynusmv_lower_interface.nusmv.node import node as _node
from pynusmv_lower_interface.bmc_utils  import bmc_utils as _lower

from pynusmv.node                import Node
from pynusmv.be.expression       import Be
from pynusmv.exception           import NuSmvSatSolverError
from pynusmv.bmc                 import utils

__all__ = ['check_ltl',
           'check_ltl_incrementally',
           'generate_ltl_problem',
           'bounded_semantics',
           'bounded_semantics_without_loop',
           'bounded_semantics_single_loop',
           'bounded_semantics_all_loops_optimisation_depth1',
           'bounded_semantics_all_loops',
           'bounded_semantics_without_loop_at_offset',
           'bounded_semantics_with_loop_at_offset',
           'bounded_semantics_at_offset',
           'dump_dimacs_filename',
           'dump_dimacs'
           ]

##############################################################################
# PROBLEM GEN SOLVE
##############################################################################
def check_ltl(ltl_prop, 
              bound=10, 
              loop=utils.all_loopbacks(), 
              one_problem=False, 
              solve=True, 
              dump_type=utils.DumpType.NONE, 
              fname_template=None):
    """
    High level function that performs the verification of an LTL property 
    (LTLSPEC property as obtained from the :class:`pynusmv.prop.PropDb`).
    
    This function performs an end to end verification of the given LTL property
    and prints the outcome (satisfaction or violation result) to standard output
    
    Formally, it tries to determine if the problem :math:`[[M,f]]_{k}` is satisfiable. 
    This problem is generated as 
    
    .. math::
    
        [[M]]_{k} \\wedge \\neg ( (\\neg L_{k} \\wedge [[ltl\\_prop]]_{k}) \\vee {}_{l}[[ltl\\_prop]]_{k}^{l} )
    
    :param ltl_prop: the LTL property to be verified. This should be an instance
        of Prop similar to what you obtain querying PropDb 
        (:func:`pynusmv.glob.prop_database()`)
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
              
    :param one_problem: a flag indicating whether the problem should be verified
        for all possible execution lengths UP TO `bound` or if it should be 
        evaluated only for executions that have the exact length `bound`.
        By default this flag is OFF and all problem lengths up to `bound` are 
        verified.
    :param solve: a flag indicating whether or not the verification should 
        actually be performed. (when this flag is turned off, no sat solver is 
        not used to perform the bmc verification and the function can serve to
        simply dump the ltl problem to files). 
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
    :raises ValueError: when the bound is infeasible (negative value) or when
        the loop and bound values are inconsistent (loop is greater than the
        bound but none of the special values described above)
    """
    utils.check_consistency(bound, loop)
    
    if dump_type is not utils.DumpType.NONE and fname_template is None:
        raise ValueError("a filename must be specified when dump_type is set")
    
    if fname_template is not None and dump_type is utils.DumpType.NONE:
        raise ValueError("a filename is specified but dump_type is not set")
    
    result = _bmc.Bmc_GenSolveLtl(ltl_prop._ptr, 
                                  bound, loop, 
                                  not one_problem, 
                                  solve, 
                                  dump_type, 
                                  fname_template)
    if result == 1:
        raise NuSmvSatSolverError("The sat solver could not be created")

def check_ltl_incrementally(ltl_prop, 
                            bound=10, 
                            loop=utils.all_loopbacks(), 
                            one_problem=False, ):
    """
    Performs the same end to end LTL property verification as `check_ltl` but
    generates the problem /incrementally/ instead of doing it all at once.
    
    Concretely, this means that it does not compute the complete unrolling of 
    the transition relation :math:`[[M]]_{k}` up front but computes each unrolling
    step separately and adds it to a group of the incremental sat solver. 
    
    The bounded semantics conversion of `ltl_prop` is done the exact same way 
    as in `check_ltl`. So the real gain of calling this function resides in 
    the avoidance of the regeneration of the formula representing the unrolled
    transition relation for lengths < bound. (and thus in the reduction of the 
    size of the generated formula that needs to be solved).
    
    :param ltl_prop: the LTL property to be verified. This should be an instance
        of Prop similar to what you obtain querying PropDb 
        (:func:`pynusmv.glob.prop_database()`)
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
              
    :param one_problem: a flag indicating whether the problem should be verified
        for all possible execution lengths UP TO `bound` or if it should be 
        evaluated only for executions that have the exact length `bound`.
        By default this flag is OFF and all problem lengths up to `bound` are 
        verified.
    :raises NuSmvSatSolverError: when the verification could not be
        performed because of a problem related to the sat solver
        (solver could not be created)
    :raises ValueError: when the bound is infeasible (negative value) or when
        the loop and bound values are inconsistent (loop is greater than the
        bound but none of the special values described above)
    """
    utils.check_consistency(bound, loop)
    
    result = _bmc.Bmc_GenSolveLtlInc(ltl_prop._ptr,bound, loop, not one_problem)
    if result == 1:
        raise NuSmvSatSolverError("The sat solver could not be created")

##############################################################################
# PROBLEM GENERATION
##############################################################################
def generate_ltl_problem(fsm, prop_node, bound=10, loop=utils.all_loopbacks()):
    """
    Generates a (non-incremental) Be expression corresponding to the SAT problem
    denoted by :math:`[[fsm, prop\\_node]]_{bound}^{loop}`
    
    That is to say it generates the problem that combines both the formula and
    and the model to perform the verification. Put another way, this problem
    can be read as: 
    
    .. math::
    
        [[fsm]]_{bound} \\wedge \\neg ( (\\neg L_k \\wedge [[ \\neg prop\\_node]]_{k}) \\vee {}_{l}[[ \\neg prop\\_node]]_{k}^{l} )
     
    :param fsm: the BeFsm object that represents the model against which the 
        property will be verified. (if in doubt, it can be obtained via 
        :func:`pynusmv.bmc.glob.master_be_fsm()` )
    :param prop_node: the property for which to generate a verification problem
        represented in a 'node' format (subclass of :class:`pynusmv.node.Node`)
        which corresponds to the format obtained from the ast. (remark: if you
        need to manipulate [ie negate] the formula before passing it, it is
        perfectly valid to pass a node decorated by `Wff.decorate`).
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
              
    :return: a Be boolean expression representing the satisfiability problem of
        for the verification of this property.
    :raises ValueError: when the bound is infeasible (negative value) or when
        the loop and bound values are inconsistent (loop is greater than the
        bound but none of the special values described above)
    """
    utils.check_consistency(bound, loop)
    
    ltl_wff = utils.make_negated_nnf_boolean_wff(prop_node)
    be_ptr  = _bmc.Bmc_Gen_LtlProblem(fsm._ptr, ltl_wff._ptr, bound, loop)
    return Be(be_ptr, fsm.encoding.manager)

#
###############################################################################
####################### Bounded semantics of a formula ########################
###############################################################################

def bounded_semantics(fsm, prop_node, bound=10, loop=utils.all_loopbacks()):
    """
    Generates a Be expression corresponding to the bounded semantics of the
    given LTL formula. It combines the bounded semantics of the formula when 
    there is a loop and when there is none with the loop condition.
    
    In the literature, the resulting formula would be denoted as 
    
    .. math::
    
       [[f]]_{k} :=
           (\\neg L_{k} \\wedge [[f]]^{0}_{k} ) \\vee (\\bigvee_{j=l}^{k} {}_{j}L_{k} \\wedge {}_{j}[[f]]_{k}^{0})
        
    where l is used to denote `loop`, f for `prop_node` and k for the `bound`.
        
    .. note::
    
        Fairness is taken into account in the generation of the resulting 
        expression
        
    :param fsm: the fsm against which the formula will be evaluated. It is not
        directly relevant to the generation of the formula for `prop_node` but
        is used to determine to generate fairness constraints for this model
        which are combined with `prop_node` constraint.
    :param prop_node: the property for which to generate a verification problem
        represented in a 'node' format (subclass of :class:`pynusmv.node.Node`)
        which corresponds to the format obtained from the ast.(remark: if you
        need to manipulate [ie negate] the formula before passing it, it is
        perfectly valid to pass a node decorated by `Wff.decorate`).
    :param bound: the bound of the problem, that is to say the maximum number of 
        times the problem will be unrolled. This parameter corresponds to the 
        value `k` used in the formal definitions of a bmc problem.
    :param optimized: a flag indicating whether or not the use of the 
        optimisation for formulas of depth 1 is desired.
        
    :return: a boolean expression corresponding to the bounded semantics of 
        `prop_node`
    :raises ValueError: when the bound is infeasible (negative value) or when
        the loop and bound values are inconsistent (loop is greater than the
        bound but none of the special values described above)
    """
    utils.check_consistency(bound, loop)
    
    ltl_wff = utils.make_nnf_boolean_wff(prop_node)
    be_ptr  = _bmc.Bmc_Tableau_GetLtlTableau(fsm._ptr, ltl_wff._ptr, bound,loop)
    return Be(be_ptr, fsm.encoding.manager)

def bounded_semantics_without_loop(fsm, prop_node, bound):
    """
    Generates a Be expression corresponding to the bounded semantics of the
    given LTL formula in the case where the formula is evaluated against paths 
    that contain no loop and have a maximal length of `bound`.
    
    .. note::
    
        This function proves to be very useful since the bounded semantics of
        LTL depends on two cases: (a) when the encountered path contains loops
        (in that case the unbounded semantics of LTL can be maintained since
        there exists infinite paths) and (b) the case where there are no 
        possible loops (and the semantics has to be altered slightly).
        
        In the literature, the expression generated by this function is denoted
        :math:`[[f]]^{0}_{k}`
        
        With f used to represent the formula `prop_node`, and k for `bound`
    
    .. note::
    
        Fairness is taken into account in the generation of the resulting 
        expression
     
    :param fsm: the fsm against which the formula will be evaluated. It is not
        directly relevant to the generation of the formula for `prop_node` but
        is used to determine to generate fairness constraints for this model
        which are combined with `prop_node` constraint.
    :param prop_node: the property for which to generate a verification problem
        represented in a 'node' format (subclass of :class:`pynusmv.node.Node`)
        which corresponds to the format obtained from the ast.(remark: if you
        need to manipulate [ie negate] the formula before passing it, it is
        perfectly valid to pass a node decorated by `Wff.decorate`).
    :param bound: the bound of the problem, that is to say the maximum number of 
        times the problem will be unrolled. This parameter corresponds to the 
        value `k` used in the formal definitions of a bmc problem.
        
    :return: a boolean expression corresponding to the bounded semantics of 
        `prop_node` in the case where there is no loop on the path.
    :raises ValueError: when the specified problem bound is negative
    """
    if bound < 0:
        raise ValueError("The problem bound may not be negative")
    ltl_wff = utils.make_nnf_boolean_wff(prop_node)
    be_ptr  = _bmc.Bmc_Tableau_GetNoLoop(fsm._ptr, ltl_wff._ptr, bound)
    return Be(be_ptr, fsm.encoding.manager)

def bounded_semantics_single_loop(fsm, prop_node, bound, loop):
    """
    Generates a Be expression corresponding to the bounded semantics of the
    given LTL formula in the case where the formula is evaluated against a path 
    that contains one single loop starting at position `loop`.
    
    In the literature, the resulting formula would be denoted as :math:`{}_{l}L_{k} \\wedge {}_{l}[[f]]_{k}^{0}`
        
    where l is used to denote `loop`, f for `prop_node` and k for the `bound`.
    
    In other words, the generated boolean expression is the conjunction of the
    constraint imposing that there be a k-l loop from `bound` to `loop` and that
    the formula is evaluated at time 0 out of `bound`.
    
    .. note::
    
        Fairness is taken into account in the generation of the resulting 
        expression
        
    :param fsm: the fsm against which the formula will be evaluated. It is not
        directly relevant to the generation of the formula for `prop_node` but
        is used to determine to generate fairness constraints for this model
        which are combined with `prop_node` constraint.
    :param prop_node: the property for which to generate a verification problem
        represented in a 'node' format (subclass of :class:`pynusmv.node.Node`)
        which corresponds to the format obtained from the ast.(remark: if you
        need to manipulate [ie negate] the formula before passing it, it is
        perfectly valid to pass a node decorated by `Wff.decorate`).
    :param bound: the bound of the problem, that is to say the maximum number of 
        times the problem will be unrolled. This parameter corresponds to the 
        value `k` used in the formal definitions of a bmc problem.
        
    :return: a boolean expression corresponding to the bounded semantics of 
        `prop_node` in the case where there is a loop from bound to loop 
    :raises ValueError: when the bound is infeasible (negative value) or when
        the loop and bound values are inconsistent (loop is greater than the
        bound but none of the special values described above)
    """
    utils.check_consistency(bound, loop)
    
    ltl_wff= utils.make_nnf_boolean_wff(prop_node)
    be_ptr = _bmc.Bmc_Tableau_GetSingleLoop(fsm._ptr, ltl_wff._ptr, bound, loop)
    return Be(be_ptr, fsm.encoding.manager)

def bounded_semantics_all_loops_optimisation_depth1(fsm, prop_node, bound):
    """
    Generates a Be expression corresponding to the bounded semantics of the
    given LTL formula in the case where the formula is evaluated against a path 
    that contains a loop at any of the positions in the range [0; bound] and 
    *the 'depth'(:attr:`pynusmv.wff.Wff.depth`) of the formula is 1 and no fairness 
    constraint comes into play*.
    
    .. note::
    
        Unless you know precisely why you are using this function, it is 
        probably safer to just use bounded_semantics_all_loops with the 
        optimized flag turned on.
            
    :param fsm: the fsm against which the formula will be evaluated. It is not
        directly relevant to the generation of the formula for `prop_node` but
        is used to determine to generate fairness constraints for this model
        which are combined with `prop_node` constraint.
    :param prop_node: the property for which to generate a verification problem
        represented in a 'node' format (subclass of :class:`pynusmv.node.Node`)
        which corresponds to the format obtained from the ast.(remark: if you
        need to manipulate [ie negate] the formula before passing it, it is
        perfectly valid to pass a node decorated by `Wff.decorate`).
    :param bound: the bound of the problem, that is to say the maximum number of 
        times the problem will be unrolled. This parameter corresponds to the 
        value `k` used in the formal definitions of a bmc problem.
        
    :return: a boolean expression corresponding to the bounded semantics of 
        `prop_node` in the case where there is may be a loop anywhere on the 
        path between the positions `loop` and `bound` and the formula has a 
        depth of exactly one.
    :raises ValueError: when the specified propblem bound is negative
    """
    if bound < 0:
        raise ValueError("The problem bound may not be negative")
    ltl_wff= utils.make_nnf_boolean_wff(prop_node)
    be_ptr = _bmc.Bmc_Tableau_GetAllLoopsDepth1(fsm._ptr, ltl_wff._ptr, bound)
    return Be(be_ptr, fsm.encoding.manager)

def bounded_semantics_all_loops(fsm, prop_node, bound, loop, optimized=True):
    """
    Generates a Be expression corresponding to the bounded semantics of the
    given LTL formula in the case where the formula is evaluated against a path 
    that contains a loop at any of the positions in the range [loop; bound]
    
    In the literature, the resulting formula would be denoted as 
    
    .. math::
    
        \\bigvee_{j=l}^{k} {}_{j}L_{k} \\wedge {}_{j}[[f]]_{k}^{0}
        
    where l is used to denote `loop`, f for `prop_node` and k for the `bound`.
        
    .. note::
    
        Fairness is taken into account in the generation of the resulting 
        expression
        
    :param fsm: the fsm against which the formula will be evaluated. It is not
        directly relevant to the generation of the formula for `prop_node` but
        is used to determine to generate fairness constraints for this model
        which are combined with `prop_node` constraint.
    :param prop_node: the property for which to generate a verification problem
        represented in a 'node' format (subclass of :class:`pynusmv.node.Node`)
        which corresponds to the format obtained from the ast.(remark: if you
        need to manipulate [ie negate] the formula before passing it, it is
        perfectly valid to pass a node decorated by `Wff.decorate`).
    :param bound: the bound of the problem, that is to say the maximum number of 
        times the problem will be unrolled. This parameter corresponds to the 
        value `k` used in the formal definitions of a bmc problem.
    :param optimized: a flag indicating whether or not the use of the 
        optimisation for formulas of depth 1 is desired.
        
    :return: a boolean expression corresponding to the bounded semantics of 
        `prop_node` in the case where there is may be a loop anywhere on the 
        path between the positions `loop` and `bound`
    :raises ValueError: when the bound is infeasible (negative value) or when
        the loop and bound values are inconsistent (loop is greater than the
        bound but none of the special values described above) 
    """
    utils.check_consistency(bound, loop)
    
    ltl_wff= utils.make_nnf_boolean_wff(prop_node)
    
    if  optimized and ltl_wff.depth == 1 and len(fsm.fairness_list) == 0:
        return bounded_semantics_all_loops_optimisation_depth1(fsm, prop_node, bound)
    else:
        be_ptr = _bmc.Bmc_Tableau_GetAllLoops(fsm._ptr, ltl_wff._ptr, bound, loop)
        return Be(be_ptr, fsm.encoding.manager)
    
   
###############################################################################
############ Offset-ed Bounded semantics of a formula #########################
###############################################################################
def car(this_node):
    """
    Returns the lhs branch of this node. 

    .. note::

        This is a simple workaround of `Node.car` which does not behave as expected.

    :param this_node: the node whose lhs (car) is wanted.
    :return: the lhs member of this node.
    """
    return Node.from_ptr(_node.car(this_node._ptr))

def cdr(this_node):
    """
    Returns the rhs branch of this node. 

    .. note::

        This is a simple workaround of `Node.cdr` which does not behave as expected.

    :param this_node: the node whose rhs (cdr) is wanted.
    :return: the rhs member of this node.
    """
    return Node.from_ptr(_node.cdr(this_node._ptr))

def bounded_semantics_without_loop_at_offset(fsm, formula, time, bound, offset):
    """
    Generates the Be :math:`[[formula]]^{time}_{bound}` corresponding to the bounded semantic 
    of `formula` when there is no loop on the path but encodes it with an `offset` long shift 
    in the timeline of the encoder.

    .. note::
    
        This code was first implemented in Python with PyNuSMV but, since
        the Python implementation proved to be a huge performance bottleneck
        (profiling revealed that useless memory management was dragging the
        whole system behind), it has been translated back to C to deliver much
        better perf. results.

    .. note:: 

        This function plays the same role as `bounded_semantics_without_loop` but allows to 
        position the time blocks at some place we like in the encoder timeline. This is mostly
        helpful if you want to devise verification methods that need to have multiple parallel
        verifications. (ie. diagnosability).

        Note however, that the two implementations are different.

    .. warning::

        So far, the only supported temporal operators are F, G, U, R, X

    :param fsm: the BeFsm for which the property will be verified. Actually, it is only used to 
        provide the encoder used to assign the variables to some time blocks. The api was kept 
        this ways to keep uniformity with its non-offsetted counterpart.
    :param formula: the property for which to generate a verification problem
        represented in a 'node' format (subclass of :class:`pynusmv.node.Node`)
        which corresponds to the format obtained from the ast. (remark: if you
        need to manipulate [ie negate] the formula before passing it, it is
        perfectly valid to pass a node decorated by `Wff.decorate`).
    :param time: the logical time at which the semantics is to be evaluated. (Leave out the offset for
        this param. If you intend the 3rd state of a trace, say time 2).
    :param bound: the logical time bound to the problem. (Leave out the offset for this param: if you
        intend to have a problem with at most 10 steps, say bound=10)
    :param offset: the time offset in the encoding block where the sem of this formula will be 
        generated.
    :return: a Be corresponding to the semantics of `formula` at `time` for a problem with a maximum
        of `bound` steps encoded to start at time `offset` in the `fsm` encoding timeline.
    """
    if time < 0:
        raise ValueError("Time must be a positive integer")
    if bound< 0:
        raise ValueError("Bound must be a positive integer")
    if offset<0:
        raise ValueError("The offset must be a positive integer")
    
    # Note: this code was first implemented in Python with PyNuSMV but, since
    #       the Python implementation proved to be a huge performance bottleneck
    #       (profiling revealed that useless memory management was dragging the
    #       whole system behind).
    _ptr = _lower.sem_no_loop_offset(fsm._ptr, formula._ptr, time, bound, offset)
    return Be(_ptr, fsm.encoding.manager)

def bounded_semantics_with_loop_at_offset(fsm, formula, time, bound, loop, offset):
    """
    Generates the Be :math:`{}_{loop}[[formula]]^{time}_{bound}` corresponding to the bounded semantic 
    of `formula` when a loop starts at time 'loop' on the path but encodes it with an `offset`
    long shift in the timeline of the encoder.
    
    .. note::
    
        This code was first implemented in Python with PyNuSMV but, since
        the Python implementation proved to be a huge performance bottleneck
        (profiling revealed that useless memory management was dragging the
        whole system behind), it has been translated back to C to deliver much
        better perf. results.

    .. note:: 

        This function plays the same role as `bounded_semantics_with_loop` but allows to 
        position the time blocks at some place we like in the encoder timeline. This is mostly
        helpful if you want to devise verification methods that need to have multiple parallel
        verifications. (ie. diagnosability).

        Note however, that the two implementations are different.

    .. warning::

        So far, the only supported temporal operators are F, G, U, R, X

    :param fsm: the BeFsm for which the property will be verified. Actually, it is only used to 
        provide the encoder used to assign the variables to some time blocks. The api was kept 
        this ways to keep uniformity with its non-offsetted counterpart.
    :param formula: the property for which to generate a verification problem
        represented in a 'node' format (subclass of :class:`pynusmv.node.Node`)
        which corresponds to the format obtained from the ast. (remark: if you
        need to manipulate [ie negate] the formula before passing it, it is
        perfectly valid to pass a node decorated by `Wff.decorate`).
    :param time: the logical time at which the semantics is to be evaluated. (Leave out the offset for
        this param. If you intend the 3rd state of a trace, say time 2).
    :param bound: the logical time bound to the problem. (Leave out the offset for this param: if you
        intend to have a problem with at most 10 steps, say bound=10)
    :param loop: the logical time at which a loop starts on the path. (Leave out the offset for this
        param. If you intend to mean that loop starts at 2nd state of the trace, say loop=2)
    :param offset: the time offset in the encoding block where the sem of this formula will be 
        generated.
    :return: a Be corresponding to the semantics of `formula` at `time` for a problem with a maximum
        of `bound` steps encoded to start at time `offset` in the `fsm` encoding timeline.
    """
    if time < 0:
        raise ValueError("Time must be a positive integer")
    if bound< 0:
        raise ValueError("Bound must be a positive integer")
    if offset<0:
        raise ValueError("The offset must be a positive integer")
    if loop < 0:
        raise ValueError("The loop must be a positive integer")
    if loop > bound:
        raise ValueError("The loop must start BEFORE the bound is reached")
    
    # Note: this code was first implemented in Python with PyNuSMV but, since
    #       the Python implementation proved to be a huge performance bottleneck
    #       (profiling revealed that useless memory management was dragging the
    #       whole system behind).
    _ptr = _lower.sem_with_loop_offset(fsm._ptr, formula._ptr, time, bound, loop, offset)
    return Be(_ptr, fsm.encoding.manager)
    
def bounded_semantics_at_offset(fsm, formula, bound, offset, fairness=True):
    """
    Generates the Be :math:`[[formula]]_{bound}` corresponding to the bounded semantic 
    of `formula` but encodes it with an `offset` long shift in the timeline of the encoder.

    .. note:: 

        This function plays the same role as `bounded_semantics_all_loops` but allows to 
        position the time blocks at some place we like in the encoder timeline. This is mostly
        helpful if you want to devise verification methods that need to have multiple parallel
        verifications. (ie. diagnosability).

        Note however, that the two implementations are different.

    .. warning::

        So far, the only supported temporal operators are F, G, U, R, X

    :param fsm: the BeFsm for which the property will be verified. Actually, it is only used to 
        provide the encoder used to assign the variables to some time blocks. The api was kept 
        this ways to keep uniformity with its non-offsetted counterpart.
    :param formula: the property for which to generate a verification problem
        represented in a 'node' format (subclass of :class:`pynusmv.node.Node`)
        which corresponds to the format obtained from the ast. (remark: if you
        need to manipulate [ie negate] the formula before passing it, it is
        perfectly valid to pass a node decorated by `Wff.decorate`).
    :param bound: the logical time bound to the problem. (Leave out the offset for this param: if you
        intend to have a problem with at most 10 steps, say bound=10)
    :param offset: the time offset in the encoding block where the sem of this formula will be 
        generated.
    :param fairness: a flag indicating whether or not to take the fairness 
        constraint into account.
    :return: a Be corresponding to the semantics of `formula` for a problem with a maximum of `bound` 
        steps encoded to start at time `offset` in the `fsm` encoding timeline.
    """
    if bound< 0:
        raise ValueError("Bound must be a positive integer")
    if offset<0:
        raise ValueError("The offset must be a positive integer")
    
    enc = fsm.encoding
    straight = bounded_semantics_without_loop_at_offset(fsm, formula, 0, bound, offset)
    k_loop   = Be.false(enc.manager)
    for i in range(bound): 
        fairness_cond = utils.fairness_constraint(fsm, offset+bound, offset+i) \
                                 if fairness \
                                 else Be.true(enc.manager)
        k_loop |= ( utils.loop_condition(enc, offset+bound, offset+i) \
                  & fairness_cond \
                  & bounded_semantics_with_loop_at_offset(fsm, formula, 0, bound, i, offset))
    
    # this is just the sem of the formula
    return straight | k_loop    
##############################################################################
# DUMP 
##############################################################################
def dump_dimacs_filename(be_enc, be_cnf, bound, fname):
    """
    Opens a new file named filename, then dumps the given LTL problem in DIMACS 
    format
    
    .. note::
        
        The bound of the problem is used only to generate a the readable 
        version of the mapping table as comment at beginning of the file.
    
    .. note::
        
        Calling this function is strictly equivalent to the following snippet::
        
            with StdioFile.for_name(fname) as f:
                dump_dimacs(be_enc, be_cnf, bound, f.handle)
    
    :param be_enc: the encoding of the problem (typically fsm.encoding)
    :param be_cnf: the LTL problem represented in CNF
    :param  bound: the bound of the problem
    :param  fname: the name of the file in which to dump the DIMACS output.
    """
    _bmc.Bmc_Dump_DimacsProblemFilename(be_enc._ptr, 
                                        be_cnf._ptr,
                                        fname, 
                                        bound)

def dump_dimacs(be_enc, be_cnf, bound, stdio_file):
    """
    Dumps the given LTL problem in DIMACS format to the designated `stdio_file`
    
    .. note::
        
        The bound of the problem is used only to generate a the readable 
        version of the mapping table as comment at beginning of the file.
    
    
    :param be_enc: the encoding of the problem (typically fsm.encoding)
    :param be_cnf: the LTL problem represented in CNF
    :param  bound: the bound of the problem
    :param stdio_file: the the file in which to dump the DIMACS output.
    """
    _bmc.Bmc_Dump_DimacsProblem(be_enc._ptr, 
                                be_cnf._ptr,
                                bound, 
                                stdio_file.handle)
