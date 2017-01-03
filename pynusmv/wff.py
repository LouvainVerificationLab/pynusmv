"""
This module defines the :class:`Wff` which encapsulates the notion of well 
formed formula as specified per the input language of NuSMV. It is particularly
useful in the scope of BMC as it
"""
from pynusmv_lower_interface.nusmv.node import node as nsnode
from pynusmv_lower_interface.nusmv.wff import wff as nswff
from pynusmv_lower_interface.nusmv.wff.w2w import w2w as nsw2w
from pynusmv_lower_interface.nusmv.bmc import bmc as nsbmc
from pynusmv_lower_interface.nusmv.compile import compile as nscompile
from pynusmv_lower_interface.nusmv.parser.parser import (IMPLIES, ATOM, NUMBER, NUMBER_UNSIGNED_WORD,
                                  NUMBER_SIGNED_WORD, NUMBER_FRAC, NUMBER_REAL,
                                  NUMBER_EXP, EX, AX, EF, AF, EG, AG, EBF, EBG,
                                  ABF, ABG)

from . import glob
from .utils import PointerWrapper
from .node import Node
from .exception import NuSMVWffError
from .be.expression import Be

class Wff(PointerWrapper):
    """
    The :class:`Wff` (Well Formed [Temporal] Formula) encapsulates the structure
    of a specification in various supported logics as of the NuSMV input language
    """
    
    def __init__(self, ptr, freeit=False):
        """
        Creates a new instance from a given pointer.
        
        .. warning::
        
            Turning the `freeit` flag on on this object is usually a very bad
            idea since it creates the risk for double free's. This stems from
            the fact that :class:`Wff` is envisioned as a wrapper for an other
            object with no personality of its own.
        
        :param ptr: the node_ptr like pointer to decorate
        :param freeit: a flag indicating whether or not the nusmv resources 
            allocated to this object should be reclaimed upon garbage collection.
        """
        super().__init__(ptr, freeit=freeit)
        
    def _free(self):
        if self._freeit and self._ptr is not None:
            nsnode.free_node(self._ptr)
            self._freeit = False
            self._ptr    = None
        
    @staticmethod
    def decorate(node_like):
        """
        Creates a new instance from a node_like object (:mod:`pynusmv.node`).
        
        :param node_like: an object which behaves as a node (typically subclass)
            which will be wrapped to be considered as a Wff 
        :return: `node_like` but wrapped in a Wff overlay.
        """
        return Wff(node_like._ptr)

    @staticmethod
    def true():
        # don't free, it is constant
        return Wff(nswff.Wff_make_truth(), freeit=False)

    @staticmethod
    def false():
        # don't free, it is constant
        return Wff(nswff.Wff_make_falsity(), freeit=False)

    @property
    def depth(self):
        """
        Returns the modal depth of the given formula]

        :return: 0 for propositional formulae, 1 or more for temporal formulae
        :raise NuSMVWffError: when this wff is not a valid LTL formula
        """
        if self._ptr.type == IMPLIES:
            raise NuSMVWffError("implies should have been nnf-ef away!\n");
        
        unexpected_leaf = [ATOM, NUMBER, NUMBER_UNSIGNED_WORD,
                           NUMBER_SIGNED_WORD, NUMBER_FRAC, NUMBER_REAL,
                           NUMBER_EXP]
        if self._ptr.type in unexpected_leaf:
            raise NuSMVWffError("Unexpected leaf")
        
        ctl_operators = [EX, AX, EF, AF, EG, AG, EBF, EBG, ABF, ABG]
        if self._ptr.type in ctl_operators:
            raise NuSMVWffError("Unexpected CTL operator")
        
        return nswff.Wff_get_depth(self._ptr)
    
    ############################################################################
    # Conversion methods
    ############################################################################
    def to_negation_normal_form(self):
        return Wff(nsw2w.Wff2Nnf(self._ptr), freeit=True)

    def to_node(self):
        return Node.from_ptr(self._ptr, freeit=False)
        
    def to_boolean_wff(self, bdd_enc=None):
        """
        Converts this scalar expression to a boolean equivalent
        
        .. note::
         
            Uses the determinizing layer and can therefore introduce new
            determination variable.
        """
        encoding = bdd_enc if bdd_enc is not None else glob.bdd_encoding()
        return Wff(nscompile.Compile_detexpr2bexpr(encoding._ptr, self._ptr), freeit=True)
    
    def to_be(self, be_enc):
        """
        Converts this WFF to the BE format.
        
        .. warning::
        
            This *DOES NOT WORK FOR TEMPORAL FORMULAS*, if you pass one, NuSMV
            will complain and crash with an error message on stderr.
            In order to generate the BMC problem for this particular formula, 
            (if it is a temporal one) you should instead, use a the *bounded*
            *semantic* of your choice to that end (LTL semantic is already 
            defined).  
            
        :param be_enc: the boolean expression encoder that will serve to back
           the conversion process.
        :return: a BE (rbc) representation of this formula.
        """
        return Be(nsbmc.Bmc_Conv_Bexp2Be(be_enc._ptr, self._ptr), be_enc.manager) 
    
    ############################################################################

    def not_(self):
        return Wff(nswff.Wff_make_not(self._ptr))

    def and_(self, other):
        if other is None:
            raise ValueError("Cannot make an AND formula without 2nd conjunct")
        return Wff(nswff.Wff_make_and(self._ptr, other._ptr), freeit=True)

    def or_(self, other):
        if other is None:
            raise ValueError("Cannot make an OR formula without 2nd conjunct")
        return Wff(nswff.Wff_make_or(self._ptr, other._ptr), freeit=True)

    def implies(self, other):
        if other is None:
            raise ValueError("Cannot make an IMPLIES formula without 2nd conjunct")
        return Wff(nswff.Wff_make_implies(self._ptr, other._ptr), freeit=True)

    def iff(self, other):
        if other is None:
            raise ValueError("Cannot make an IFF formula without 2nd conjunct")
        return Wff(nswff.Wff_make_iff(self._ptr, other._ptr), freeit=True)

    def next_(self):
        return Wff(nswff.Wff_make_next(self._ptr), freeit=True)

    def next_times(self, x):
        return Wff(nswff.Wff_make_opnext_times(self._ptr, x), freeit=True)

    def opnext(self):
        return Wff(nswff.Wff_make_opnext(self._ptr), freeit=True)

    def opprec(self):
        return Wff(nswff.Wff_make_opprec(self._ptr), freeit=True)

    def opnotprecnot(self):
        return Wff(nswff.Wff_make_opnotprecnot(self._ptr), freeit=True)

    def globally(self):
        return Wff(nswff.Wff_make_globally(self._ptr), freeit=True)

    def historically(self):
        return Wff(nswff.Wff_make_historically(self._ptr), freeit=True)

    def eventually(self):
        return Wff(nswff.Wff_make_eventually(self._ptr), freeit=True)

    def once(self):
        return Wff(nswff.Wff_make_once(self._ptr), freeit=True)

    def until(self, other):
        return Wff(nswff.Wff_make_until(self._ptr, other._ptr), freeit=True)

    def since(self, other):
        return Wff(nswff.Wff_make_since(self._ptr, other._ptr), freeit=True)

    def releases(self, other):
        return Wff(nswff.Wff_make_releases(self._ptr, other._ptr), freeit=True)

    def triggered(self, other):
        return Wff(nswff.Wff_make_triggered(self._ptr, other._ptr), freeit=True)

    def __and__(self, other):
        return self.and_(other)

    def __or__(self, other):
        return self.or_(other)

    def __not__(self):
        return self.not_()

    def __neg__(self):
        return self.not_()

    def __invert__(self):
        return self.not_()
    
    def __hash__(self):
        return self._ptr
    
    def __eq__(self, other):
        return self._ptr == other._ptr
    
    def __str__(self):
        return nsnode.sprint_node(self._ptr)
    
    def __repr__(self):
        return "WFF("+nsnode.sprint_node(self._ptr)+") for "+str(self._ptr)

