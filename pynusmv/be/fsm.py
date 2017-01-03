"""
The :mod:`pynusmv.be.fsm` module contains classes and functions related  
to PyNuSMV's description of a BE encoded FSM

In particular it contains: :class:`BeFsm` which is the sole implementation of a BE FSM
"""

__all__ = ['BeFsm']

from pynusmv_lower_interface.nusmv.prop    import prop as _prop
from pynusmv_lower_interface.nusmv.node    import node as _node
from pynusmv_lower_interface.nusmv.fsm.be  import be   as _be
from pynusmv.utils         import PointerWrapper

from pynusmv.be.expression import Be
from pynusmv.be.encoder    import BeEnc
from pynusmv.collections   import NodeIterator 

from pynusmv.exception     import NuSMVBeFsmMasterInstanceNotInitializedError 

class BeFsm(PointerWrapper):
    """
    This class wraps the public interface of a BE FSM as defined in NuSMV
    with the BeFsm_ptr type.
    
    Its role is to give an access to the properties of FSM as represented with
    boolean expressions (BE). For instance, it gives access to the initial states
    the invariants and the transition relation encoded in terms of BE. Moreover
    it gives the possibility to compute the synchronous product of two FSMs.  
    """
    
    def __init__(self, ptr, freeit=False):
        """
        Creates an instance of the BeFsm, using the NuSMV pointer. 
        :param ptr: the NuSMV pointer of type BeFsm_ptr
        :param freeit: a flag indicating whether or not the system resources 
          should be freed upon garbage collection.
        """
        super().__init__(ptr, freeit)
        
    def _free(self):
        """Frees the system resources associated with this object"""
        if self._freeit and self._ptr is not None:
            _be.BeFsm_destroy(self._ptr)
            self._freeit = False
            self._ptr    = None
    
    @staticmethod
    def global_master_instance():
        """
        :return: the boolean FSM in BE stored in the master prop. 
        :raises NuSMVBeFsmMasterInstanceNotInitializedError:
             when the global BE FSM is null in the global properties database 
             (ie when coi is enabled).
        """
        _pd  = _prop.PropPkg_get_prop_database()
        _fsm = _prop.PropDb_master_get_be_fsm(_pd)
        if _fsm is None:
            raise NuSMVBeFsmMasterInstanceNotInitializedError("""
                            BE fsm stored in master prop is not initialized.
                            You must either initialize the BE model (ie. go_bmc)
                            or disable COI.
                            """)
        return BeFsm(_fsm)
    
    @staticmethod
    def create(enc, init, invar, trans, fairness, freeit=False):
        """
        Creates a new BeFsm instance using the given encoder, initial states, 
        invariants, transition relation and list of fairness.
        
        :param enc: the encoder used to represent the variables of the model.
        :param init: the boolean expression representing the initial states of 
          the FSM
        :param invar: the boolean expression representing the invariants of the 
          model encoded in this FSM
        :pqram trans: the boolean expression representing the transition relation
          of the model encoded in this FSM
        :param fairness: a list of boolean expression representing the fairness
          constraints of the model. 
        :param freeit: a flag indicating whether or not the system resources 
          should be freed upon garbage collection.
          
        :return: a new instance of BeFsm that gets its init, invar, transition 
          relation and the list of fairness in Boolean Expression format
        """
        # very unlikely to be used directly
        return BeFsm(_be.BeFsm_create(enc._ptr, 
                                      init._ptr, 
                                      invar._ptr,
                                      trans._ptr,
                                      fairness._ptr))
    
    @staticmethod
    def create_from_sexp(enc, sexp_fsm):
        """
        Creates a new instance of BeFsm extracting the necessary information
        from the given `sexp_fsm` of type :class:`BoolSexpFsm <pynusmv.sexp.BoolSexpFsm>`
        
        :param enc: the encoder used to represent the variables of the model.
        :param sexp_fsm: the BoolSexpFsm which contains the automaton information
        """
        return BeFsm(_be.BeFsm_create_from_sexp_fsm(enc._ptr, sexp_fsm._ptr)) 
    
    def copy(self, freeit=True):
        """
        Creates a new independent copy of the FSM.
        :param freeit: a flag indicating whether or not the system resources 
        should be freed upon garbage collection.
        """
        return BeFsm(_be.BeFsm_copy(self._ptr), freeit=freeit)
    
    def __copy__(self):
        """Creates a new independent copy of the FSM"""
        return self.copy()
    
    @property
    def encoding(self):
        """The BE encoding of this FSM"""
        if not hasattr(self, "__encoding"):
            setattr(self, '__encoding', BeEnc(_be.BeFsm_get_be_encoding(self._ptr), freeit=False))
        return getattr(self, '__encoding')
    
    @property
    def init(self):
        """The BE representing the initial states of this FSM"""
        _expr = _be.BeFsm_get_init(self._ptr)
        return Be(_expr, self.encoding.manager) if _expr is not None else None
    
    @property
    def invariants(self):
        """The boolean expression representing the invariants of this FSM"""
        _expr = _be.BeFsm_get_invar(self._ptr)
        return Be(_expr, self.encoding.manager) if _expr is not None else None
    
    @property
    def trans(self):
        """
        The boolean expression representing the transition relation of the FSM
        
        .. note::
        
            Transition expression shifted at time zero is what brings you to 
            state one. Hence::
            
                shift_to_time(init, 0) & shift_to_time(trans, 0) == STATE_1 
        """
        _expr = _be.BeFsm_get_trans(self._ptr)
        return Be(_expr, self.encoding.manager) if _expr is not None else None
    
    @property
    def fairness_list(self):
        """
        The list of fairness constraints of this model encoded in BE format.
        
        .. note:: accessing this property is not free: use fairness_iterator
           instead if you don't need to manipulate the list as a list.
        """
        return [ i for i in self.fairness_iterator() ]
    
    def fairness_iterator(self):
        """:return: an iterator to iterate over the fairness list"""
        _ptr  = _be.BeFsm_get_fairness_list(self._ptr)
        _iter = NodeIterator.from_pointer(_ptr)
        for fairness in _iter:
            yield self._fairness_conversion(fairness)
    
    def _fairness_conversion(self, fairness):
        """
        Converts the given `fairness` into a Be representation.
        
        .. note::
            This function is present for purely technical reason: under the 
            hood, NuSMV encodes the fairness list as a NodeList however the
            'car' (value) of these nodes is nothing that can be understood 
            AST-wise. Indeed, the values are opaque pointers (be_ptr that is 
            to say void*) to a structure representing a Be. 
        """
        beptr = _be.node_ptr_to_be_ptr(_node.car(fairness._ptr))
        bexpr = Be(beptr, self.encoding.manager)
        return bexpr
    
    def apply_synchronous_product(self, other):
        """
        Apply the synchronous product between self and other modifying self.
        :param other: the other to compute the synchronous product with
        """
        _be.BeFsm_apply_synchronous_product(self._ptr, other._ptr)
        
    def __mul__(self, other):
        """
        :return: a new fsm corresponding to the synchronous product of self and
        other.
        :param other: the other to compute the synchronous product with
        """
        cpy = self.copy()
        cpy.apply_synchronous_product(other)
        return cpy
    
    def __imul__(self, other):
        """
        Apply the synchronous product between self and other modifying self.
        :param other: the other to compute the synchronous product with
        """
        self.apply_synchronous_product(other)
    