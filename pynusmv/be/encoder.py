"""
The :mod:`pynusmv.be.encoder` module provides the BE encoder related functionalities

* :class:`BeWrongVarType` a kind of exception thrown when the type of a variable
  does not correspond to what the specification expects.
* :class:`BeVarType` an enum describing the possible types of variables 
  (These can be combined)
* :class:`BeEnc` which provides the encoder related functionalities (i.e: shifts)

.. note::
    Most of the documentation comes either from the NuSMV source code BeEnc.c
    or the NuSMV-2.5 User Manual
    
    :url: http://nusmv.fbk.eu/NuSMV/userman/v25/nusmv.pdf
"""

# There is no reason one would like to instanciate BeEncUntimedVarIterator so
# it is not exposed
__all__ = ['BeEnc', 'BeVarType', 'BeWrongVarType' ]

from pynusmv_lower_interface.nusmv.enc      import enc  as _enc  
from pynusmv_lower_interface.nusmv.enc.be   import be   as _be
from pynusmv_lower_interface.nusmv.enc.base import base as _base
from pynusmv_lower_interface.nusmv.enc.bool import bool  as _bool

from enum                   import IntEnum
from collections            import Iterator 
from pynusmv.node           import Node
from pynusmv.utils          import PointerWrapper, indexed
from pynusmv.collections    import NodeList  
from pynusmv.fsm            import SymbTable
from pynusmv.be.expression  import Be
from pynusmv.be.manager     import BeRbcManager

from pynusmv.exception      import NuSMVBeEncNotInitializedError 

class BeWrongVarType(Exception):
    """
    Thrown whenever an error happens because the type of variable is not the
    expected one.
    """
    def __init__(self, msg):
        """Creates a new instance"""
        super().__init__(msg)


class BeVarType(IntEnum):
    """
    Used to classify a be variable within 4 main categories: 
      - current state variables
      - frozen variables
      - input variables
      - next state variables 
    
    These values can be combined when for example the iteration is
    performed.  In this way it is possible to iterate through the set of
    current and next state vars, skipping the inputs.
    """
    CURR   = _be.BE_VAR_TYPE_CURR 
    FROZEN = _be.BE_VAR_TYPE_FROZEN
    INPUT  = _be.BE_VAR_TYPE_INPUT
    NEXT   = _be.BE_VAR_TYPE_NEXT
    ALL    = _be.BE_VAR_TYPE_ALL
    ERROR  = _be.BE_VAR_TYPE_ERROR
  

class BeVar:
    """
    An abstraction used to represent an encoded variable.
    
    .. note::
        An *untimed* variable, is an 'abstract' variable that does
        not belong to any time block. It can therefore be seen as a 
        prototypical variable meant to help you retrieve the variable which 
        is actually used to model this 'variable' at some point of time in 
        a computation. That second type of variable (which are associated to 
        a time block) are therefore called *timed* variables.
        
        Even though a variable is untimed, it can be 'current' or 'next'. 
        These designations simply express the fact that within a time block,
        the current variable designates the variable before a transition is
        taken and the 'next' variable expresses the fact that it relates to
        the same variable after a transition is taken.
    
    """
    def __init__(self, encoding, index):
        """
        Creates a new instance. 
        
        .. note:: 
            This constructor is considered private and should be called from
            the BeEnc related classes only. (That is to say, only the classes
            that know for sure the logical index of the variable in the 
            encoding).
        
        :param encoding: the BeEnc responsible of this variable
        :param index: the logical index of this variable in the given encoding
        """
        self.encoding = encoding
        self.index    = index
    
    @property
    def boolean_expression(self):
        """
        :return: the boolean expression :class:`Be` used to encode this variable 
        """
        ptr = None
        if self.is_untimed:
            ptr = _be.BeEnc_index_to_var(self.encoding._ptr, self.index)
        else:
            time        = self.time
            untimed_idx = _be.BeEnc_index_to_untimed_index(self.encoding._ptr, self.index) 
            ptr = _be.BeEnc_index_to_timed(self.encoding._ptr, untimed_idx, time)
        mgr = self.encoding.manager
        return Be(ptr, mgr)
    
    @property 
    def cnf_literal(self):
        """
        :return: the cnf literal used to encode this variable in the manager.
            (this is the value of this variable in a DIMACS file)
        """
        return self.encoding.manager.be_index_to_cnf_literal(self.index)
    
    @property
    def name(self):
        """
        Returns the name of this BOOLEAN variable. If this variable was not
        declared boolean in the SMV text, this is going to be the name of one
        of the bits composing that variable. 
        
        :return: the name node corresponding to this boolean variable.
        """
        ptr = _be.BeEnc_index_to_name(self.encoding._ptr, self.untimed.index)
        return Node.from_ptr(ptr)
    
    @property
    def is_bit(self):
        """
        This property is true iff this BeVar is ONE bit of a variable. That
        is to say, if this BeVar does not denote a complete variable from the 
        SMV text because it was booleanized and encoded as a set of bits.
        
        .. note::
        
            If this property is true, then the name of this variable as it was
            declared in the SMV text can be retrieved using the `scalar` 
            property.
        
        :return: True iff this BeVar represents only one bit of a variable in 
            the SMV text.
        """
        bool_enc = self.encoding._bool_enc
        return bool(_bool.BoolEnc_is_var_bit(bool_enc, self.name._ptr))
    
    @property
    def scalar(self):
        """
        Returns the name node of this variable as it was declared in the SMV 
        text (hence not the name of the bit, but the name of the variable).
        
        .. seealso:: `is_bit`
        :return: the name node corresponding to scalar using this variable.
        """
        bool_enc = self.encoding._bool_enc
        if self.is_bit:
            scalar = _bool.BoolEnc_get_scalar_var_from_bit(bool_enc, self.name._ptr) 
            return Node.from_ptr(scalar)
        else:
            return self.name
    
    @property 
    def time(self):
        """
        :return: the time in which this variable lives
        """
        return _be.BeEnc_index_to_time(self.encoding._ptr, self.index)

    @property
    def untimed(self):
        """
        :return: the untimed variable corresponding to self. If self is already
            untimed, self is returned.
        """
        if self.is_untimed:
            return self
        else:
            idx = _be.BeEnc_index_to_untimed_index(self.encoding._ptr, self.index)
            return BeVar(self.encoding, idx)
    
    @indexed.getter
    def at_time(self, time):
        """
        :return: the timed version corresponding to this variable at `time`.
        """
        var = _be.BeEnc_index_to_timed(self.encoding._ptr, self.untimed.index, time)
        idx = _be.BeEnc_var_to_index(self.encoding._ptr, var)
        return BeVar(self.encoding, idx)
    
    @property
    def next(self):
        """
        If this variable is an untimed state variable, returns the untimed 
        next state variable corresponding to this one.
        
        Example::
            self = variable v
            self.next = next(v)
            
        :return: the untimed variable used to model self in the next state
        """
        if not self.is_untimed_current:
            raise BeWrongVarType("BeVar must be untimed current")
        var = _be.BeEnc_var_curr_to_next(self.encoding._ptr, self.boolean_expression._ptr)
        idx = _be.BeEnc_var_to_index(self.encoding._ptr, var)
        return BeVar(self.encoding, idx)
    
    @property
    def curr(self):
        """
        If this variable is an untimed next state variable, returns the untimed 
        state variable corresponding to this one.
        
        Example::
            self      = next(v)
            self.curr = v
            
        :return: the untimed variable used to model self in the current state
        """
        if not self.is_untimed_next:
            raise BeWrongVarType("BeVar must be untimed next")
        var = _be.BeEnc_var_next_to_curr(self.encoding._ptr, self.boolean_expression._ptr)
        idx = _be.BeEnc_var_to_index(self.encoding._ptr, var)
        return BeVar(self.encoding, idx)
    
    @property
    def is_valid(self):
        """
        :return: True iff self designates a valid variable
        """
        return bool(_be.BeEnc_is_var_index_valid(self.encoding._ptr, self.index))
    
    @property
    def is_state_var(self):
        """
        :return: True iff self designates a state variable
        """
        return bool(_be.BeEnc_is_index_state_var(self.encoding._ptr, self.index))
    
    @property
    def is_frozen_var(self):
        """
        Returns True iff self designates a frozen variable
        
        FROZENVAR s (frozen variables) are variables that retain their initial 
        value throughout the evolution of the state machine; this initial 
        value can be constrained in the same ways as for normal state variables.
        Similar to input variables the difference between the syntax for the 
        frozen and state variables declarations is the keyword indicating the 
        beginning of a declaration:
            frozenvar_declaration :: FROZENVAR simple_var_list
        The semantics of some frozen variable a is that of a state variable 
        accompanied by an assignment that keeps its value constant 
        (it is handled more efficiently, though):
            ASSIGN next(a) := a;
        
        .. note:: frozen vars are always untimed
        
        :return: True iff self designates a frozen variable
        """
        return bool(_be.BeEnc_is_index_frozen_var(self.encoding._ptr, self.index))
    
    @property
    def is_input_var(self):
        """
        Checks whether given index corresponds to an input variable
        
        IVAR s (input variables) are used to label transitions of the 
        Finite State Machine. The difference between the syntax for the input 
        and state variables declarations is the keyword indicating the beginning
        of a declaration:
            ivar_declaration :: IVAR simple_var_list
        
        :return: True iff self designates an input variable
        """
        return bool(_be.BeEnc_is_index_input_var(self.encoding._ptr, self.index))
    
    @property
    def is_untimed(self):
        """
        Checks whether given index corresponds to an untimed variable
        
        .. note::
            An *untimed* variable, is an 'abstract' variable that does
            not belong to any time block. It can therefore be seen as a 
            prototypical variable meant to help you retrieve the variable which 
            is actually used to model this 'variable' at some point of time in 
            a computation. That second type of variable (which are associated to 
            a time block) are therefore called *timed* variables.
            
            Even though a variable is untimed, it can be 'current' or 'next'. 
            These designations simply express the fact that within a time block,
            the current variable designates the variable before a transition is
            taken and the 'next' variable expresses the fact that it relates to
            the same variable after a transition is taken.
        
        :return: True iff self designates an untimed variable.
        """
        return bool(_be.BeEnc_is_index_untimed(self.encoding._ptr, self.index))
    
    @property
    def is_untimed_current(self):
        """
        Checks if self designates an untimed current state variable.
        
        :return: True iff self designates an untimed current state variable
        """
        return bool(_be.BeEnc_is_index_untimed_curr(self.encoding._ptr, self.index))
    
    @property
    def is_untimed_frozen(self):
        """
        Checks whether self corresponds to an untimed frozen variable.
        
        FROZENVAR s (frozen variables) are variables that retain their initial 
        value throughout the evo- lution of the state machine; this initial 
        value can be constrained in the same ways as for normal state variables.
        Similar to input variables the difference between the syntax for the 
        frozen and state variables declarations is the keyword indicating the 
        beginning of a declaration:
            frozenvar_declaration :: FROZENVAR simple_var_list
        The semantics of some frozen variable a is that of a state variable 
        accompanied by an assignment that keeps its value constant 
        (it is handled more efficiently, though):
            ASSIGN next(a) := a;
        
        .. note::
          Frozen variables are always untimed. So this function returns the same
          result as is_frozen_var
        
        :return: True iff self designates an untimed frozen variable
        """
        return bool(_be.BeEnc_is_index_untimed_frozen(self.encoding._ptr, self.index))
    
    @property
    def is_untimed_curr_frozen_input(self):
        """
        Checks whether self designates an untimed current state var,
        or an untimed frozen, or an untimed input variable
        
        IVAR s (input variables) are used to label transitions of the 
        Finite State Machine. The difference between the syntax for the input 
        and state variables declarations is the keyword indicating the beginning
        of a declaration:
            ivar_declaration :: IVAR simple_var_list
            
        FROZENVAR s (frozen variables) are variables that retain their initial 
        value throughout the evo- lution of the state machine; this initial 
        value can be constrained in the same ways as for normal state variables.
        Similar to input variables the difference between the syntax for the 
        frozen and state variables declarations is the keyword indicating the 
        beginning of a declaration:
            frozenvar_declaration :: FROZENVAR simple_var_list
        The semantics of some frozen variable a is that of a state variable 
        accompanied by an assignment that keeps its value constant 
        (it is handled more efficiently, though):
            ASSIGN next(a) := a;
        

        :return: True iff the self is either an untimed current state variable, 
            an untimed frozen variable or an untimed input variable.
        """
        return bool(_be.BeEnc_is_index_untimed_curr_frozen_input(self.encoding._ptr, self.index))
    
    @property
    def is_untimed_next(self):
        """
        Checks whether self corresponds to an untimed next state var.
        
        :return: True iff self is an untimed next state variable.
        """
        return bool(_be.BeEnc_is_index_untimed_next(self.encoding._ptr, self.index))
    
    def __eq__(self, other):
        """Performs a comparison between two variables"""
        return self.index == other.index and self.encoding == other.encoding
    
    def __hash__(self):
        """returns a value used to store this object in a hashed structure"""
        return self.index
    
    def __repr__(self):
        """returns a string representation of this variable object"""
        return "BeVar({} at time {})".format(self.name, self.time)
    
    
class BeEncUntimedVarIterator(Iterator):
    """
    This class implements an iterator meant to iterate over the untimed variables
    of the given `enc`.
    """
    def __init__(self, enc, var_type, randomized=False, random_offset=1):
        """
        Creates a new iterator
        
        :param enc: the encoding whose variables need be iterated
        :param var_type: a BeVarType (or any combination thereof) to select the 
          types of variables to consider while iterating over the vars.
        :param randomized: a flag indicating whether the iteration should be randomized
        :param random_offset: the offset to consider in random iterations
        """
        self._enc        = enc
        self._idx        = _be.BeEnc_get_first_untimed_var_index(enc._ptr,
                                                                 var_type)
        if randomized:
            self._nxt = lambda x: _be.BeEnc_get_var_index_with_offset(enc._ptr, x, random_offset, var_type)
        else:
            self._nxt = lambda x: _be.BeEnc_get_next_var_index(enc._ptr, x, var_type)
            
    def __next__(self):
        """
        Iterates over the value
        
        :return: the variable at the current position of the iterator
        :raise: StopIteration when the iteration is over.
        """
        if not _be.BeEnc_is_var_index_valid(self._enc._ptr, self._idx):
            raise StopIteration
        else:
            _ret      = BeVar(self._enc, self._idx)
            self._idx = self._nxt(self._idx)
            return _ret


class BeEnc(PointerWrapper):
    """
    Pythonic wrapper for the BE encoder  class of NuSMV.
    
    .. note::
        The timed and untimed variable notions are used a lot in the context of
        this classs. It is therefore worthwile to explain what these notions
        encompass. 
        
        An *untimed* variable, is an 'abstract' variable that does
        not belong to any time block. It can therefore be seen as a prototypical
        variable meant to help you retrieve the variable which is actually used 
        to model this 'variable' at some point of time in a computation.
        That second type of variable (which are associated to a time block) are
        therefore called *timed* variables.
        
    """

    def __init__(self, ptr, freeit=False):
        """
        Creates a new Boolean expr encoder instance wrapping the `ptr` pointer.
        
        :param ptr: the pointer to a BeEnc_ptr structure
        :param freeit: a flag indicating whether or not the resources associated
          to this encoding should be reclaimed upon garbage collection.
        """
        super().__init__(ptr, freeit=freeit)
    
    def _free(self):
        """
        Overrides PointerWrapper._free. Reclaims the memory and resources 
        allocated to this object
        """
        if self._freeit and self._ptr is not None:
            _be.BeEnc_destroy(self._ptr)
            self._freeit = False
            self._ptr    = None
    
    @property
    def _bool_enc(self):
        """
        Returns the boolean encoding which serves for the conversion to of 
        variables to bits in the underlying system.
        
        .. warning::
            
            The returned value of this property method is a plain raw SWIG
            pointer wrapper. This property is for INTERNAL USE ONLY !!
            
        :return: a swig pointer corresponding to the bool enc used by this 
            encoder.
        """
        return _be.BeEnc_ptr_get_bool_enc(self._ptr)
    
    @staticmethod
    def global_singleton_instance():
        """
        Currently, in NuSMV, the be_enc is a singleton global private variable 
        which is shared between all the BE FSMs. 
        
        :return: the global singleton be_encoder instance
        :raises NuSMVBeEncNotInitializedError: if the global encoding is not 
            initialized
        """
        encoding_ptr = _enc.Enc_get_be_encoding()
        if encoding_ptr is None:
            raise NuSMVBeEncNotInitializedError("be_encoding not initialized")
        return BeEnc(encoding_ptr, freeit=False) 
    
    # =========================================================================
    # ========== Getters ======================================================
    # =========================================================================
    @property
    def symbol_table(self):
        """:return: the symbol table used by this encoder"""
        _casted = _be.BeEnc_ptr_to_BaseEnc_ptr(self._ptr)
        return SymbTable(_base.BaseEnc_get_symb_table(_casted))
    
    @property
    def manager(self):
        """
        :return: the Boolean Expressions manager (:class:`BeManager`) 
          contained into the variable manager, to be used by any operation on 
          BEs
        """
        if not hasattr(self, "__manager"):
            setattr(self, '__manager', BeRbcManager(_be.BeEnc_get_be_manager(self._ptr)))
        return getattr(self, '__manager')
    
    @property
    def max_time(self):
        """:return: the maximum allocated time"""
        return _be.BeEnc_get_max_time(self._ptr)
    
    @property
    def num_of_vars(self):
        """
        :return: number of input and state variables currently handled by the 
          encoder
        """
        return _be.BeEnc_get_vars_num(self._ptr)
    
    @property
    def num_of_state_vars(self):
        """
        Returns the number of state variables in the encoded model.
        
        A state of the model is an assignment of values to a set of state and 
        frozen variables. State variables (and also instances of modules) are 
        declared by the notation:
        
            var_declaration :: VAR var_list
        
        :return: number of state variables currently handled by the encoder
        """
        return _be.BeEnc_get_state_vars_num(self._ptr)
    
    @property
    def num_of_frozen_vars(self):
        """
        Returns the number of frozen variables in the encoded model.
        
        FROZENVAR s (frozen variables) are variables that retain their initial 
        value throughout the evo- lution of the state machine; this initial 
        value can be constrained in the same ways as for normal state variables.
        Similar to input variables the difference between the syntax for the 
        frozen and state variables declarations is the keyword indicating the 
        beginning of a declaration:
        
            frozenvar_declaration :: FROZENVAR simple_var_list
        
        The semantics of some frozen variable a is that of a state variable 
        accompanied by an assignment that keeps its value constant 
        (it is handled more efficiently, though):
        
            ASSIGN next(a) := a;

        :return: number of frozen variables currently handled by the encoder
        """
        return _be.BeEnc_get_frozen_vars_num(self._ptr)
    
    @property
    def num_of_input_vars(self):
        """
        Returns the number of input variables in the encoded model.
        
        IVAR s (input variables) are used to label transitions of the 
        Finite State Machine. The difference between the syntax for the input 
        and state variables declarations is the keyword indicating the beginning
        of a declaration:
        
            ivar_declaration :: IVAR simple_var_list

        :return: number of input variables currently handled by the encoder
        """
        return _be.BeEnc_get_input_vars_num(self._ptr)
    
    def iterator(self, var_type=BeVarType.ALL, randomized=False, rnd_offset=1):
        """
        :return: an iterator to walk through all the untimed variables
        
        :param var_type: the kind of variables to be taken into account while
          iterating
        :param randomized: a flag indicating whether or not the variables should
          be walked in a random order.
        :param rnd_offset: the random offset to use when iterating in random
          order
        """
        return BeEncUntimedVarIterator(self, var_type, randomized, rnd_offset)
    
    def __iter__(self):
        """
        Magic method to provide an iterator (iterates over untimed variables)
        """
        return self.iterator()
    
    @indexed.getter
    def at_index(self, index):
        """
        Returns the variable encoded at the given logical index.
        
        :param index: the index of the variable to access
        :return: the variable at `index` (may not be valid)  
        :raises ValueError: when the index is not legal (<0)
        """
        if index < 0:
            raise ValueError("Index needs to be >= 0")
        return BeVar(self, index)
    
    @indexed.getter
    def by_name(self, name_str):
        """
        Returns an untimed variable (Be) corresponding to the given name
        
        :param name_str: a string representing the name (in string format, not 
                         node) of the untimed variable to be fetched
        :return: the Be representing the variable if it was found
        :raise: KeyError if the variable could not be found.
        """
        for v in self.iterator():
            if str(v.name) == name_str:
                return v
        raise KeyError("{} not found".format(name_str))
    
    @indexed.getter
    def by_expr(self, expr):
        """
        Returns the value of the variable corresponding to the given Be 
        expression (which should denote a variable only)
        
        :return: the variable corresponding to expr. (may be timed or not) 
        :raise KeyError: when the given expression looked up does not denote
            a variable
        """
        index = _be.BeEnc_var_to_index(self._ptr, expr._ptr)
        if index == -1:
            raise KeyError("The given expression does not denote a variable")
        return BeVar(self, index)
    
    @property
    def untimed_variables(self):
        """
        Returns the list of all the untimed variable
        
        :return: the list of (all) untimed variables
        """
        return [v for v in self.iterator()]
    
    @property
    def curr_variables(self):
        """
        Returns the list of all the (untimed) current state variables
        
        :return: the list of the current state untimed variables
        """
        return [v for v in self.iterator(BeVarType.CURR)]
    
    @property
    def frozen_variables(self):
        """
        Returns the list of the frozen variables.
        
        FROZENVAR s (frozen variables) are variables that retain their initial 
        value throughout the evo- lution of the state machine; this initial 
        value can be constrained in the same ways as for normal state variables.
        Similar to input variables the difference between the syntax for the 
        frozen and state variables declarations is the keyword indicating the 
        beginning of a declaration:
        
            frozenvar_declaration :: FROZENVAR simple_var_list
            
        The semantics of some frozen variable a is that of a state variable 
        accompanied by an assignment that keeps its value constant 
        (it is handled more efficiently, though):
        
            ASSIGN next(a) := a;
        
        :return: the list of the frozen variables
        """
        return [v for v in self.iterator(BeVarType.FROZEN)]
    
    @property
    def input_variables(self):
        """
        Returns the list of the (untimed) input variables
        
        IVAR s (input variables) are used to label transitions of the 
        Finite State Machine. The difference between the syntax for the input 
        and state variables declarations is the keyword indicating the beginning
        of a declaration:
        
            ivar_declaration :: IVAR simple_var_list
        
        :return: the list of the (untimed) input variables
        """
        return [v for v in self.iterator(BeVarType.INPUT)]
    
    @property
    def next_variables(self):
        """:return: the list of the (untimed) next state variables"""
        return [v for v in self.iterator(BeVarType.NEXT)]
    
    # =========================================================================
    # ========== Shift operations are the one to use to implement unrolling ===
    # =========================================================================
    def shift_curr_to_next(self, expr):
        """
        Returns an *untimed* Be expression corresponding to `expr` in which all 
        variables v have been shifted to next(v). Example:
            
            v == True & w == False becomes next(v) == True & next(w) == False
        
        .. note::
            Despite the fact that this operation performs a shift of the 
            variables it remains in the *untimed* block. (next of untimed vars 
            are also untimed vars). Hence the returned expression is an *untimed*
            expression. Therefore, in order to use it in (ie a transition 
            relation unrolling), it must be shifted again to a time block using
            one of :
            
                - :meth:`shift_to_time`
                - :meth:`shift_to_times`
                - :func:`or_interval`
                - :func:`and_interval`
        
        .. warning:: 
            argument 'expr' must contain only untimed current state variables 
            and untimed frozen variables, otherwise results will be 
            unpredictable. Unfortunately, there is no way to preemptively check
            that a given expression contains only untimed variable so it is up
            to the programmer to make sure he calls this method in an 
            appropriate way.
        
        :param expr: the expression to shift
        :return: an expression equivalent to expr but with the variables shifted
            to the next-state portion of the block.
        """
        ptr = _be.BeEnc_shift_curr_to_next(self._ptr, expr._ptr)
        return Be(ptr, self.manager)
    
    def shift_to_time(self, expr, time):
        """
        Returns a *timed* Be expression corresponding to `expr` in which all 
        variables v have been shifted to the given `time` block. Natually, the
        variables of the `next` sub-block are shifted to time t+1 (which 
        corresponds to what one would intuitively expect). 
            
        .. warning:: 
            argument 'expr' must contain only untimed current state variables 
            and untimed frozen variables, otherwise results will be 
            unpredictable. Unfortunately, there is no way to preemptively check
            that a given expression contains only untimed variable so it is up
            to the programmer to make sure he calls this method in an 
            appropriate way. 
        
        :param expr: the expression to shift
        :param time: the time to shift the expression to
        :return: an expression equivalent to `expr` but with the variables 
            shifted to the given `time` block.
        """
        ptr = _be.BeEnc_untimed_expr_to_timed(self._ptr, expr._ptr, time)
        return Be(ptr, self.manager)
    
    def shift_to_times(self, expr, curr_time, frozen_time, ivar_time, next_time):
        """
        Returns a *timed* Be expression corresponding to `expr` in which:
        
            - all the current state variables are shifted to time `curr_time`
            - all the frozen variables are shifted to time `frozen_time`
            - all the input variables are shifted to time `ivar_time`
            - all the next state variables are shifted to time `next_time`
            
        .. warning:: 
            argument 'expr' must contain only untimed current state variables 
            and untimed frozen variables, otherwise results will be 
            unpredictable. Unfortunately, there is no way to preemptively check
            that a given expression contains only untimed variable so it is up
            to the programmer to make sure he calls this method in an 
            appropriate way. 
        
        :param expr: the expression to shift
        :param curr_time: the time to shift the current variables to
        :param frozen_time: the time to shift the frozen variables to
        :param ivar_time: the time to shift the input variables to
        :param next_time: the time to shift the next state variables to.
        :return: an expression equivalent to `expr` but with the sets of 
            variables shifted to the time blocks.
        """
        ptr = _be.BeEnc_untimed_expr_to_times(self._ptr, 
                                              expr._ptr, 
                                              curr_time,
                                              frozen_time, 
                                              ivar_time, 
                                              next_time)
        return Be(ptr, self.manager)
    
    def and_interval(self, expr, start, end):
        """
        This method is an utility meant to let you easily compute the 
        conjunction of the given `expr` shifted at all the times in the interval
        [start, end]. Mathematically, this corresponds to the following formula:
        
        .. math:: 
            \\underset{t=start}{\\overset{t=end}{\\bigwedge}} shift\\_to\\_time(expr, t)
        """
        ptr = _be.BeEnc_untimed_to_timed_and_interval(self._ptr, 
                                                      expr._ptr, 
                                                      start, 
                                                      end)
        return Be(ptr, self.manager)
    
    def or_interval(self, expr, start, end):
        """
        This method is an utility meant to let you easily compute the 
        disjunction of the given `expr` shifted at all the times in the interval
        [start, end]. Mathematically, this corresponds to the following formula:
        
        .. math:: 
            \\underset{t=start}{\\overset{t=end}{\\bigvee}} shift\\_to\\_time(expr, t)
        """
        ptr = _be.BeEnc_untimed_to_timed_or_interval(self._ptr, 
                                                      expr._ptr, 
                                                      start, 
                                                      end)
        return Be(ptr, self.manager)
    
    def encode_to_bits(self, name_node):
        """
        Returns the list of bits variable names used to encode the SMV variable
        denoted by `name_node` in the boolean model.
        
        :param name_node: the node symbol representing the expression to break
            down to bits.
        :return: the list of bits names (in the form of nodes) which are used
            to encode `name_node`.
        """
        try:
            # raises a KeyError when 'name' is not found
            self.by_name[str(name_node)]
            # if found, its ok to just use 'symbol'
            return [name_node]
        except KeyError:
            # the encoder doesn't know 'name' we need to find the bits
            boolenc = self._bool_enc
            node_lst= NodeList(_bool.BoolEnc_get_var_bits(boolenc, name_node._ptr))
            return list(node_lst)
    
    def decode_value(self, list_of_bits_and_value):
        """
        Returns a node (:class:`pynusmv.node.Node`) corresponding to the value of
        the variable encoded by the list of bits and values.
        
        :param list_of_bits_and_value: a sequence of tuples (BeVar, BooleanValue)
            which represent a bit and its value.
        :return: an intelligible value node corresponding to what these bits
            means when interpreted in the context of the SMV model.
        """
        if not list_of_bits_and_value:
            raise ValueError("The given list of bits and values must at least "+
                             "contain one bit")
        # if the variable to be decoded is boolean in the model 
        if not list_of_bits_and_value[0][0].is_bit:
            return list_of_bits_and_value[0][1]
        
        # otherwise decode the bits
        bool_enc = self._bool_enc
        scalar   = list_of_bits_and_value[0][0].scalar
        
        bv = _bool.BitValues_create(bool_enc, scalar._ptr)
        for bit,val in list_of_bits_and_value:
            bit_index = _bool.BoolEnc_get_index_from_bit(bool_enc, bit.name._ptr)
            _bool.BitValues_set(bv, bit_index, val)
            
        result_ptr = _bool.BoolEnc_get_value_from_var_bits(bool_enc, bv)
        
        _bool.BitValues_destroy(bv)
        return Node.from_ptr(result_ptr)
    
    def decode_sat_model(self, sat_model):
        """
        Decodes the given `sat_model` and translates it in a sequence of 
        valuations. Concretely, the returned value is a multi-level dictionary
        with the following structure: time_block -> scalar_name -> decoded_value
        
        :param sat_model: the dimacs model generated by a sat solver to satisfy
            some given property.
        :return: a multi-level map time_block -> scalar_name -> decoded_value
            representing the content of the sat_model
        """
        mgr = self.manager
        
        def _to_var_value(x):
            """Internal function, converts dimacs literal to a variable"""
            try:
                k = self.at_index[mgr.cnf_literal_to_index(abs(x))]
                v = x > 0
                return (k,v)
            except:
                return (None,None)
        
        def _group_by_time(valuation):
            """Internal function, groups the variables in time blocks"""
            result = {}
            for k,v in valuation:
                if k is None:
                    continue
                if k.time not in result:
                    result[k.time] = []    
                result[k.time].append((k, v))
            return result
        
        def _group_by_scalar(timed):
            """
            Internal function, inside each block, group bits by scalar to which
            they relate
            """
            result = {}
            for tm in timed.keys():
                result[tm] = {}
                for var,value in timed[tm]:
                    scalar = str(var.scalar)
                    if scalar not in result[tm]:
                        result[tm][scalar] = [(var, value)]
                    else:
                        result[tm][scalar].append((var,value))
            return result
        
        def _decode(by_time_and_scalar):
            """
            Internal function, decodes the bits of each scalar var within each
            time block
            """
            result = {}
            for tm in by_time_and_scalar.keys():
                result[tm] = {}
                for scalar in by_time_and_scalar[tm].keys(): 
                    result[tm][scalar] = self.decode_value(by_time_and_scalar[tm][scalar])
            return result
        
        # use the above internal functions
        valuation = [_to_var_value(x) for x in sat_model]
        by_time   = _group_by_time(valuation)
        by_scalar = _group_by_scalar(by_time)
        decoded   = _decode(by_scalar)
               
        return decoded
    
    # =========================================================================
    # ========== Magic methods ======================================================
    # =========================================================================
    
    def __eq__(self, other):
        """
        Performs a comparison between two encodings
        
        .. warning:: 
            The comparison is made using the underlying pointers.
            So the comparison is more of an identity test than
            a true equality.
        
        :return: True iff self == other
        """
        return self._ptr == other._ptr
    
    def __hash__(self):
        """returns a value used to store this object in a hashed structure"""
        return self._ptr
    
    def __str__(self):
        """
        Returns a string representation of this encoder
        """
        res = self._str_header()    
        for time in range(self.max_time+1):
            res += self._str_time(time)
        return res
    
    def _str_header(self):
        """
        Returns the header of the string representation of the encoder
        """
        result = "+--------------+----------------+---------------+\n"
        result+= "| Time steps from 0 to {:6d}                   |\n"
        result+= "+--------------+----------------+---------------+\n"
        result+= "| # State Vars |  # Frozen Vars |  # Input Vars |\n"
        result+= "+--------------+----------------+---------------+\n"
        result+= "| {:12d} | {:14d} | {:13d} |\n"
        result+= "+--------------+----------------+---------------+\n"
        return result.format(
                    self.max_time, 
                    self.num_of_state_vars, 
                    self.num_of_frozen_vars, 
                    self.num_of_input_vars)
        
    def _str_time(self, t):
        """
        Returns a string representation of a time block (variables at a given
        time)
        """
        result = "@@@@@@@@@@@@@@@@@@@ Time {:3d} @@@@@@@@@@@@@@@@@@@@\n".format(t)
        result+= "+----------+-----------+-------+----------------+\n"
        result+= "| Be index | Cnf index |  Time | Model variable |\n"
        result+= "+----------+-----------+-------+----------------+\n"
        for v in self.untimed_variables:
            timed = v.at_time[t]
            result +="| {:8d} | {:9d} | {:5d} | {:14s} |\n".format(
                                            timed.index, 
                                            timed.cnf_literal, 
                                            timed.time, 
                                            str(v.name))
        result+= "+----------+-----------+-------+----------------+\n"
        return result