"""
The module :mod:`pynusmv.trace` defines the classes :class:`Trace` and 
:class:`TraceStep` which serve the purpose of representing traces (executions) 
in a PyNuSMV model.

For instance, these classes are used to represent a counter example in the scope
of LTL verification via bounded model checking.
"""

from enum                import IntEnum
from _collections_abc    import Iterable

from pynusmv_lower_interface.nusmv.trace import trace as _trace

from pynusmv.utils       import PointerWrapper, indexed
from pynusmv.node        import Node 
from pynusmv.fsm         import SymbTable
from pynusmv.collections import NodeList
from pynusmv.exception   import NuSmvIllegalTraceStateError

class TraceType(IntEnum):
    """
    The possible types of traces
    """
    UNSPECIFIED     = _trace.TRACE_TYPE_UNSPECIFIED,
    COUNTER_EXAMPLE = _trace.TRACE_TYPE_CNTEXAMPLE,
    SIMULATION      = _trace.TRACE_TYPE_SIMULATION,
    EXECUTION       = _trace.TRACE_TYPE_EXECUTION,
    END             = _trace.TRACE_TYPE_END
    
    def __str__(self):
        """:return: a string representation of this trace type"""
        return _trace.TraceType_to_string(self)

class Trace(PointerWrapper, Iterable):
    """
    Encapsulates the details of a counter example trace.
    """
    
    def __init__(self, ptr, freeit=False):
        super().__init__(ptr, freeit=freeit)
        
    def _free(self):
        if self._freeit and self._ptr is not None:
            _trace.Trace_destroy(self._ptr)
            self._ptr = None
            self._freeit = False
            
    @staticmethod
    def create(description, trace_type, symb_table, symbols_list, is_volatile):
        """
        Creates a new (empty trace)
        
        :param description: a text describing what the trace is describing
        :param trace_type: an enumeration value (:class:`TraceType`) describing
            how the trace should be interpreted
        :param symb_table: the symbol table used to associate an human
            meaningful symbol to the internal representation of the trace
        :param symb_list: a NodeList (:class:`pynusmv.collections.NodeList`) 
            containing the various symbols that may appear in the trace.
            Note, this is not a regular python list but you can obtain a NodeList
            using `NodeList.from_list` if you need to. In case you just use
            SexpFsm (:func:`pynusmv.sexp.fsm.SexpFsm.symbols_list`) then no
            conversion is required as it already yields a NodeList
        :param is_volatile: a flag indicating whether or not the created insrance
            should be responsible of the symbol table reference it owns
        """
        ptr = _trace.Trace_create(symb_table._ptr, 
                                  description, 
                                  trace_type, 
                                  symbols_list._ptr, 
                                  is_volatile)
        return Trace(ptr, freeit=True)
    
    def concat(self, other):
        """
        Concatenates all the content from `other` to self and destroys other.
        
        .. warning::
            
            The initial state of `other` is not copied over to self.
        
        :param other: the other trace to append to self 
        """
        if other.is_registered:
            raise NuSmvIllegalTraceStateError("Cannot concat a registered trace")
        _trace.Trace_concatenate(self._ptr, other._ptr)
        # This function is DESTRUCTIVE !
        other._ptr = None
        other._freeit = False
        return self
    
    @property
    def id(self):
        """
        An unique identifier for this trace (a non-negative number)
        
        :return: an unique identifier for this trace
        """
        return _trace.Trace_get_id(self._ptr) 
    
    @property
    def description(self):
        """:return: this trace description in a human friendly format"""
        return _trace.Trace_get_desc(self._ptr)
    
    @description.setter
    def description(self, desc):
        """
        Sets a new description to explain what this trace is about
        
        :param desc: the new description value
        """
        _trace.Trace_set_desc(self._ptr, desc)
    
    @property
    def type(self):
        """
        Returns the TraceType (:class:`TraceType`) explaining how this
        trace should be interpreted
        
        :return: the trace type of this trace
        """
        return TraceType(_trace.Trace_get_type(self._ptr))
    
    @type.setter
    def type(self, trace_type):
        """
        Sets the type of this trace (a value explaining how to interpret this
        trace (:class:`TraceType`).
        
        :param trace_type: the new trace type
        """
        _trace.Trace_set_type(self._ptr, trace_type)
        
    @property
    def length(self):
        """
        Length for a trace is defined as the number of the transitions in it. 
        Thus, a trace consisting only of an initial state is a 0-length trace. 
        A trace with two states is a 1-length trace and so forth.
               
        :return: the length of this trace
        """
        return _trace.Trace_get_length(self._ptr)
    
    def __len__(self):
        """:return: the length of this trace (using the built in function)"""
        return self.length
    
    @property
    def is_empty(self):
        """
        Tests this trace for emptiness
        
        :return: True iff this trace is empty (that is to say it has length==0)
        """
        return bool(_trace.Trace_is_empty(self._ptr))
        
    @property
    def is_volatile(self):
        """
        A trace is volatile if it is not the owner of its symbol table reference
        
        :return: a flag indicating whether or not the trace is volatile
        """
        return bool(_trace.Trace_is_volatile(self._ptr)) 
        
    @property
    def is_registered(self):
        """
        :return: true iff the trace is registered with a trace manager
        """
        return bool(_trace.Trace_is_registered(self._ptr))
    
    def register(self, identifier):
        """
        sets the id of the trace (to be called by the trace manager when the
        trace gets registered in that context)
        
        :param identifier: an id for this trace
        """
        _trace.Trace_register(self._ptr, identifier)
        
    def unregister(self):
        """
        De-associates this trace from the trace manager it was previously 
        registered with
        """
        _trace.Trace_unregister(self._ptr)
        
    @property
    def is_frozen(self):
        """
        A frozen trace holds explicit information about loopbacks and can not 
        be appended a step, or added a variable value.

        .. warning::
        
            After freezing no automatic looback calculation will be performed: 
            it is up to the owner of the trace to manually add loopback 
            information.
            
        :return: True iff this trace is frozen.
        """
        return bool(_trace.Trace_is_frozen(self._ptr))
    
    def freeze(self):
        """
        Forces this trace to enter the frozen state so as to be able to add
        loopback information on this trace.
        
        A frozen trace holds explicit information about loopbacks. Its length 
        and assignments are immutable, that is it cannot be appended more steps,
        nor can it accept more values that those already stored in it.

        Still it is possible to register/unregister the trace and to change its
        type or description.
        
        .. warning::
        
            After freezing no automatic looback calculation is performed: it is
            up to the owner of the trace to manually add loopback information.
        """
        _trace.Trace_freeze(self._ptr)
    
    @property
    def is_thawed(self):
        """
        A thawed trace holds no explicit information about loopbacks and can be 
        appended a step or added a variable value.
        
        .. note::
            
            As the name suggests, thawed <-> ! frozen.

        .. warning:: 
        
            After thawing the trace will not persistently retain any loopback 
            information. In particular it is *illegal* to force a loopback on 
            a thawed trace.
        """
        return bool(_trace.Trace_is_thawed(self._ptr))
    
    def thaw(self):
        """
        Forces this trace to enter the thawed state so as to enable the 
        addition of steps or variables.
        
        .. note::
            
            As the name suggests, thawed <-> ! frozen.
            
        
        .. warning:: 
        
            After thawing the trace will not persistently retain any loopback 
            information. In particular it is *illegal* to force a loopback on 
            a thawed trace.
        """
        _trace.Trace_thaw(self._ptr)
    
    def equals(self, other):
        """
        Two traces are equals iff:

        1. They're the same object or None.
        2. They have exactly the same language, length, assignments for all 
           variables in all times and the same loopbacks.

                 (Defines are not taken into account for equality.)

        .. note:: 
        
            In order to be considered equal, the two traces need not be both 
            frozen/thawed, and to both have the same registration status. 
            (Of course two traces *cannot* have the same ID).
            
        .. warning::
        
            This test implements an 'equals logic', not an 'is same' logic 
            since the id field of the trace is not considered in the comparison.
            
            Hence, this equality test is inconsistent with the result of __hash__
        """
        if other is None: 
            return False
        return bool(_trace.Trace_equals(self._ptr, other._ptr))
    
    def __eq__(self, other):
        """
        Magic method to perform an equality test
        
        .. warning::
        
            This test implements an 'equals logic', not an 'is same' logic 
            since the id field of the trace is not considered in the comparison.
            
            Hence, this equality test is inconsistent with the result of __hash__
        """
        return self.equals(other)
    
    def append_step(self):
        """
        Creates and return a new step which is appended to the current trace
        
        :return: a new trace step which corresponds to the last step of the 
            trace.
        """
        return TraceStep(self, _trace.Trace_append_step(self._ptr))
    
    @property
    def symbol_table(self):
        """:return the symbol table associated to this trace"""
        return SymbTable(_trace.Trace_get_symb_table(self._ptr))
    
    @property
    def symbols(self):
        """
        Returns a NodeList (:class:`pynusmv.collections.NodeList`)
        exposing the symbols of the trace language.
        
        :returns: a NodeList exposing the symbols of the trace language
        """
        return NodeList(_trace.Trace_get_symbols(self._ptr))
    
    @property
    def state_vars(self):
        """
        Returns a NodeList  (:class:`pynusmv.collections.NodeList`)
        exposing the state variables that exist in the trace language
        
        :return: a NodeList containing the state variables of the trace language
        """
        return NodeList(_trace.Trace_get_s_vars(self._ptr))
    
    @property
    def state_frozen_vars(self):
        """
        Returns a NodeList  (:class:`pynusmv.collections.NodeList`)
        exposing the state and frozen variables that exist in the trace language
        
        :return: a NodeList containing the state and frozen variables of the 
            trace language
        """
        return NodeList(_trace.Trace_get_sf_vars(self._ptr))
    
    @property
    def input_vars(self):
        """
        Returns a NodeList  (:class:`pynusmv.collections.NodeList`)
        exposing the input variables that exist in the trace language
        
        :return: a NodeList containing the input variables of the trace language
        """
        return NodeList(_trace.Trace_get_i_vars(self._ptr))
    
    def language_contains(self, symbol_node):
        """
        Tests whether the given symbol represented by `symbol_node` 
        (:class:`pynusmv.node.Node`) belongs to the trace language.
        
        .. note::
        
            A more pythonic accessor is foreseen for the same purpose. If you
            prefer, you may perfectly use `symb_node` in `self` to get the
            exact same result. 
            
        :returns: True iff this symbol_node belongs to the trace language.
        """
        return bool(_trace.Trace_symbol_in_language(self._ptr, symbol_node._ptr))
    
    def __contains__(self, symbol_node):
        """
        Tests whether the given symbol represented by `symbol_node` 
        (:class:`pynusmv.node.Node`) belongs to the trace language.
        
        :returns: True iff this symbol_node belongs to the trace language.
        """
        return self.language_contains(symbol_node)
    
    def is_complete(self, vars_nlist, report=False):
        """
        Checks if a Trace is complete on the given set of vars
        
        A Trace is complete iff in every node, all vars are given a value

        .. note::

                * Only input and state section are taken into account.
                  Input vars are not taken into account in the first
                  step. Defines are not taken into account at all.
                * If result is false and parameter 'report' is true
                  then a message will be output in nusmv_stderr with
                  some explanation of why the trace is not complete
                
        :param vars_nlist: a NodeList of variable symbols that need to have a
            value in order for the trace to be considered complete.
            (:class:`pynusmv.collections.NodeList`)
            
        :return: True iff the trace has a value associated to each of the vars
            in vars_nlist.
        """
        return bool(_trace.Trace_is_complete(self._ptr, vars_nlist._ptr, report))

    def __iter__(self):
        """Iterator that permits an easy navigation in the steps of the trace"""
        for i in range(1, len(self)+2):
            yield self.steps[i]
    
    @indexed.getter
    def steps(self, i):
        """
        Returns the ith step of the trace
        
        .. warning::
        
            the indices start at 1
        
        :param i: the index/time of the step to fetch
        :return: the ith step of this trace
        """
        if i < 1 or i > self.length+1:
            raise KeyError("step index not in the range [0; {}]".format(len(self)+1))
        return TraceStep(self, _trace.Trace_ith_iter(self._ptr, i))
    
    def __repr__(self):
        """
        Returns a string representation of this object.
        """
        text ="""******************************************************\n"""
        text+= "{} : {}\n".format(str(self.type), self.description)
        for step in self:
            text+= str(step)
        return text
    # NOTE: covers language does not exist in the C code.
    #       public api for symbol_is_assigned not found in C code either


class TraceStep:
    """
    Encapsulates the details of what step is in a trace. In the context of a 
    trace, a step is considered to be a container for incoming input and next
    state (i.e. it has the form <i, S>)
    """
    
    def __init__(self, trace, step_ptr):
        """
        Creates a new instance
        
        :param trace: the parent trace (the one to which this step belongs to)
        :param step_ptr: a swig wrapper to the unerlying NuSMV pointer 
            representing this step (:type: `TraceIter`)
        """
        self.trace = trace
        self._ptr  = step_ptr
        
    @property
    def is_loopback(self):
        """
        Tests whether the state denoted by this step is a loopback state w.r.t 
        the last state in the parent trace.
        
        This function behaves accordingly to two different modes a trace  can 
        be: frozen or thawed(default).

        If the trace is frozen, permanent loopback information is used to 
        determine if this step has a loopback state and no further loopback 
        computation is made.
        
        If the trace is thawed, dynamic loopback calculation takes place, using
        a variant of Rabin-Karp pattern matching algorithm.
        
        .. note::
        
            No matter the configuration, the last step of a trace is always 
            seen as *NOT* being a loopback step.
        """
        return bool(_trace.Trace_step_is_loopback(self.trace._ptr, self._ptr))
    
    def force_loopback(self):
        """
        Forces this step to be considered as a loopback step using explicit 
        loopback information (trace must be frozen)
        
        Use this function to store explicit loopback information in a frozen 
        trace. The trace will retain loopback data until it is thawed again.
        
        :raises NuSmvIllegalTraceStateError: if the parent trace is not frozen
        """
        if not self.trace.is_frozen :
            raise NuSmvIllegalTraceStateError(
                    """
                    The parent trace must be frozen before explicit loopback 
                    information can be used
                    """)
        
        _trace.Trace_step_force_loopback(self.trace._ptr, self._ptr)
    
    def assign(self, symbol_node, value_node):
        """
        Stores an assignment into a trace step
        
        .. warning::
        
            Assignments to symbols not in trace language are silently ignored.
        
        
        :param symbol_node: a Node (:class:`pynusmv.node.Node`) 
            representing the symbol to which a value is assigned
        :param value_node: a Node (:class:`pynusmv.node.Node`)
            representing the value being assigned to the symbol
        
        :return: true iff the assignment worked smoothly.
        
        :raises NuSmvIllegalTraceStateError: if the parent trace is frozen
        """   
        if self.trace.is_frozen:
            raise NuSmvIllegalTraceStateError(
                        """
                        The parent trace must be thawed before any assignment
                        can be added to this trace step.
                        """)
        return bool(_trace.Trace_step_put_value(self.trace._ptr,
                                                self._ptr, 
                                                symbol_node._ptr, 
                                                value_node._ptr))
        
    def __iadd__(self, assignment):
        """
        Stores an assignment into a trace step
        
        .. note::
        
            Assignments to symbols not in trace language are silently ignored.
        
        :param assignment: is a tuple composed of a symbol_node (:class:`pynusmv.node.Node`)
            representing the symbol to which an assignment is made and a
            value_node (:class:`pynusmv.node.Node`) representing the value being
            assigned to the symbol.
            
        :raises NuSmvIllegalTraceStateError: if the parent trace is frozen
        """
        self.assign(assignment[0], assignment[1])
        return self
        
    @indexed.getter
    def value(self, symbol_node):
        """
        Retrieves the value that was assigned to `symbol_node` in the current
        trace step.
        
        :param symbol_node: a Node (:class:`pynusmv.node.Node`) 
            representing the symbol to which a value is assigned
        :return: a value_node, that is to say a Node (:class:`pynusmv.node.Node`)
            representing the value being assigned to the requested symbol.   
        """
        return Node.from_ptr(_trace.Trace_step_get_value(
                                            self.trace._ptr, 
                                            self._ptr, 
                                            symbol_node._ptr))
        
    def __iter__(self):
        """
        :return: an iterator to iterate over the variables symbols of this step
        """
        # NuSMV advises not to use Trace_step_iter. This implementation is safer
        # and works well
        for sym in self.trace.symbols:
            value = self.value[sym]
            if value is not None:
                yield (sym, value)
    
    def __repr__(self):
        """
        Returns a string representation of this object.
        """
        text = """****** Step ******* is_loopback : [{}] ****************\n""".\
                                        format("V" if self.is_loopback else " ")
                                        
        for symbol, value in self:
            text += "{} = {}\n".format(symbol, value)
        text +="""******************************************************\n"""
        return text

    def __eq__(self, other):
        """
        Equality test between two objects. 
        
        .. warning::
        
            Beware it uses the pointer to implement the hashing function.  
            So it is IDENTITY dependent (in C) and not value dependant.
        
        :return: True iff the two object are the same
        """
        return self._ptr == other._ptr
    
    def __hash__(self):
        """
        Makes this object hashable. 
        
        .. warning::
        
            Beware it uses the pointer to implement the hashing function.  
            So it is IDENTITY dependent (in C) and not value dependant.
        
        :return: an object that can serve as key to perform the lookup in a dict.
        """
        return self._ptr