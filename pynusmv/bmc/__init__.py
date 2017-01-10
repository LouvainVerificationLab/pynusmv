'''
The :mod:`pynusmv.bmc` module regroups the modules related to the bounded model
checking features of pynusmv. In particular, it provides an access to the 
following modules:

- :mod:`glob <pynusmv.bmc.glob>` which provides initialisation facilities for 
  the bmc sub system and global structures related to BMC in NuSMV. 
- :mod:`utils <pynusmv.bmc.utils>` which provides a set of utility functions 
  convenient when implementing a SAT based bounded model checker.
- :mod:`ltlspec <pynusmv.bmc.ltlspec>` which provides functions relative to the 
  implementation of BMC verification for linear time logic (see [BCC+03]_ for 
  further information about BMC).
- :mod:`invarspec <pynusmv.bmc.invarspec>` which provides a set of features 
  relative to *temporal induction* using sat solvers which is a technique 
  conceptually close to BMC. (For the full details, check [ES03]_ ).


References
~~~~~~~~~~

.. [BCC+03] 
    A. Biere, A. Cimatti, E. Clarke, O. Strichman, and Y. Zhu. 
    "Bounded model checking."
    In Ad- vances in Computers, 
    volume 58. Academic Press, 2003.
    
.. [ES03] Niklas Eén and Niklas Sörensson.
    "Temporal induction by incremental sat solving." 
    in Ofer Strichman and Armin Biere, editors, 
    Electronic Notes in Theoretical Computer Science, 
    volume 89. Elsevier, 2004.
'''

__all__ = [
    'glob', 
    'utils',
    'ltlspec',
    'invarspec'
]

from . import glob
from . import utils
from . import ltlspec
from . import invarspec
