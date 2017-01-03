"""
The :mod:`pynusmv.be.manager` module contains classes and functions related  
to the management of boolean expressions in PyNuSMV

In particular it contains:

* :class:`BeManager` which is the abstract interface of a manager
* :class:`BeRbcManager` which is the sole implementation of the BE manager
"""

__all__ = ['BeManager', 'BeRbcManager']

from pynusmv_lower_interface.nusmv.be       import be as _be
from pynusmv.utils          import PointerWrapper
from pynusmv.collections    import Slist, IntConversion
from pynusmv.be.expression  import Be


class BeManager(PointerWrapper):
    """
    The manager is the data structure that serves to physically store the 
    variables used to construct boolean expressions. As such, it is seen
    as rather low level of abstraction meant to offer services to an higher
    level encoding of the variables. As a consequence, the objects manipulated
    through its interface are fairly low level as well (integers instead of
    variables). If you are not implementing a new boolean encoding, you will
    probably want to focus and use the boolean encoding (:class:`pynusmv.be.encoder.BeEnc`)
    which offers roughly the same services but with an higher level interface. 
    
    .. note:: 
        whenever an 'index' is mention, it is used to denote the canonical
        identifier that permits to establish a correspondence between a be
        literal and a cnf literal.
    
    .. warning:: Subclassing this class imposes to implement _free
    
    .. seealso:: :class:`pynusmv.be.encoder.BeEnc`
    """

    def __init__(self, ptr, freeit=False):
        """
        Creates a new BeManager from the given ``ptr``
        
        :param ptr:   a pointer to a NuSMV structure representing a BeManager
        :type  ptr:   Be_Manager_ptr
        :param freeit:A flag telling whether or not this object has to be
                      automatically freed by the system. 
                      (more info in ``PointerWrapper``)
        """
        assert (ptr is not None)
        super().__init__(ptr, freeit)

    def _free(self):
        """
        Frees any system resources related to the manager.
        
        Warning: 
            This method is NOT implemented in this base class and should be 
            overridden by any implementing subclass
        """
        raise NotImplementedError("This is a bug: subclasses of BeManager must implement _free")

    def __hash__(self):
        """
        Makes this object hashable. 
        
        .. warning::
        
            Beware it uses the pointer to implement the hashing function.  
            So it is IDENTITY dependent (in C) and not value dependant.
        
        :return: an object that can serve as key to perform the lookup in a dict.
        """
        return self._ptr

    def __eq__(self, other):
        """
        Equality test between two objects. 
        
        .. warning::
        
            Beware it uses the pointer to implement the hashing function.  
            So it is IDENTITY dependent (in C) and not value dependant.
        
        :return: True iff the two object are the same
        """
        return self._ptr == other._ptr 
    
    # =========================================================================
    # ===== Utilities =========================================================
    # =========================================================================
    def be_index_to_var(self, index):
        """
        Retrieves the BE variable (expression) corresponding to the given index
        (index may be retrieved from the literals managed by this manager)

        :param index: the index
        :return: the be corresponding to this index
        """
        return Be(_be.Be_Index2Var(self._ptr, index), self)

    def be_var_to_index(self, expression):
        """
        Returns the BE index which corresponding to the given expression which
        can later be used to identify the BE literal or the CNF literal corres-
        ponding to this expression.
        
        .. note::
            
            This is the function you need to call in order to gain access to the
            BE or CNF literals ( managed by this manager ) corresponding to the
            given expression.
            
            Exemple::
            
                # assuming that variable a was declared in the SMV model and
                # converted to cnf
                idx = self.mgr.be_var_to_index(a)
                blit= self.mgr.be_index_to_literal(idx)
                clit= self.mgr.be_literal_to_cnf_literal(blit)
        
        :param expression: the expression whose index needs to be found
        :return: the BE index of the expression
        """
        return _be.Be_Var2Index(self._ptr, expression._ptr)
    
    def be_literal_to_index(self, literal):
        """
        Retrieves the BE index corresponding to the given BE literal.
        That BE index can later be used to identify the corresponding CNF literal.
        
        :param literal: the literal (may not be zero)
        :return: converts a BE literal to its index
        :raise: ValueError if `literal` is zero
        """
        if literal == 0:
            raise ValueError("Literal cannot be zero: this is used as an error marker by NuSMV")
        return _be.Be_BeLiteral2BeIndex(self._ptr, literal)

    def be_index_to_literal(self, index):
        """
        Retrieves the BE literal stored at the given index.
        
        :param index: the index (may not be smaller than zero)
        :return: Converts a BE index into a BE literal (always positive)
        :raise: ValueError if the given `index` is < 0
        """
        if index < 0:
            raise ValueError("Index is not allowed to be smaller than zero")
        return _be.Be_BeIndex2BeLiteral(self._ptr, index)

    def be_index_to_cnf_literal(self, index):
        """
        Retrieves the CNF literal corresponding to the given index.
        
        :param index: the index
        :return: Returns a CNF literal (always positive) associated with a given index
        """
        return _be.Be_BeIndex2CnfLiteral(self._ptr, index)

    def be_literal_to_cnf_literal(self, literal):
        """
        Converts a BE literal into a CNF literal (sign is taken into account)

        :param literal: the be literal
        :type  literal: integer
        :return: the CNF literal corresponding to the BE literal ``literal``
        """
        return _be.Be_BeLiteral2CnfLiteral(self._ptr, literal)

    def cnf_to_be_model(self, slist):
        """
        Converts the given CNF model (dimacs obtained from `solver.model` into 
        an equivalent model.

        :param slist: the cnf model in the form of a slist (as is the case from 
          `solver.model`).
        :return: Converts the given CNF model into BE model
        """
        # note: this is never used in NuSMV
        return Slist(_be.Be_CnfModelToBeModel(self._ptr, slist._ptr), IntConversion())

    def cnf_literal_to_be_literal(self, literal):
        """
        Converts a CNF literal into a BE literal

        The function returns 0 if there is no BE index associated with the given 
        CNF index. A given CNF literal should be created by given BE manager

        :param literal: the cnf literal (may not be zero)
        :type  literal: integer
        :return: the BE literal corresponding to the cnf literal ``literal``
        
        :raise: ValueError if `literal` is zero
        """
        if literal == 0:
            raise ValueError("Litteral cannot be ZERO (this is used as an error marker by NuSMV)")
        
        return _be.Be_CnfLiteral2BeLiteral(self._ptr, literal)
    
    def cnf_literal_to_index(self, literal):
        """
        Retrieves the index corresponding to the given CNF literal.
        That index can later be used to identify the corresponding BE literal.
        
        :param literal: the literal (may not be zero)
        :return: converts a CNF literal to its corresponding index
        :raise: ValueError if `literal` is zero
        """
        if literal == 0:
            raise ValueError("Litteral cannot be ZERO (this is used as an error marker by NuSMV)")
        
        return self.be_literal_to_index(self.cnf_literal_to_be_literal(literal))

    def dump_davinci(self, be, file):
        """
        Dumps the BE to the given `file` in davinci format
        
        :param be: the boolean expression
        :param file: the output StdioFile used to dump the information
        """
        _be.Be_DumpDavinci(self._ptr, be._ptr, file.handle)
 
    def dump_gdl(self, be, file):
        """
        Dumps the BE to the given `file` in gdl format
        
        :param be: the boolean expression
        :param file: the output StdioFile used to dump the information
        """
        _be.Be_DumpGdl(self._ptr, be._ptr, file.handle)
 
    def dump_sexpr(self, be, file):
        """
        Dumps the BE to the given `file`
        
        :param be: the boolean expression
        :param file: the output StdioFile used to dump the information
        """
        _be.Be_DumpSexpr(self._ptr, be._ptr, file.handle)
        
################################################################################
# Do not expose as long as RBC is not exposed too 
# (as discussed with S. Busard, this does not make much sense for a first  
#  iteration of the work)     
################################################################################
#     def spec_to_be(self, spec_expr) -> 'Be':
#         """
#         Converts an expression (ie. in RBC format) to a BE expression that can be manipulated
# 
#         :param spec_expr: the expression text
#         :return: a BE expression corresponding to the given ``spec_expr``
#         """
#         return Be(_be.Be_Manager_Spec2Be(self._ptr, spec_expr), self)
#     
#     def be_to_spec(self, bexpr):
#         """
#         Converts a BE to a spec in an other format (for instance RBC)
#         
#         :param bexpr: the expression to be converted
#         :return: the converted spec. Note however that since, the underlying api
#           returns a void*, there is no way to know 'a priori' what the real type
#           of the object will be. It is your responsibility to cast it and make
#           something useful with the returned pointer. (Rbc_t is nonetheless the
#           only spec type that's implemented in NuSMV at the time being)
#         """
#         return _be.Be_Manager_Be2Spec(self._ptr, bexpr._ptr)
#
#     @property
#     def spec_manager(self):
#         """
#         :return: the low level spec manager of this Be manager
#         """
#         return _be.Be_Manager_GetSpecManager(self._ptr)
################################################################################

class BeRbcManager(BeManager):
    """
    This is (at the time being) the sole implementation of the BeManager.
    It uses RBC as the underlying format to represent the boolean expressions
    but these are (so far) only exposed as an opaque pointer. 
    
    .. note::
        
        RBC stands for Reduced Boolean Circuit which is used to encode 
        (rewrite and shorten) boolean expressions in the form of an directed
        acyclic graph. 
        
        This form of representation is currently not available to PyNuSMV.
    """    
    
    # =========================================================================
    # ===== Construction/Destruction ==========================================
    # =========================================================================
    
    def __init__(self, ptr, freeit=False):
        super().__init__(ptr, freeit=freeit)

    def _free(self):
        """
        Frees the low level resources allocated for this object.
        See ``pynusmv.utils.PointerWrapper`` for more info about this api
        """
        if self._freeit and self._ptr is not None:
            _be.Be_RbcManager_Delete(self._ptr)
            self._freeit = False
            self._ptr = None
    
    # =========================================================================
    # ===== Static methods ====================================================
    # =========================================================================
    @staticmethod
    def with_capacity(capacity: int, freeit=True) -> 'BeRbcManager':
        """
        Creates a BeRbcManager with the capacity to store 'capacity' variables.
        
        Args: 
            :param capacity: the variable capacity of this rbc manager
            :type  capacity: integer
        
        Returns:
            A fresh instance of ``BeRbcManager``
        """
        return BeRbcManager(_be.Be_RbcManager_Create(capacity),freeit=freeit)

    # =========================================================================
    # ===== RbcManager specific fn ============================================
    # =========================================================================
    def reserve(self, size):
        """
        Changes the maximum number of variables the rbc manager can handle.
        
        Args:
            :param size: the new maximum number of variables that can be handled
                         by this manager.
            :type size: integer
        """
        _be.Be_RbcManager_Reserve(self._ptr, size)

    def reset(self):
        """
        Resets the RBC cache
        """
        _be.Be_RbcManager_Reset(self._ptr)
