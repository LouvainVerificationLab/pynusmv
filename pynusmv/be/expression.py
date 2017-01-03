"""
The :mod:`pynusmv.be.expression` module contains classes and functions related  
to the operation and manipulation of the boolean expressions in PyNuSMV.

In particular it contains:

+ :class:`Be`
+ :class:`BeCnf`
+ other utility functions
"""
from pynusmv.sat import Polarity
from pynusmv_lower_interface.nusmv.utils.utils import _utils
__all__ = ['Be', 'BeCnf']

from pynusmv.utils       import PointerWrapper
from pynusmv.collections import Slist, IntConversion, Conversion

import pynusmv_lower_interface.nusmv.be.be as _be

# ==============================================================================
# ===== Useful classes =========================================================
# ==============================================================================
class Be:
    """
    This is the interface of the boolean expression type.
    For obvious reasons, the function names have been kept as close to its
    BDD counterpart. The 'dsl' has also been kept. Hence:
    
        * ``a + b`` and ``a | b`` compute the disjunction of ``a`` and ``b``
        * ``a * b`` and ``a & b`` compute the conjunction of ``a`` and ``b``
        * ``~a`` and ``-a`` compute the negation of ``a``
        * ``a - b`` computes ``a & ~b``
        * ``a ^ b`` computes the exclusive-OR (XOR) of ``a`` and ``b``

    However, no comparison operators such as (lt, ge, ...) are provided.
    
    .. note::
        
        For the sake of compactness and efficient memory use, the boolean
        expressions (Be) are encoded in the form of reduced boolean circuits
        (directed acyclic graphs) because this representation is up to 
        exponentially smaller than the classic tree representation. See slides
        9-10 and 19 of http://disi.unitn.it/~rseba/DIDATTICA/fm2016/03_TEMPORAL_LOGICS_SLIDES.pdf
        to get more information about this.
        
        However, the details of the reduced boolean circuit are (so far) not  
        accessible throught PyNuSMV since it was considered as a too low level
        concern.
    """

    def __init__(self, ptr, be_manager):
        """
        Creates a new boolean expression (BE) from the given ``ptr``

        Args:
            :param ptr:        a pointer to a NuSMV structure representing a be_ptr
            :type  ptr:        be_ptr
            :param be_manager: the BeManager responsible for this object
            :type  be_manager: BeManager
            :param freeit:     A flag telling whether or not this object has to be
                               automatically freed by the system.
                               (more info in ``PointerWrapper``)
        """
        assert (ptr is not None)
        assert (be_manager is not None)
        self._ptr = ptr
        self._manager = be_manager

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

    # ==============================================================================
    # ===== Static methods to build true false =====================================
    # ==============================================================================
    @staticmethod
    def true(be_manager) -> 'Be':
        """
        Creates a constant with the meaning 'True'

        :param be_manager: the manager responsible for this expression
        :type  be_manager: BeManager
        :return: a constant boolean expression meaning True
        """
        return Be(_be.Be_Truth(be_manager._ptr), be_manager)

    @staticmethod
    def false(be_manager) -> 'Be':
        """
        Creates a constant with the meaning 'False'

        :param be_manager: the manager responsible for this expression
        :type  be_manager: BeManager
        :return: a constant boolean expression meaning False
        """
        return Be(_be.Be_Falsity(be_manager._ptr), be_manager)

    @staticmethod
    def if_then_else(be_manager, _if, _then, _else) -> 'Be':
        """
        Creates an if then else operation

        :param be_manager: the manager responsible for this expression
        :type  be_manager: BeManager
        :param        _if: the 'if' condition expression of the if then else
        :type         _if: Be
        :param      _then: the 'then' part of the expression
        :type       _then: Be
        :param      _else: the alternative
        :type       _else: Be
        :return: a constant boolean expression meaning True
        """
        return Be(_be.Be_Ite(be_manager._ptr, _if._ptr, _then._ptr, _else._ptr), be_manager)

    # ==============================================================================
    # ===== BE operations ==========================================================
    # ==============================================================================
    def is_true(self) -> 'bool':
        """
        Returns true iff the expression can be evaluated to True
        
        :return: true iff the expression can be evaluated to True
        """
        return bool(_be.Be_IsTrue(self._manager._ptr, self._ptr))

    def is_false(self) -> 'bool':
        """
        Returns true iff the expression can be evaluated to False
        
        :return: true iff the expression can be evaluated to False
        """
        return bool(_be.Be_IsFalse(self._manager._ptr, self._ptr))

    def is_constant(self) -> 'bool':
        """
        Returns true if the given be is a constant value, such as either False or True
        
        :return: true if the given be is a constant value, such as either False or True
        """
        return bool(_be.Be_IsConstant(self._manager._ptr, self._ptr))

    def not_(self) -> 'Be':
        """
        Negates the current expression
        
        :return: an expression (Be) corresponding to the negation of `self`
        """
        return Be(_be.Be_Not(self._manager._ptr, self._ptr), self._manager)

    def and_(self, other) -> 'Be':
        """
        Returns an expression (Be) corresponding to the conjunction of `self` and `other`
        
        :param other: a Be that will be conjuncted with self.
        :return: Returns an expression (Be) corresponding to the conjunction of `self` and `other`
        """
        return Be(_be.Be_And(self._manager._ptr, self._ptr, other._ptr), self._manager)

    def or_(self, other) -> 'Be':
        """
        Returns an expression (Be) corresponding to the disjunction of `self` and `other`
        
        :param other: a Be that will be disjuncted with self.
        :return: Returns an expression (Be) corresponding to the disjunction of `self` and `other`
        """
        return Be(_be.Be_Or(self._manager._ptr, self._ptr, other._ptr), self._manager)

    def xor(self, other) -> 'Be':
        """
        Returns an expression (Be) corresponding (`self` exclusive or `other`)
        
        :param other: a Be that will be xor'ed with self.
        :return: Returns an expression (Be) corresponding (`self` exclusive or `other`)
        """
        return Be(_be.Be_Xor(self._manager._ptr, self._ptr, other._ptr), self._manager)

    def imply(self, other) -> 'Be':
        """
        Returns an expression (Be) corresponding :math:`(self \\implies other)`. That is
        to say: :math:`(\\neg self \\vee other)` 
        
        :param other: a Be that will have to be implied by `self`
        :return: Returns an expression (Be) corresponding :math:`(self \\implies other)`
        """
        return Be(_be.Be_Implies(self._manager._ptr, self._ptr, other._ptr), self._manager)

    def iff(self, other) -> 'Be':
        """
        Returns an expression (Be) corresponding :math:`(self \\iff other)`. That is
        to say: :math:`(self \\implies other) \\wedge (other \\implies self)` 
        
        :param other: a Be that will have to be equivalent to `self`
        :return: Returns an expression (Be) corresponding :math:`(self \\iff other)`
        """
        return Be(_be.Be_Iff(self._manager._ptr, self._ptr, other._ptr), self._manager)

    def inline(self, add_conj):
        """
        Performs the inlining of this expression, either including or not the conjuction set.

        If add_conj is true, the conjuction set is included, otherwise only the inlined
        formula is returned for a lazy SAT solving.

        :param conj: a flag to tell whether or not to include the conjunction set
        :return: a copy of this expression with the inlining performed.
        """
        return Be(_be.Be_apply_inlining(self._manager._ptr, self._ptr, add_conj), self._manager)

    # ==============================================================================
    # ===== pythonic equivalent of the above =======================================
    # ==============================================================================
    def __neg__(self):
        """
        Negates the current expression (allows to write -self)
        
        :return: an expression (Be) corresponding to the negation of `self'
        """
        return self.not_()

    def __invert__(self):
        """
        Negates the current expression (allows to write ~self)
        
        :return: an expression (Be) corresponding to the negation of `self'
        """
        return self.not_()

    def __and__(self, other):
        """
        Returns an expression (Be) corresponding to the conjunction of `self' and `other'
        Allows to use the operator notation to write 
            `self' and `other'
            `self'  &  `other'
        
        :param other: a Be that will be conjuncted with self.
        :return: Returns an expression (Be) corresponding to the conjunction of `self' and `other'
        """
        return self.and_(other)
    
    def __mul__(self, other):
        """
        Returns an expression (Be) corresponding to the conjunction of `self' and `other'
        Allows to use the operator notation to write `self' * `other'
        
        :param other: a Be that will be conjuncted with self.
        :return: Returns an expression (Be) corresponding to the conjunction of `self' and `other'
        """
        return self.and_(other)
    
    def __or__(self, other):
        """
        Returns an expression (Be) corresponding to the disjunction of `self' and `other'
        Allows to use the operator notation to write 
            `self' or `other'
            `self' |  `other'
        
        :param other: a Be that will be disjuncted with self.
        :return: Returns an expression (Be) corresponding to the disjunction of `self' and `other'
        """
        return self.or_(other)
    
    def __add__(self, other):
        """
        Returns an expression (Be) corresponding to the disjunction of `self' and `other'
        Allows to use the operator notation to write  `self' + `other'
        
        :param other: a Be that will be disjuncted with self.
        :return: Returns an expression (Be) corresponding to the disjunction of `self' and `other'
        """
        return self.or_(other)
    
    def __xor__(self, other):
        """
        Returns an expression (Be) corresponding (`self' exclusive or `other')
        Allows to use the operator notation to write `self' ^ `other'
        
        :param other: a Be that will be xor'ed with self.
        :return: Returns an expression (Be) corresponding (`self' exclusive or `other')
        """
        return self.xor(other)

    def __sub__(self, other):
        """
        Returns an expression (Be) corresponding (`self' and not `other')
        Allows to use the operator notation to write `self' - `other'
        
        :param other: a Be that will be combined with self.
        :return: Returns an expression (Be) corresponding (`self' and not `other')
        """
        return self & ~(other)

    # ==============================================================================
    # ===== Conversions ============================================================
    # ==============================================================================
    ################################################################################
    # Hidden because it only returns an opaque pointer to self but casted to Rbc_t
    ################################################################################
    # def to_spec(self):
    #     """
    #     Converts a be to an external format (for instance RBC)
    # 
    #     :return: a specification corresponding to this expr
    #     """
    #     return _be.Be_Manager_Be2Spec(self._manager._ptr, self._ptr)
    ################################################################################

    def to_cnf(self, polarity=Polarity.POSITIVE):
        """
        Converts this boolean expression to a corresponding CNF

        .. note::
            By default, the POSITIVE polarity is used since it corresponds to
            what one would intuitively imagine when converting a formula to
            CNF. 

        'polarity' is used to determine if the clauses generated should
        represent the RBC positively, negatively, or both (1, -1 or 0
        respectively). For an RBC that is known to be true, the clauses
        that represent it being false are not needed (they would be removed
        anyway by propogating the unit literal which states that the RBC is
        true). Similarly for when the RBC is known to be false. This
        parameter is only used with the compact cnf conversion algorithm,
        and is ignored if the simple algorithm is used.
        
        :param polarity: the polarity of the expression
        :type  polarity: integer
        :return: a CNF equivalent of this boolean expression
        """
        return BeCnf(_be.Be_ConvertToCnf(self._manager._ptr, self._ptr, polarity), self._manager)

   
class BeCnf:
    """
    This class implements the CNF representation of a boolean expression
    """
    
    # This is really weird, declaring this var as a subclass of PointerWrapper
    # will only bring SEGFAULTs (because of double free's) although, it should
    # be perfectly allowed to manually delete some cnf. For this reason, it has
    # been undone and this class no longer inherits from PointerWrapper.
     
    def __init__(self, ptr, be_manager, freeit=False):
        """
        Creates a CNF from the given ``ptr``
        :param    ptr: the raw NuSMV Be_Cnf pointer
        :type     ptr: Be_Cnf_ptr
        :param freeit: a flag indicating whether or not ptr should be freed by the system
        :type  freeit: bool
        :param be_manager: a BE manager used to wrap unwrap boolean expressions
        :type  be_manager: BeManager
        :return: a new CNF object wrapping the given pointer
        """
        assert(ptr is not None)
        #super().__init__(ptr, freeit=freeit)
        self._ptr = ptr
        self._manager = be_manager  # serves only the purpose of being able to wrap/unwrap BE

    #def _free(self):
    #    """
    #    Frees any system resources related to the CNF.
    #    """
    #    if self._freeit and self._ptr is not None:
    #        _be.Be_Cnf_Delete(self._ptr)
    #        self._ptr = None
    #        self._freeit = False
    
    # ==============================================================================
    # ===== CNF properties =========================================================
    # ==============================================================================
    @property
    def original_problem(self) -> 'Be':
        """:return: the original BE problem this CNF was created from"""
        return Be(_be.Be_Cnf_GetOriginalProblem(self._ptr), self._manager)

    @property
    def vars_list(self):
        """
        Returns the list of independent variables in the CNF representation.

        :return:the independent variables list in the CNF representation
        """
        return Slist(_be.Be_Cnf_GetVarsList(self._ptr), IntConversion(), freeit=False)

    @property
    def clauses_list(self):
        """
        :return: a list of lists which contains the CNF-ed formula]

        Each list in the list is a set of integers which represents a single clause.
        Any integer value depends on the variable name and the time which the variable
        is considered in, whereas the integer sign is the variable polarity in
        the CNF-ed representation.
        """        
        return Slist(_be.Be_Cnf_GetClausesList(self._ptr), ArrayOfClauses(), freeit=False)

    @property
    def vars_number(self):
        """:return: Returns the number of independent variables in the given BeCnf structure"""
        return _be.Be_Cnf_GetVarsNumber(self._ptr)

    @property
    def clauses_number(self):
        """:return: the number of clauses in the given Be_Cnf structure"""
        return _be.Be_Cnf_GetClausesNumber(self._ptr)

    @property
    def max_var_index(self):
        """:return: the maximum variable index in the list of clauses"""
        return _be.Be_Cnf_GetMaxVarIndex(self._ptr)

    @max_var_index.setter
    def max_var_index(self, max_idx):
        """
        Sets the maximum variable index in the list of clauses

        :param max_idx: the maximum variable index in the list of clauses
        :type  max_idx: integer
        """
        _be.Be_Cnf_SetMaxVarIndex(self._ptr, max_idx)

    @property
    def formula_literal(self):
        """
        :return: the literal assigned to the whole formula.
                 It may be negative. If the formula is a constant unspecified value is returned
        """
        return _be.Be_Cnf_GetFormulaLiteral(self._ptr)

    @formula_literal.setter
    def formula_literal(self, literal):
        """
        :param literal: the literal assigned to the whole formula.
                        It may be negative.
        :type  literal: int
        """
        _be.Be_Cnf_SetFormulaLiteral(self._ptr, literal)

    # ==========================================================================
    # ===== CNF operations =====================================================
    # ==========================================================================
    def remove_duplicates(self):
        """Removes any duplicate literal appearing in single clauses"""
        _be.Be_Cnf_RemoveDuplicateLiterals(self._ptr)

    def print_stats(self, file, prefix):
        """
        Prints some statistics
 
        Print out, in this order: the clause number, the var number, the
        highest variable index, the average clause size, the highest
        clause size
 
        :param file: the output StdioFile where to write the stats
        :param prefix: the prefix to prepend the output lines with
        """
        _be.Be_Cnf_PrintStat(self._ptr, file.handle, prefix)
        
    def __repr__(self):
        """
        Returns a string representation of this CNF formula (especially useful
        for debugging purposes)
        
        .. note:: 
            the actual generated clauses all contain the formula literal but 
            this one is not shown in the representation as it only makes it 
            harder for a human to understand the meaning of that formula
        
        :return: a string representation of this formula
        """
        f_lit = self.formula_literal
        def clause2str(clause):
            lits = [ "X"+str(x) if x >= 0 else "!X"+str(-1*x) for x in clause if abs(x) != f_lit]
            return "("+ " | ".join(lits) +")"
        
        conj = " & ".join(list(map(clause2str, list(self.clauses_list))))
        return "formula literal = X{} <-> {}".format(f_lit, conj)
    
class ArrayOfClauses(Conversion):
    """
    A conversion object able to wrap/unwrap Slist of int to void* and vice versa
    """
    def __init__(self):
        """
        Creates a new SlistOfIntConversion
        """
        # void* -> Slist of int
        def p2o(x):
            # Thanks to the declared typemap, the list of clauses will be 
            # seamlessly translated from an int* to a python list PyListObject
            return _utils.void_star_to_int_star(x)
        def o2p(x):
            raise NotImplemented("Direct alteration of the list of clauses is not allowed")
        super().__init__(p2o, o2p)
        