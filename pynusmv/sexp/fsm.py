'''
This module defines the classes wrapping the SEXP FSM structures. 
In particular:

    - :class:`SexpFsm` which wraps the basic SEXP fsm
    - :class:`BoolSexpFsm` which wraps a boolean SEXP fsm
    
'''

from pynusmv_lower_interface.nusmv.fsm.sexp import sexp as _sexp

from pynusmv.fsm         import SymbTable  
from pynusmv.utils       import PointerWrapper
from pynusmv.node        import Node, FlatHierarchy
from pynusmv.collections import NodeList, NodeIterator


__all__ = ['SexpFsm', 'BoolSexpFsm']

class SexpFsm(PointerWrapper):
    """
    This class encapsulates a generic SEXP FSM
    """
    
    # NOT exposed because never used in NuSMV: 
    # - SexpFsm_create_predicate_normalised_copy
    # - SexpFsm_apply_synchronous_product
    # - SexpFsm_get_var_init
    # - SexpFsm_get_var_invar
    # - SexpFsm_get_var_input
    # - SexpFsm_self_check
    #
    # NOT exposed for other reason: 
    # - SexpFsm_get_var_trans (only used in FsmBuilder_create_bdd_fsm_of_vars)
    # - variables_set not exposed as it is useless once we have variables_list
    
    def __init__(self, ptr, freeit=True):
        """
        Creates a new instance from the given pointer
        
        :param ptr: the pointer to wrap (SexpFsm_ptr)
        :param freeit: a flag indicating whether or not the undeflying fsm  
            should be destroyed upon garbage collection
        """
        super().__init__(ptr, freeit=freeit)
    
    def _free(self):
        """
        Destroys the underlying fsm if needed
        """
        if self._freeit and self._ptr is not None:
            _sexp.SexpFsm_destroy(self._as_SexpFsm_ptr())
            self.freeit = False
            self._ptr   = None
            
    def _as_SexpFsm_ptr(self):
        """
        Returns a pointer representing this object of the type SexpFsm_ptr.
        This method is useful to seamlessly implement the polymorphism of the
        subclasses
        """
        return self._ptr
    
    def copy(self):
        """
        Creates a copy of this object
        
        :return: a copy of this object
        """
        return SexpFsm(_sexp.BoolSexpFsm_copy(self._as_SexpFsm_ptr()))
    
    def __copy__(self):
        """
        Creates a copy of this object
        
        :return: a copy of this object
        """
        return self.copy()

    @property
    def symbol_table(self):
        """
        :return: the symbol table associated to this FSM.
        """
        return SymbTable(_sexp.SexpFsm_get_symb_table(self._as_SexpFsm_ptr()))
    
    @property
    def is_boolean(self):
        """
        :return: true iff this fsm is a boolean SEXP FSM
        """
        return bool(_sexp.SexpFsm_is_boolean(self._as_SexpFsm_ptr()))
    
    @property
    def hierarchy(self):
        """
        :return: the flat hierarchy associated to this object
        """
        return FlatHierarchy(_sexp.SexpFsm_get_hierarchy(self._as_SexpFsm_ptr()))
    
    @property
    def init(self):
        """
        :return: an Expression that collects init states for all handled vars. 
        """
        return Node.from_ptr(_sexp.SexpFsm_get_init(self._as_SexpFsm_ptr()))
    
    @property
    def invariants(self):
        """
        :return: an Expression that collects invar states for all handled vars. 
        """
        return Node.from_ptr(_sexp.SexpFsm_get_invar(self._as_SexpFsm_ptr()))

    @property
    def trans(self):
        """
        :return: an Expression that collects all next states for all variables
        """
        return Node.from_ptr(_sexp.SexpFsm_get_trans(self._as_SexpFsm_ptr()))
    
    @property
    def input(self):
        """
        :return: an Expression that collects all input states for all variables
        """
        # I don"t get it, this method always returns None
        return Node.from_ptr(_sexp.SexpFsm_get_input(self._as_SexpFsm_ptr()))

    @property
    def justice(self):
        """
        The list of sexp expressions defining the set of justice constraints 
        for this FSM.
        
        .. note::
            
            NUSMV supports two types of fairness constraints, namely justice 
            constraints and com- passion constraints. A justice constraint 
            consists of a formula f, which is assumed to be true infinitely 
            often in all the fair paths. In NUSMV, justice constraints are 
            identified by keywords JUSTICE and, for backward compatibility, 
            FAIRNESS.
                 
        :return: the list of sexp expressions defining the set of justice
                 constraints for this FSM. 
        """
        ptr = _sexp.SexpFsm_get_justice(self._as_SexpFsm_ptr())
        return NodeIterator.from_pointer(ptr)
    
    @property
    def compassion(self):
        """
        The list of sexp expressions defining the set of compassion constraints 
        for this FSM.
        
        .. note::
            
            NUSMV supports two types of fairness constraints, namely justice 
            constraints and compassion constraints. A justice constraint 
            consists of a formula f, which is assumed to be true infinitely 
            often in all the fair paths. A compassion constraint consists of a 
            pair of formulas (p,q); if property p is true infinitely often in a
            fair path, then also formula q has to be true infinitely often in 
            the fair path. In NUSMV, compassion constraints are identified by 
            keyword COMPASSION. If compassion constraints are used, then the 
            model must not contain any input variables. Currently, NUSMV does 
            not enforce this so it is the responsibility of the user to 
            make sure that this is the case.
                 
        :return: the list of sexp expressions defining the set of compassion
                 constraints for this FSM. 
        """
        ptr = _sexp.SexpFsm_get_compassion(self._as_SexpFsm_ptr())
        return NodeIterator.from_pointer(ptr)
    
    @property
    def variables_list(self):
        """
        :return: the set of variables in the FSM
        """
        return NodeList(_sexp.SexpFsm_get_vars_list(self._as_SexpFsm_ptr()))
    
    @property
    def symbols_list(self):
        """
        :return: the set of symbols in the FSM
        """
        return NodeList(_sexp.SexpFsm_get_symbols_list(self._as_SexpFsm_ptr()))
    
    @property
    def is_syntactically_universal(self):
        """
        Checks if the SexpFsm is syntactically universal:
        Checks INIT, INVAR, TRANS, INPUT, JUSTICE, COMPASSION to be empty 
        (ie: True Expr). In this case returns true, false otherwise
                       
        :return: true iff this fsm has no INIT, INVAR, TRANS, INPUT, JUSTICE or
            COMPASSION.
        """
        return bool(_sexp.SexpFsm_is_syntactically_universal(self._as_SexpFsm_ptr()))
    

class BoolSexpFsm(SexpFsm):
    """
    This class encapsulates a boolean encoded SEXP FSM. 
    
    .. note:: 
        
        Since it defines the same interface as the regular SexpFSM, the purpose
        of this class is to correctly redefine the _free function and override
        the _as_SexpFsm_ptr function so as to leverage the inheritance defined
        in C.
    """
    
    def __init__(self, ptr, freeit=True):
        """
        Creates a new instance from the given pointer
        
        :param ptr: the pointer to wrap (SexpFsm_ptr)
        :param freeit: a flag indicating whether or not the undeflying fsm  
            should be destroyed upon garbage collection
        """
        super().__init__(ptr, freeit=freeit)
    
    def _free(self):
        """
        Destroys the underlying fsm if needed
        """
        if self._freeit and self._ptr is not None:
            _sexp.BoolSexpFsm_destroy(self._as_SexpFsm_ptr())
            self.freeit = False
            self._ptr   = None
    
    def _as_SexpFsm_ptr(self):
        """
        Returns a pointer representing this object of the type SexpFsm_ptr.
        This method is useful to seamlessly implement the polymorphism of the
        subclasses
        
        .. note:: this method overrides that from SexpFsm
        """
        return _sexp.boolsexpfsm_to_sexpfsm(self._ptr)
            
    # TODO: complete with missing functions