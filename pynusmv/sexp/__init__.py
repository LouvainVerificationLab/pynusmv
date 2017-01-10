'''
The :mod:`pynusmv.sexp` module regroups the modules related to the treatment of
simple expressions (SEXP) in pynusmv. As a matter of fact, it only provides an
access to the :mod:`fsp <pynusmv.sexp.fsm>` module which provides an abstract 
representation of the FSM encoded in terms of simple expressions (but not BE yet).

Concretely, it is highly likely that you'll use this module in conjunction with 
:mod:`pynusmv.be.fsm`.
'''
__all__ = [
    'fsm'
]

from . import fsm
