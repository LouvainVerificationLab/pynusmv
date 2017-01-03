"""
PyNuSMV is a Python framework for experimenting and prototyping BDD-based model
checking algorithms based on NuSMV. It gives access to main BDD-related NuSMV
functionalities, like model and BDD manipulation, while hiding NuSMV
implementation details by providing wrappers to NuSMV functions and data
structures. In particular, NuSMV models can be read, parsed and compiled,
giving full access to SMV's rich modeling language and vast collection of
existing models.

PyNuSMV is composed of several modules, each one proposing some
functionalities:

* :mod:`init <pynusmv.init>` contains all the functions needed to initialize
  and close NuSMV. These functions need to be used before any other access to
  PyNuSMV.
* :mod:`glob <pynusmv.glob>` provides functionalities to read and build a model
  from an SMV source file.
* :mod:`model <pynusmv.model>` provides functionalities to define NuSMV models
  in Python.
* :mod:`node <pynusmv.node>` provides a wrapper to NuSMV `node` structures.
* :mod:`fsm <pynusmv.fsm>` contains all the FSM-related structures like
  BDD-represented FSM, BDD-represented transition relation, BDD encoding and
  symbols table.
* :mod:`prop <pynusmv.prop>` defines structures related to propositions of a
  model; this includes CTL specifications.
* :mod:`dd <pynusmv.dd>` provides BDD-related structures like generic BDD,
  lists of BDDs and BDD-represented states, input values and cubes.
* :mod:`parser <pynusmv.parser>` gives access to NuSMV parser to parse simple
  expressions of the SMV language.
* :mod:`mc <pynusmv.mc>` contains model checking features.
* :mod:`exception <pynusmv.exception>` groups all the PyNuSMV-related
  exceptions.
* :mod:`utils <pynusmv.utils>` contains some side functionalities.
* :mod:`sat <pynusmv.sat>` contains classes and functions related to the 
  operation and manipulation of the different sat solvers available in PyNuSMV.
* :mod:`bmc.glob <pynusmv.bmc.glob>` serves as a reference entry point for the 
  bmc-related functions (commands) and global objects. It defines amongst other 
  the function :func:`bmc_setup <pynusmv.bmc.glob.bmc_setup>` wich must be called 
  before using any of the BMC related features + the class :class:`BmcSupport <pynusmv.bmc.glob.BmcSupport>`
  which acts as a context manager and frees you from the need of explicitly 
  calling :func:`bmc_setup <pynusmv.bmc.glob.bmc_setup>`.
* :mod:`bmc.ltlspec <pynusmv.bmc.ltlspec>` contains all the functionalities 
  related to the bounded model checking of LTL properties: from end to end 
  property verification to the translation of formulas to boolean expressions 
  corresponding to the SAT problem necessary to verify these using LTL bounded 
  semantics of the dumping of problem to file (in DIMACS format).
* :mod:`bmc.invarspec <pynusmv.bmc.invarspec>` contains all the functionalities
  related to the verification of INVARSPEC properties using a technique close to
  that of SAT-based bounded model checking for LTL. (See *Niklas Eén and Niklas 
  Sörensson. "Temporal induction by incremental sat solving."* for further details).
* :mod:`bmc.utils <pynusmv.bmc.utils>` contains bmc related utility functions.
* :mod:`be.expression <pynusmv.be.expression>` contains classes and functions 
  related to the operation and manipulation of the boolean expressions.
* :mod:`be.fsm <pynusmv.be.fsm>` contains classes and functions related to 
  PyNuSMV’s description of an FSM when it is encoded in terms of boolean 
  expressions.
* :mod:`be.encoder <pynusmv.be.encoder>` provides the boolean expression 
  encoder capabilities that make the interaction with a SAT solver easy.
* :mod:`be.manager <pynusmv.be.manager>` contains classes and functions related 
  to the management of boolean expressions (conversion to reduced boolean circuits.
  Caveat: RBC representation is not exposed to the upper interface).
* :mod:`collections <pynusmv.collections>` impements pythonic wrappers around 
  the internal collections and iterator structures used in NuSMV.
* :mod:`wff <pynusmv.wff>` encapsulates the notion of well formed formula as 
  specified per the input language of NuSMV. It is particularly useful in the 
  scope of BMC.
* :mod:`trace <pynusmv.trace>` defines the classes Trace and TraceStep which 
  serve the purpose of representing traces (executions) in a PyNuSMV model.
* :mod:`sexp.fsm <pynusmv.sexp.fsm>` contains a representation of the FSM in 
  terms of simple expressions.

.. WARNING:: Before using any PyNuSMV functionality, make sure to call
   :func:`init_nusmv <pynusmv.init.init_nusmv>` function to initialize NuSMV;
   do not forget to also call :func:`deinit_nusmv <pynusmv.init.deinit_nusmv>`
   when you do not need PyNuSMV anymore to clean everything needed by NuSMV to
   run.

"""

__all__ = ['dd', 'exception', 'fsm', 'glob', 'init', 'mc', 'parser',
           'prop', 'utils', 'model', 'node', 'collections']

from . import dd
from . import fsm
from . import glob
from . import init
from . import mc
from . import parser
from . import prop
from . import utils
from . import model
from . import node
from . import collections
from . import exception
