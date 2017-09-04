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

As explained above, a model can be defined in SMV format and loaded into PyNuSMV through a file. PyNuSMV also provides a set of classes in the :mod:`model module <pynusmv.model>` to define an SMV model directly in Python. For instance, the two-counter model above can befined with ::

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

Note that SMV state and input variables can be declared as members of the `Module` sub-class defining the module by instantiating :class:`Var <pynusmv.model.Var>` and :class:`IVar <pynusmv.model.IVar>` classes. The argument to the constructor is the type of the variable, and can be either a primitive one (:class:`Range <pynusmv.model.Range>` or :class:`Boolean <pynusmv.model.Boolean>`), or instances of another module. All these instantiated objects can then be used as identifiers everywhere in the module definition.

The different sections of an SMV module are declared as members with special names such as `INIT`, `TRANS`, or `ASSIGN`. Some must be iterables (such as `INIT` and `TRANS`), others must be mappings (such as `ASSIGN`).

The :mod:`model module <pynusmv.model>` supports a large variety of classes to define all concepts in SMV modules. For instance, in the code above, we can write `c1.c` for the `c` variable of the `c1` instance. Standard arithmetic operations such as additions are supported by SMV expressions, as shown with `c + 1` above.

The defined modules can then be loaded in PyNuSMV in a similar way to SMV files::

    pynusmv.glob.load(counter, main)

This :func:`load <pynusmv.glob.load>` function accepts either sub-classes of :class:`Module <pynusmv.model.Module>`, a single path to an SMV file, or a string containing the definition of the model. Once the model is loaded, the corresponding internal data structures such as the BDD-encoded finite-state machine can be built with ::

    pynusmv.glob.compute_model()

This :func:`compute_model <pynusmv.glob.compute_model>` function accepts the path to a file containing the BDD variable order to use for building the BDD FSM, and whether or not single enumerations should be kept as they are, or converted into defines. Once the model is built, the BDD-encoded FSM can be accessed via ::

    fsm = pynusmv.glob.prop_database().master.bddFsm


Manipulating the BDD-encoded finite-state machine
=================================================


Manipulating BDDs
=================


Defining properties
===================


Verifying properties
====================



