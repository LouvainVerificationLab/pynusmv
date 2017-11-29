"""
The :mod:`pynusmv.mc` module provides some functions of NuSMV dealing with
model checking, like CTL model checking.
"""

__all__ = ['check_ltl_spec', 'check_explain_ltl_spec',
           'check_ctl_spec', 'eval_simple_expression', 'eval_ctl_spec',
           'ef', 'eg', 'ex', 'eu', 'au',
           'explain', 'explainEX', 'explainEU', 'explainEG']


from pynusmv_lower_interface.nusmv.node import node as nsnode
from pynusmv_lower_interface.nusmv.dd import dd as nsdd
from pynusmv_lower_interface.nusmv.mc import mc as nsmc
from pynusmv_lower_interface.nusmv.ltl import ltl as nsltl
from pynusmv_lower_interface.nusmv.prop import prop as nsprop
from pynusmv_lower_interface.nusmv.compile import compile as nscompile
from pynusmv_lower_interface.nusmv.opt import opt as nsopt
from pynusmv_lower_interface.nusmv.fsm.bdd import bdd as nsfsmbdd
from pynusmv_lower_interface.nusmv.enc.bdd import bdd as nsencbdd
from pynusmv_lower_interface.nusmv.compile.symb_table import symb_table as \
                                                             nssymb_table

from .dd import BDD, State, Inputs, BDDList, DDManager, Cube
from .prop import atom, propTypes
from . import glob
from .fsm import BddFsm


def check_ltl_spec(spec):
    """
    Return whether the loaded SMV model satisfies or not the LTL given `spec`.
    That is, return whether all initial states of le model satisfies `spec` or
    not.

    :param spec: a specification
    :type spec: :class:`Spec <pynusmv.prop.Spec>`
    :rtype: bool

    """
    # Check that a model has been compiled
    assert(glob.prop_database().master is not None)
    
    # Create a property from the given spec
    prop = nsprop.Prop_create_partial(spec._ptr, propTypes["LTL"])
    
    # Save settings
    o = nsopt.OptsHandler_get_enum_option_value(
            nsopt.OptsHandler_get_instance(),
            "oreg_justice_emptiness_bdd_algorithm")
    if (nscompile.
            FlatHierarchy_get_compassion(glob.
                                         global_compile_flathierarchy())
            is None and
            o == nsfsmbdd.BDD_OREG_JUSTICE_EMPTINESS_BDD_ALGORITHM_EL_FWD):
        
        saved_options = nsfsmbdd.Bdd_elfwd_check_set_and_save_options(
                            nsfsmbdd.BDD_ELFWD_OPT_ALL)
    else:
        saved_options = None
    
    # Create, build and check the structure for LTL model checking
    ltl_struct = nsltl.Ltl_StructCheckLtlSpec_create(prop)
    nsltl.Ltl_StructCheckLtlSpec_build(ltl_struct)
    nsltl.Ltl_StructCheckLtlSpec_check(ltl_struct)
    
    # Get the result
    result = nsprop.Prop_get_status(prop) == nsprop.Prop_True
    
    # Destroy the intermediate structure
    nsltl.Ltl_StructCheckLtlSpec_destroy(ltl_struct)
    
    # Restore settings
    if saved_options is not None:
        nsfsmbdd.Bdd_elfwd_restore_options(nsfsmbdd.BDD_ELFWD_OPT_ALL,
                                           saved_options)
    
    # Destroy prop
    nsprop.Prop_destroy(prop)
    
    return result


def check_explain_ltl_spec(spec):
    """
    Return whether the loaded SMV model satisfies or not the LTL given `spec`,
    that is, whether all initial states of le model satisfies `spec` or not.
    Return also an explanation for why the model does not satisfy `spec`,
    if it is the case, or `None` otherwise.
    
    The result is a tuple where the first element is a boolean telling whether
    `spec` is satisfied, and the second element is either `None` if the first
    element is `True`, or a path of the SMV model violating `spec` otherwise.
    
    The explanation is a tuple of alternating states and inputs, starting and
    ennding with a state. The path is looping if the last state is somewhere
    else in the sequence. States and inputs are represented by dictionaries
    where keys are state and inputs variable of the loaded SMV model, and
    values are their value.

    :param spec: a specification
    :type spec: :class:`Spec <pynusmv.prop.Spec>`
    :rtype: tuple

    """
    # Check that a model has been compiled
    assert(glob.prop_database().master is not None)
    
    # Create a property from the given spec
    prop = nsprop.Prop_create_partial(spec._ptr, propTypes["LTL"])
    
    # Save settings
    o = nsopt.OptsHandler_get_enum_option_value(
            nsopt.OptsHandler_get_instance(),
            "oreg_justice_emptiness_bdd_algorithm")
    if (nscompile.
            FlatHierarchy_get_compassion(glob.
                                         global_compile_flathierarchy())
            is None and
            o == nsfsmbdd.BDD_OREG_JUSTICE_EMPTINESS_BDD_ALGORITHM_EL_FWD):
        
        saved_options = nsfsmbdd.Bdd_elfwd_check_set_and_save_options(
                            nsfsmbdd.BDD_ELFWD_OPT_ALL)
    else:
        saved_options = None
    
    # Create, build and check the structure for LTL model checking
    ltl_struct = nsltl.Ltl_StructCheckLtlSpec_create(prop)
    nsltl.Ltl_StructCheckLtlSpec_build(ltl_struct)
    nsltl.Ltl_StructCheckLtlSpec_check(ltl_struct)
    
    # Get the result
    result = nsprop.Prop_get_status(prop) == nsprop.Prop_True
    
    # explain
    if not result:
        # Extract explanation
        bdd_fsm = BddFsm(ltl_struct.fsm)
        
        full_fairness = (not nsfsmbdd.FairnessList_is_empty(
                             nsfsmbdd.compassionList2fairnessList(
                             nsfsmbdd.BddFsm_get_compassion(bdd_fsm._ptr))))
        
        # Counterexample construction for forward Emerson-Lei not yet
        # implemented
        assert(full_fairness or not o)

        tmp = BDD(nsencbdd.BddEnc_pick_one_state(ltl_struct.bdd_enc,
                                                 ltl_struct.s0),
                  dd_manager=DDManager(nsencbdd.BddEnc_get_dd_manager(
                                       ltl_struct.bdd_enc)))
        
        if full_fairness:
            exp = BDDList(nsltl.witness(bdd_fsm._ptr,
                                        ltl_struct.bdd_enc,
                                        tmp._ptr),
                          ddmanager=tmp._manager)
        else:
            path = nsnode.cons(nsnode.bdd2node(nsdd.bdd_dup(tmp._ptr)), None)
            exp = BDDList(nsnode.reverse(
                          nsmc.explain(bdd_fsm._ptr,
                                       ltl_struct.bdd_enc,
                                       path,
                                       ltl_struct.spec_formula,
                                       None)),
                          ddmanager=tmp._manager)
        
        if exp is None: # The counterexample consists of one initial state
            exp = BDDList(nsnode.cons(nsnode.bdd2node(nsdd.bdd_dup(tmp._ptr)),
                                      None),
                          ddmanager=tmp._manager)
        exp = exp.to_tuple()

        # removes all the tableau variables from the result before
        # building the resulting trace. This will make simulation
        # working, but may show unexistent loops in the shown trace
        def clean(bdd):
            tableau_cube = Cube(nsencbdd.BddEnc_get_layer_vars_cube(
                                    ltl_struct.bdd_enc,
                                    ltl_struct.tableau_layer,
                                    nssymb_table.VFT_ALL),
                                dd_manager=bdd._manager)
            return bdd.forsome(tableau_cube)
        
        # exp has at least one element
        explanation = [bdd_fsm.pick_one_state(clean(exp[0])).get_str_values()]
        for inputs_bdd, state_bdd in zip(exp[1::2], exp[2::2]):
            explanation.append(bdd_fsm.pick_one_inputs(
                               clean(inputs_bdd))
                               .get_str_values())
            explanation.append(bdd_fsm.pick_one_state(
                               clean(state_bdd))
                               .get_str_values())
    else:
        explanation = None
    
    # Destroy the intermediate structure
    nsltl.Ltl_StructCheckLtlSpec_destroy(ltl_struct)
    
    # Restore settings
    if saved_options is not None:
        nsfsmbdd.Bdd_elfwd_restore_options(nsfsmbdd.BDD_ELFWD_OPT_ALL,
                                           saved_options)
    
    # Destroy prop
    nsprop.Prop_destroy(prop)
    
    return (result, explanation if explanation is None else tuple(explanation))


def check_ctl_spec(fsm, spec, context=None):
    """
    Return whether the given `fsm` satisfies or not the given `spec` in
    `context`, if specified. That is, return whether all initial states of
    `fsm` satisfies `spec` in context or not.

    :param fsm: the concerned FSM
    :type fsm: :class:`BddFsm <pynusmv.fsm.BddFsm>`
    :param spec: a specification about `fsm`
    :type spec: :class:`Spec <pynusmv.prop.Spec>`
    :param context: the context in which evaluate `spec`
    :type context: :class:`Spec <pynusmv.prop.Spec>`
    :rtype: bool

    """
    sat = eval_ctl_spec(fsm, spec, context)
    unsatinit = fsm.init & fsm.state_constraints & fsm.fair_states & ~sat
    return unsatinit.is_false()


def eval_simple_expression(fsm, sexp):
    """
    Return the set of states of `fsm` satisfying `sexp`, as a BDD.
    `sexp` is first parsed, then evaluated on `fsm`.

    :param fsm: the concerned FSM
    :type fsm: :class:`BddFsm <pynusmv.fsm.BddFsm>`
    :param sexp: a simple expression, as a string
    :rtype: :class:`BDD <pynusmv.dd.BDD>`

    """
    return eval_ctl_spec(fsm, atom(sexp))


def eval_ctl_spec(fsm, spec, context=None):
    """
    Return the set of states of `fsm` satisfying `spec` in `context`, as a BDD.

    :param fsm: the concerned FSM
    :type fsm: :class:`BddFsm <pynusmv.fsm.BddFsm>`
    :param spec: a specification about `fsm`
    :type spec: :class:`Spec <pynusmv.prop.Spec>`
    :param context: the context in which evaluate `spec`
    :type context: :class:`Spec <pynusmv.prop.Spec>`
    :rtype: :class:`BDD <pynusmv.dd.BDD>`

    """
    enc = fsm.bddEnc
    specbdd = BDD(nsmc.eval_ctl_spec(fsm._ptr, enc._ptr,
                                     spec._ptr,
                                     context and context._ptr or None),
                  enc.DDmanager, freeit=True)
    return specbdd

def ef(fsm, states):
    """
    Return the set of states of `fsm` satisfying `EF states`, as a BDD.

    :param fsm: the concerned FSM
    :type fsm: :class:`BddFsm <pynusmv.fsm.BddFsm>`
    :param states: a set of states of `fsm`
    :type states: :class:`BDD <pynusmv.dd.BDD>`
    :rtype: :class:`BDD <pynusmv.dd.BDD>`
    """
    return BDD(nsmc.ef(fsm._ptr, states._ptr),
               fsm.bddEnc.DDmanager, freeit=True)

def eg(fsm, states):
    """
    Return the set of states of `fsm` satisfying `EG states`, as a BDD.

    :param fsm: the concerned FSM
    :type fsm: :class:`BddFsm <pynusmv.fsm.BddFsm>`
    :param states: a set of states of `fsm`
    :type states: :class:`BDD <pynusmv.dd.BDD>`
    :rtype: :class:`BDD <pynusmv.dd.BDD>`
    """
    return BDD(nsmc.eg(fsm._ptr, states._ptr),
               fsm.bddEnc.DDmanager, freeit=True)

def ex(fsm, states):
    """
    Return the set of states of `fsm` satisfying `EX states`, as a BDD.

    :param fsm: the concerned FSM
    :type fsm: :class:`BddFsm <pynusmv.fsm.BddFsm>`
    :param states: a set of states of `fsm`
    :type states: :class:`BDD <pynusmv.dd.BDD>`
    :rtype: :class:`BDD <pynusmv.dd.BDD>`
    """
    return BDD(nsmc.ex(fsm._ptr, states._ptr),
               fsm.bddEnc.DDmanager, freeit=True)

def eu(fsm, s1, s2):
    """
    Return the set of states of `fsm` satisfying `E[s1 U s2]`, as a BDD.

    :param fsm: the concerned FSM
    :type fsm: :class:`BddFsm <pynusmv.fsm.BddFsm>`
    :param s1: a set of states of `fsm`
    :type s1: :class:`BDD <pynusmv.dd.BDD>`
    :param s2: a set of states of `fsm`
    :type s2: :class:`BDD <pynusmv.dd.BDD>`
    :rtype: :class:`BDD <pynusmv.dd.BDD>`
    """
    return BDD(nsmc.eu(fsm._ptr, s1._ptr, s2._ptr),
               fsm.bddEnc.DDmanager, freeit=True)

def au(fsm, s1, s2):
    """
    Return the set of states of `fsm` satisfying `A[s1 U s2]`, as a BDD.

    :param fsm: the concerned FSM
    :type fsm: :class:`BddFsm <pynusmv.fsm.BddFsm>`
    :param s1: a set of states of `fsm`
    :type s1: :class:`BDD <pynusmv.dd.BDD>`
    :param s2: a set of states of `fsm`
    :type s2: :class:`BDD <pynusmv.dd.BDD>`
    :rtype: :class:`BDD <pynusmv.dd.BDD>`
    """
    return BDD(nsmc.au(fsm._ptr, s1._ptr, s2._ptr),
               fsm.bddEnc.DDmanager, freeit=True)

def explain(fsm, state, spec, context=None):
    """
    Explain why `state` of `fsm` satisfies `spec` in `context`.

    :param fsm: the system
    :type fsm: :class:`BddFsm <pynusmv.fsm.BddFsm>`
    :param state: a state of `fsm`
    :type state: :class:`State <pynusmv.dd.State>`
    :param spec: a specification about `fsm`
    :type spec: :class:`Spec <pynusmv.prop.Spec>`
    :param context: the context in which evaluate `spec`
    :type context: :class:`Spec <pynusmv.prop.Spec>`

    Return a tuple `t` composed of states (:class:`State <pynusmv.dd.State>`)
    and inputs (:class:`Inputs <pynusmv.dd.Inputs>`),
    such that `t[0]` is `state` and `t` represents a path in `fsm` explaining
    why `state` satisfies `spec` in `context`.
    The returned path is looping if the last state of path is equal to a
    previous state along the path.

    """
    if context is not None:
        context_ptr = context._ptr
    else:
        context_ptr = None

    enc = fsm.bddEnc
    manager = enc.DDmanager
    path = nsnode.cons(nsnode.bdd2node(nsdd.bdd_dup(state._ptr)), None)

    expl = nsmc.explain(fsm._ptr, enc._ptr, path, spec._ptr, context_ptr)
    if expl is None:
        expl = nsnode.cons(nsnode.bdd2node(nsdd.bdd_dup(state._ptr)), None)

    bddlist = BDDList(expl, manager)
    bddlist = bddlist.to_tuple()

    path = []
    path.insert(0, State.from_bdd(bddlist[0], fsm))
    for i in range(1, len(bddlist), 2):
        inputs = Inputs.from_bdd(bddlist[i], fsm)
        state = State.from_bdd(bddlist[i + 1], fsm)

        path.insert(0, inputs)
        path.insert(0, state)

    return tuple(path)

def explainEX(fsm, state, a):
    """
    Explain why `state` of `fsm` satisfies `EX phi`, where `a` is
    the set of states of `fsm` satisfying `phi`, represented by a BDD.

    :param fsm: the system
    :type fsm: :class:`BddFsm <pynusmv.fsm.BddFsm>`
    :param state: a state of `fsm`
    :type state: :class:`State <pynusmv.dd.State>`
    :param a: the set of states of `fsm` satisfying `phi`
    :type a: :class:`BDD <pynusmv.dd.BDD>`

    Return `(s, i, s')` tuple where `s` (:class:`State <pynusmv.dd.State>`)
    is the given state, `s'` (:class:`State <pynusmv.dd.State>`) is a successor
    of `s` belonging to `a` and `i` (:class:`Inputs <pynusmv.dd.Inputs>`)
    is the inputs to go from `s` to `s'` in `fsm`.

    """
    enc = fsm.bddEnc
    manager = enc.DDmanager
    path = nsnode.cons(nsnode.bdd2node(nsdd.bdd_dup(state._ptr)), None)
    bddlist = BDDList(nsmc.ex_explain(fsm._ptr, enc._ptr, path, a._ptr),
                      manager)

    # bddlist is reversed!
    statep = State.from_bdd(bddlist[0], fsm)
    inputs = Inputs.from_bdd(bddlist[1], fsm)
    state = State.from_bdd(bddlist[2], fsm)

    return (state, inputs, statep)


def explainEU(fsm, state, a, b):
    """
    Explain why `state` of `fsm` satisfies `E[phi U psi]`,
    where `a is the set of states of `fsm` satisfying `phi`
    and `b` is the set of states of `fsm` satisfying `psi`, both represented
    by BDDs.

    :param fsm: the system
    :type fsm: :class:`BddFsm <pynusmv.fsm.BddFsm>`
    :param state: a state of `fsm`
    :type state: :class:`State <pynusmv.dd.State>`
    :param a: the set of states of `fsm` satisfying `phi`
    :type a: :class:`BDD <pynusmv.dd.BDD>`
    :param b: the set of states of `fsm` satisfying `psi`
    :type b: :class:`BDD <pynusmv.dd.BDD>`

    Return a tuple `t` composed of states (:class:`State <pynusmv.dd.State>`)
    and inputs (:class:`Inputs <pynusmv.dd.Inputs>`),
    such that `t[0]` is `state`, `t[-1]` belongs to `b`, and every other state
    of `t` belongs to `a`. The states of `t` are separated by inputs.
    Furthermore, `t` represents a path in `fsm`.

    """
    enc = fsm.bddEnc
    manager = enc.DDmanager
    path = nsnode.cons(nsnode.bdd2node(nsdd.bdd_dup(state._ptr)), None)
    bddlist = BDDList(nsmc.eu_explain(fsm._ptr, enc._ptr,
                                      path, a._ptr, b._ptr), manager)
    bddlist = bddlist.to_tuple()

    path = []
    path.insert(0, State.from_bdd(bddlist[0], fsm))
    for i in range(1, len(bddlist), 2):
        inputs = Inputs.from_bdd(bddlist[i], fsm)
        state = State.from_bdd(bddlist[i + 1], fsm)

        path.insert(0, inputs)
        path.insert(0, state)

    return tuple(path)


def explainEG(fsm, state, a):
    """
    Explain why `state` of `fsm` satisfies `EG phi`, where `a` the set of
    states of `fsm` satisfying `phi`, represented by a BDD.

    :param fsm: the system
    :type fsm: :class:`BddFsm <pynusmv.fsm.BddFsm>`
    :param state: a state of `fsm`
    :type state: :class:`State <pynusmv.dd.State>`
    :param a: the set of states of `fsm` satisfying `phi`
    :type a: :class:`BDD <pynusmv.dd.BDD>`

    Return a tuple `(t, (i, loop))`
    where `t` is a tuple composed of states (:class:`State <pynusmv.dd.State>`)
    and inputs (:class:`Inputs <pynusmv.dd.Inputs>`),
    such that `t[0]` is state and every other state of `t`
    belongs to `a`. The states of `t` are separated by inputs.
    Furthermore, `t` represents a path in `fsm`.
    `loop` represents the start of the loop contained in `t`,
    i.e. `t[-1]` can lead to `loop` through `i`, and `loop` is a state of `t`.

    """
    enc = fsm.bddEnc
    manager = enc.DDmanager
    path = nsnode.cons(nsnode.bdd2node(nsdd.bdd_dup(state._ptr)), None)
    bddlist = BDDList(nsmc.eg_explain(fsm._ptr, enc._ptr, path, a._ptr),
                      manager)
    bddlist = bddlist.to_tuple()

    path = []
    # Discard last state and input, store them as loop indicators
    loopstate = State.from_bdd(bddlist[0], fsm)
    loopinputs = Inputs.from_bdd(bddlist[1], fsm)

    # Consume first state
    curstate = State.from_bdd(bddlist[2], fsm)
    if curstate._ptr == loopstate._ptr:
        loopstate = curstate

    path.insert(0, curstate)

    for i in range(3, len(bddlist), 2):
        inputs = Inputs.from_bdd(bddlist[i], fsm)
        curstate = State.from_bdd(bddlist[i + 1], fsm)
        if curstate._ptr == loopstate._ptr:
            loopstate = curstate

        path.insert(0, inputs)
        path.insert(0, curstate)
    return (tuple(path), (loopinputs, loopstate))
