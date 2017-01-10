'''
The :mod:`pynusmv.be` module regroups the modules related to the treatment of
boolean expressions (BE) in pynusmv. In particular, it provides an access to:

- :mod:`expression <pynusmv.be.expression>` containing classes and functions 
  related to the BE themselves.
- :mod:`fsm <pynusmv.be.fsm>` containing classes and functions to represent the 
  model FSM encoded in terms of boolean variables only.
- :mod:`encoder <pynusmv.be.encoder>` containg classes to represent boolean 
  variables and the way to encode them so as to represent a *timeline*, a path in 
  the fsm.
- :mod:`manager <pynusmv.be.manager>` which provides an access to lower level 
  functions and classes related to the management and physical representation of 
  the boolean expressions.

'''
__all__ = [
    'expression',
    'fsm',
    'encoder',
    'manager'
]

from . import expression
from . import fsm
from . import encoder
from . import manager
