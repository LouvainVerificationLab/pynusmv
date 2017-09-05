.. _tutorial:

Tutorial
********

This page presents a short overview of PyNuSMV capabilities with a small example. It then goes deeper into these capabilities and explains how to use them.

.. contents:: Contents
    :local:

Getting started
===============

Let's consider the following SMV model. This model is composed of two counters, incrementing from 0 to 3, and looping. They run asynchronously and the running one is defined at each step by the ``run`` action.

.. include:: models/counters.smv
    :literal:


Considering that the model is saved in the ``counters.smv`` file in the current directory, we can now run Python. 
The following Python session shows the basics of PyNuSMV. After importing pynusmv, the function :func:`init_nusmv <pynusmv.init.init_nusmv>` **must** be called before calling any other PyNuSMV functionality. The function :func:`deinit_nusmv <pynusmv.init.deinit_nusmv>` must also be called after using PyNuSMV to release all resources hold by NuSMV. After initializing PyNuSMV, the model is read with the function :func:`load_from_file <pynusmv.glob.load_from_file>` and the model is computed, that is, flattened and encoded into BDDs, with the function :func:`compute_model <pynusmv.glob.compute_model>`.


>>> import pynusmv
>>> pynusmv.init.init_nusmv()
>>> pynusmv.glob.load_from_file("counters.smv")
>>> pynusmv.glob.compute_model()
>>> pynusmv.init.deinit_nusmv()


Another way to initialize and release NuSMV resources is to use the result of the :func:`init_nusmv <pynusmv.init.init_nusmv>` function as a context with the `with` statement. The following code is equivalent to the one above:


>>> import pynusmv
>>> with pynusmv.init.init_nusmv():
...     pynusmv.glob.load_from_file("counters.smv")
...     pynusmv.glob.compute_model()

All NuSMV resources are automatically released when the context is exited.


The next Python session shows functionalities of FSMs, access to specifications of the model, calls to CTL model checking and manipulation of BDDs. First, NuSMV is initialized and the model is read. Then the model encoded with BDDs is retrieved from the main propositions database. The first (and only) proposition is then retrieved from the same database, and the specification of this proposition is isolated.

From the BDD-encoded FSM ``fsm`` and the specification ``spec``, we call the :func:`eval_ctl_spec <pynusmv.mc.eval_ctl_spec>` function to get all the states of ``fsm`` satisfying ``spec``. Conjuncted with the set of reachables states of the model, we get ``bdd``, a BDD representing all the reachable states of ``fsm`` satisfying ``spec``. Finally, from this BDD we extract all the single states and display them, that is, we display, for each of them, the value of each state variable of the model.


>>> import pynusmv
>>> pynusmv.init.init_nusmv()
>>> pynusmv.glob.load_from_file("counters.smv")
>>> pynusmv.glob.compute_model()
>>> fsm = pynusmv.glob.prop_database().master.bddFsm
>>> fsm
<pynusmv.fsm.BddFsm object at 0x1016d9e90>
>>> prop = pynusmv.glob.prop_database()[0]
>>> prop
<pynusmv.prop.Prop object at 0x101770250>
>>> spec = prop.expr
>>> print(spec)
AF c1.c = stop - 1
>>> bdd = pynusmv.mc.eval_ctl_spec(fsm, spec) & fsm.reachable_states
>>> bdd
<pynusmv.dd.BDD object at 0x101765a90>
>>> satstates = fsm.pick_all_states(bdd)
>>> for state in satstates:
...     print(state.get_str_values())
... 
{'c1.c': '2', 'c2.c': '2', 'stop': '3', 'start': '0'}
{'c1.c': '2', 'c2.c': '0', 'stop': '3', 'start': '0'}
{'c1.c': '2', 'c2.c': '1', 'stop': '3', 'start': '0'}
>>> pynusmv.init.deinit_nusmv()


This (very) short tutorial showed the main functionalities of PyNuSMV. More of them are available, such as functionalities to parse and evaluate a simple expression, to build new CTL specifications, or to perform operations on BDDs. The rest of this page gives more details on these functionalities; the :ref:`full documentation <pynusmv-api>` of the library is also given beside this tutorial.


Defining and loading a model
============================

As explained above, a model can be defined in SMV format and loaded into PyNuSMV through a file. PyNuSMV also provides a set of classes in the :mod:`model <pynusmv.model>` module to define an SMV model directly in Python. For instance, the two-counter model above can befined with ::

    from pynusmv.model import *

    class counter(Module):
        COMMENT = """
            A modulo counter
            Go from start (inclusive) to stop (exclusive) by 1-increments
            Run only when run is true
        """
        run, start, stop = (Identifier(id_) for id_ in ("run", "start", "stop"))
        ARGS = [run, start, stop]
        c = Var(Range(start, stop))
        INIT = [c == start]
        TRANS = [c.next() == (Case(((run, Case((((c + 1) == stop, start),
                                                (Trueexp(), c + 1)))),
                                    (~run, c))))]

    class main(Module):
        start = Def(0)
        stop = Def(3)
        run = IVar(Scalar(("rc1", "rc2")))
        c1 = Var(counter(run == "rc1", start, stop))
        c2 = Var(counter(run == "rc2", start, stop))

    print(counter)
    print(main)

This prints the following ::

    -- A modulo counter
    -- Go from start (inclusive) to stop (exclusive) by 1-increments
    -- Run only when run is true
    MODULE counter(run, start, stop)
        VAR
            c: start .. stop;
        INIT
            c = start
        TRANS
            next(c) =
            case
                run:
                case
                    c + 1 = stop: start;
                    TRUE: c + 1;
                esac;
                ! run: c;
            esac
    MODULE main
        DEFINE
            start := 0;
            stop := 3;
        IVAR
            run: {rc1, rc2};
        VAR
            c1: counter(run = rc1, start, stop);
            c2: counter(run = rc2, start, stop);

Note that SMV state and input variables can be declared as members of the ``Module`` sub-class defining the module by instantiating :class:`Var <pynusmv.model.Var>` and :class:`IVar <pynusmv.model.IVar>` classes. The argument to the constructor is the type of the variable, and can be either a primitive one (:class:`Range <pynusmv.model.Range>`, :class:`Boolean <pynusmv.model.Boolean>`, etc.), or instances of another module. All these instantiated objects can then be used as identifiers everywhere in the module definition.

The different sections of an SMV module are declared as members with special names such as ``INIT``, ``TRANS``, or ``ASSIGN``. Some must be iterables (such as ``INIT`` and ``TRANS``), others must be mappings (such as ``ASSIGN``).

The :mod:`model module <pynusmv.model>` supports a large variety of classes to define all concepts in SMV modules. For instance, in the code above, we can write ``c1.c`` for the ``c`` variable of the ``c1`` instance. Standard arithmetic operations such as additions are supported by SMV expressions, as shown with ``c + 1`` above.

Another way to produce a Python-defined NuSMV model is to parse an existing SMV model (as a string or as a file) with the :mod:`parser <pynusmv.parser>` module functionalities. It contains the :func:`parseAllString <pynusmv.parser.parseAllString>` function to parse a string according to a pre-defined parser. Several parsers are provided to parse identifiers (:data:`parser.identifier <pynusmv.parser.identifier>`), expressions (:data:`parser.next_expression <pynusmv.parser.next_expression>`), modules (:data:`parser.module <pynusmv.parser.module>`), etc.

The defined modules can then be loaded in PyNuSMV in a similar way to SMV files::

    import pynusmv
    pynusmv.init.init_nusmv()
    pynusmv.glob.load(counter, main)

This :func:`load <pynusmv.glob.load>` function accepts either sub-classes of :class:`Module <pynusmv.model.Module>`, a single path to an SMV file, or a string containing the definition of the model. Once the model is loaded, the corresponding internal data structures such as the BDD-encoded finite-state machine can be built with ::

    pynusmv.glob.compute_model()

This :func:`compute_model <pynusmv.glob.compute_model>` function accepts the path to a file containing the BDD variable order to use for building the BDD FSM, and whether or not single enumerations should be kept as they are, or converted into defines. Once the model is built, the BDD-encoded FSM can be accessed via ::

    fsm = pynusmv.glob.prop_database().master.bddFsm


Manipulating BDDs
=================

The BDD-encoded finite-state machine representing the SMV model is an instance of the :class:`BddFsm <pynusmv.fsm.BddFsm>` class. It gives access to the parts of this model: the BDD representing the initial states (``fsm.init``), its reachable states (``fsm.reachable_states``), etc.
It also allows us to pick one particular state from a given BDD-encoded set of states with the :meth:`pick_one_state <pynusmv.fsm.BddFsm.pick_one_state>` method, or to count the input values contained in one BDD::

    print(fsm.count_states(fsm.init))
    for state in fsm.pick_all_states(fsm.init):
        print(state.get_str_values())

prints ::

    1
    {'stop': '3', 'c1.c': '0', 'start': '0', 'c2.c': '0'}

The :class:`BddFsm <pynusmv.fsm.BddFsm>` class also gives access to the transition relation (``fsm.trans``) and the :meth:`pre <pynusmv.fsm.BddFsm.pre>` and :meth:`post <pynusmv.fsm.BddFsm.post>` methods returning the pre- and post-images of given states::

    for state in fsm.pick_all_states(fsm.post(fsm.init)):
        print(state.get_str_values())

prints ::

    {'stop': '3', 'c1.c': '0', 'start': '0', 'c2.c': '1'}
    {'stop': '3', 'c1.c': '1', 'start': '0', 'c2.c': '0'}

The transition relation is an instance of the :class:`BddTrans <pynusmv.fsm.BddTrans>` class and can be modified. Several transition relations can also co-exist, separately from the FSM itself.

The BDD-encoded FSM can also return the BDD encoder :class:`BddEnc <pynusmv.fsm.BddEnc>` (through ``fsm.bddEnc``) that keeps track of how the model variables are encoded into BDD variables.
This encoder gives access to masks (:meth:`BddEnc.inputsMask <pynusmv.fsm.BddEnc.inputsMask>` for instance) representing all valid values for input variables. It also gives access to cubes (:meth:`BddEnc.statesCube <pynusmv.fsm.BddEnc.statesCube>` for instance) and can produce cubes for particular state or input variables (via :meth:`BddEnc.cube_for_inputs_vars <pynusmv.fsm.BddEnc.cube_for_inputs_vars>` for instance). Finally, it gives access to the set of declared variables and the current order of BDD variables used for building BDDs::

    enc = fsm.bddEnc
    print(enc.stateVars)
    print(enc.inputsVars)

prints ::

    frozenset({'c1.c', 'c2.c'})
    frozenset({'run'})

The BDD encoder also gives access to the symbols table that is used to store the symbols of the model (``bddEnc.symbTable``). This :class:`SymbTable <pynusmv.fsm.SymbTable>` can be used to declare new variables and to encode them into BDD variables.

Most of the parts of the FSM, such as the initial and reachable states, or the masks and cubes returned by the BDD encoder, are encoded into BDDs. These BDDs are instances of the :class:`BDD <pynusmv.dd.BDD>` class, that provides several operations on BDDs. For instance, ::

    fsm.reachable_states & fsm.fair_states

computes the conjunct of both BDDs, getting the fair reachable states of the model. Most common BDD operations are provided as builtin operators, such as disjunction (``|``), conjunction (``&``), negation (``~``). These BDDs also support comparison, and the class also provides a way to build the ``True`` and ``False`` canonical BDDs with ``BDD.true()`` and ``BDD.false()``, respectively.
Finally, the :mod:`dd <pynusmv.dd>` module contains some function to enable or disable BDD variable reordering::

    pynusmv.dd.enable_dynamic_reordering()


Defining properties
===================

A NuSMV property ``prop`` is a structure containing useful information about a given specification: its type ``prop.type`` (LTL or CTL specification, etc.), its name ``prop.name``, its actual temoral-logic formula ``prop.expr``, its status ``prop.status`` (unchecked, true, false), etc. These properties are represented in PyNuSMV with :class:`Prop <pynusmv.prop.Prop>` instances. They come from a property database (:class:`PropDb <pynusmv.prop.PropDb>`) built and populated by NuSMV. The property database associated to the model built by NuSMV can be obtained through the :mod:`glob <pynusmv.glob>` module::

    prop_db = pynusmv.glob.prop_database()

once the model has been built with :func:`compute_model <pynusmv.glob.compute_model()>`. The property database contains all properties defined beside the loaded model, such as the specification ``AF c1.c = stop - 1`` defined in the ``counters.smv`` model at the beginning of this tutorial. It acts as an iterable.

Property expressions ``spec`` are instances of the :class:`Spec <pynusmv.prop.Spec>` class. They reflect NuSMV internal structures, so they have a type ``spec.type``, a left child ``spec.car`` and a right child ``spec.cdr`` (both can be ``None``, depending on the type of the expression). New specifications can be defined thanks to :mod:`prop <pynusmv.prop>` module functions such as atomic propositions with the :func:`atom <pynusmv.prop.atom>` function, Boolean operators (``&``, ``|``, etc.), CTL operators (:func:`ag <pynusmv.prop.ag>`, :func:`ef <pynusmv.prop.ef>`, etc.), and LTL ones (:func:`x <pynusmv.prop.x>`, :func:`u <pynusmv.prop.u>`, etc.) For instance, the specification ``AF c1.c = stop - 1`` can be obtained with ::

    from pynusmv import prop
    spec = prop.af(prop.atom("c1.c = stop - 1"))



Verifying properties
====================



