'''
This module implements wrappers around the NuSMV list types:

* :class:`Slist` which represents a singly linked list as used in many internal 
         functions of NuSMV
* :class:`NodeList` which is a wrapper for NuSMV's internal NodeList class
* :class:`Assoc` which stands for NuSMV's internal associative array 
         (hash_ptr and st_table*) 
'''
from collections import Iterator, Iterable

from pynusmv_lower_interface.nusmv.utils import utils as _utils
from pynusmv_lower_interface.nusmv.node  import node as _node
from pynusmv.utils import PointerWrapper
from pynusmv.node  import Node

__all__ = ['Conversion', 'IntConversion', 'NodeConversion',
           'Slist', 'SlistIterator', 'Sentinel', 'NodeIterator', 'NodeList', 
           'NodeListIter', 'Assoc' ]

#===============================================================================
#====== Utility common to all collections ======================================
#===============================================================================
class Conversion:
    """
    This class wraps the functions used to perform the back and forth conversion
    between types of the the lower interface (pointers) and types of the higher 
    interface (python objects)
    """
    def __init__(self, p2o, o2p):
        """
        Creates a new instance of the encapsulated conversion
        :param p2o: the conversion fn to convert (pointer -> object )
        :param o2p: the conversion fn to convert (object  -> pointer)
        """
        self._p2o = p2o
        self._o2p = o2p
        
    def to_object(self, pointer):
        """
        Returns an higher level (and meaningful) representation of `pointer`
        
        :param pointer: a raw (low level) pointer that needs to be mapped to
           something more meaningful
        :return: an higher level (and meaningful) representation of `pointer`
        """ 
        return self._p2o(pointer)
    
    def to_pointer(self, obj):
        """
        Returns a low level pointer representing `obj`
        
        :param obj: an high level object that needs to be translated to a C pointer
        :return: a low level pointer representing `obj` 
        """
        return self._o2p(obj)


class IntConversion(Conversion):
    """
    A conversion object able to wrap/unwrap int to void* and vice versa
    """
    def __init__(self):
        """Creates a new IntConversion"""
        # void* -> int
        p2i = lambda p: _utils.void_star_to_int(p)
        # int -> void*
        i2p = lambda i: _utils.int_to_void_star(i)
          
        super().__init__(p2i, i2p)

class NodeConversion(Conversion):
    """
    A conversion object able to wrap/unwrap Node to void* and vice versa
    """
    def __init__(self):
        """Creates a simple node conversion"""
        p2n = lambda x: Node.from_ptr(x)
        n2p = lambda x: x._ptr
        super().__init__(p2n, n2p)

#===============================================================================
#====== SList related types ====================================================
#===============================================================================
class Slist(PointerWrapper, Iterable):
    """
    This class implements an high level pythonic interface to Slist which is a
    NuSMV-defined simply linked list.
    
    Although this type is implemented in C, some of its operation have a slow
    O(n) performance. For instance the __getitem__ and __delitem__ which 
    correspond to x = lst[y] and del lst[z] are O(n) operation despite their
    indexed-looking syntax. In case many such operations are required or 
    whenever you need more advanced list operations, you are encouraged to cast
    this list to a builtin python list with the list(lst) operator. The inverse
    conversion is possible using Slist.fromlist(lst) but requires however to
    provide the element conversion as an object of type util.Conversion
    """
    
    def __init__(self, ptr, conversion, freeit=True):
        """
        Creates a new Slist from the given `ptr` using the provided conversion
        function `itm_conversion` to map low level types to higher abstraction
        of the accessed items.
        
        :param ptr: the pointer 
        :type  ptr: Slist_ptr
        :param conversion: the object encapsulating the conversion to and from
                           pointer
        :type conversion: pynusmv.util.Conversion
        :param freeit: a flag indicating whether or not the system should free
                    the system resources allocated to this object when it is
                    garbage collected.
        :type  freeit: boolean 
        """
        super().__init__(ptr, freeit=freeit)
        self._conversion = conversion
        
    def _free(self):
        """
        Frees the resources allocated to this object
        """
        if self._freeit and self._ptr is not None:
            _utils.Slist_destroy(self._ptr)
            self._ptr = None
            self._freeit = False
    
    def __str__(self):
        return 'Slist'+str(list(self))
    
    @staticmethod
    def empty(conversion):
        """
        Returns a new empty Slist
        
        :param conversion: the object encapsulating the conversion to and from
                           pointer
        :type conversion: pynusmv.util.Conversion
        :return: a new empty list
        """
        return Slist(_utils.Slist_create(), conversion)
    
    @staticmethod
    def from_list(lst, conversion):
        """
        Returns a new Slist corresponding to the `lst` given as first argument
        
        :param lst: an iterable from which to create a new Slist
        :type  lst: any collection that can be iterated
        :param conversion: the object encapsulating the conversion to and from
                           pointer
        :type conversion: pynusmv.util.Conversion
        :return: a new list containing the same elements (in the same order) than `lst`
        """
        ret = Slist(_utils.Slist_create(), conversion)
        # copy each element
        for i in lst:
            ret.push(i)
        # reverse the list to keep the order
        ret.reverse()
        return ret
    
    def copy(self):
        """:return: a copy of this Slist"""
        return self.__copy__()
    
    def __copy__(self):
        """:return: a copy of this Slist"""
        return Slist(_utils.Slist_copy(self._ptr), self._conversion)
    
    def __reversed__(self):
        """:return: a reversed copy of this Slist""" 
        return Slist(_utils.Slist_copy_reversed(self._ptr), self._conversion)
    
    def reverse(self):
        """Reverses the order of the elements in this list"""
        _utils.Slist_reverse(self._ptr)
    
    def push(self, o):
        """Prepends o tho the list"""
        _utils.Slist_push(self._ptr, self._conversion.to_pointer(o))
        
    def pop(self):
        """:return: returns and remove the top (first element) of the list"""
        return self._conversion.to_object(_utils.Slist_pop(self._ptr))
    
    def top(self):
        """:return: the first element of the list w/o removing it"""
        return self._conversion.to_object(_utils.Slist_top(self._ptr))
    
    def is_empty(self):
        """:return: True iff this list is empty"""
        return _utils.Slist_is_empty(self._ptr)
    
    def __contains__(self, elem):
        """
        :return: True iff the list contains `elem`
        
        :param elem: any element that might be in the list
        """
        return _utils.Slist_contains(self._ptr, self._conversion.to_pointer(elem))
    
    def extend(self, other):
        """
        Appends one list to this one
        
        :param other: the other list to append to thisone
        """
        _utils.Slist_append(self._ptr, other._ptr)
        
    def remove(self, item):
        """
        Removes all occurences of `item` in this list
        
        :param item: the item to remove
        """
        _utils.Slist_remove(self._ptr, self._conversion.to_pointer(item))
    
    def __eq__(self, other):
        """
        :return: True off other has the same content (and order) than this list
        """
        if not isinstance(other, Slist):
            return False
        else:
            return _utils.Slist_equals(self._ptr, other._ptr)
    
    def __len__(self):
        """
        :return: the number of items in the list
        """
        return _utils.Slist_get_size(self._ptr)
    
    def clear(self):
        """Removes all items from the list"""
        _utils.Slist_clear(self._ptr)
    
    # Slist_sort and Slist_find are not implemented as they require function ptr
    # as parameters. Should these functions be required, then their functionality
    # can be re-implemented in python
    
    def __iter__(self):
        """
        :return: an iterator that lets you walk all the elements in the list
        """
        return SlistIterator(self)
    
    def __getitem__(self, idx):
        """
        :return: the item at offset `idx` in the list
        :param idx: the offset of the item to return
        
        :raise: KeyError if there is no idx-th element in the list
        """
        counter = 0
        for i in self:
            if idx == counter:
                return i
            counter += 1
        # not found
        raise KeyError("No value at index {}".format(idx))
            
    def __delitem__(self, idx):
        """
        Remove all occurrences of item at index `idx` in the list
        :param idx: the offset of the elem to remove
        """
        counter = 0
        for i in self:
            if idx == counter:
                return _utils.Slist_remove(self._ptr, self._conversion.to_pointer(i))
            counter += 1
    
class SlistIterator(Iterator):
    """
    This class defines a pythonic iterator to iterate over NuSMV Slist objects
    """    
    def __init__(self, slist):
        """
        Creates a new iterator to iterate over `slist`
        :param slist: the list to iterate
        :type  slist: Slist
        """
        super().__init__()
        self._SENTINEL = Sentinel()
        self._lst      = slist
        self._iter     = _utils.Slist_first(slist._ptr)
        self._val      = self._peek()
    
    def __str__(self):
        return 'SlistIterator'+str(list(self))
    
    def __next__(self):
        """Implements the iteration mechanism"""
        if self._SENTINEL == self._val:
            raise StopIteration
        else:
            ret = self._val
            self._iter = _utils.Siter_next(self._iter)
            self._val  = self._peek() 
            return ret
    
    def _peek(self):
        """
        Returns the value at the current position of the iterator
        but does not move the cursor.
        
        :return: the value at the current position of the iterator OR
                 self._SENTINEL when the iterator has reached the end of the
                 collection
        """
        if _utils.Siter_is_end(self._iter):
            return self._SENTINEL
        else:
            return self._lst._conversion.to_object(_utils.Siter_element(self._iter))
    
    # Siter_set_element is not implemented in NuSMV

class Sentinel:
    """This class implements a sentinel value"""
    def __eq__(self, other):
        return isinstance(other, Sentinel)
        
    def __repr__(self): 
        return "(Sentinel object)"


#===============================================================================
#====== NodeList iterator ======================================================
#===============================================================================
# TODO: maybe add to Node ?
class NodeIterator(Iterator):
    """
    This class implements an useful iterator to iterate over nodes or wrap them
    to python lists.
    """
    def __init__(self, ptr):
        """
        Creates a new instance iterating over the given node (considered as list)
        """
        super().__init__() # will go up to object
        self._ptr = ptr
    
    def __str__(self):
        return 'NodeIterator'+str(list(self))
    
    @staticmethod
    def from_node(node):
        """
        Creates an iterator from an high level Node
        :param node: the Node representing the list to iterate
        :type node: Node
        :return: an iterator iterating over the node considered as a linked list
        """
        return NodeIterator(node._ptr)

    @staticmethod
    def from_pointer(ptr):
        """
        Creates an iterator from a low level pointer to a node_ptr
        :param ptr: the pointer to a node representing the list to iterate
        :type node: node_ptr
        :return: an iterator iterating over the node considered as a linked list
        """
        return NodeIterator(ptr)
    
    def __next__(self):
        """
        Performs the iteration
        :return: the next node
        :raise: StopIteration when the iteration is over
        """
        if self._ptr is None:
            raise StopIteration
        else:
            ret = Node.from_ptr(self._ptr)
            self._ptr = _node.cdr(self._ptr)
            return ret
    
#===============================================================================
#====== NodeList type ==========================================================
#===============================================================================
class NodeList(PointerWrapper, Iterable):
    """
    This class implements a pythonic interface to NuSMV's internal version of a
    doubly linked list
    
    .. note:: The following apis have not been exposed since they require pointer
      to function (in C) which are considered too low level for this pythonic
      interface. However, these apis are accessible using 
      pynusmv_lower_interface.nusmv.utils.utils.<TheAPI> and passing nodelst._ptr instead of 
      nodelist.
      
        - NodeList_remove_elems
        - NodeList_search
        - NodeList_foreach
        - NodeList_map
        - NodeList_filter
    """
    def __init__(self, ptr, conversion=NodeConversion(),freeit=False):
        """
        Creates a new instance from the given pointer and conversion
        :param ptr: the pointer to a NuSMV NodeList to be wrapped
        :param conversion: the conversion object allowing the transformation
           from pointer to object and vice versa
        :param freeit: a flag indicating whether or not this list should be 
           freed upon garbage collection
        """
        # super is PointerWrapper since it's the first in the mro order
        super().__init__(ptr, freeit=freeit)
        self._conv = conversion
        
    def _free(self):
        """Overrides PointerWrapper._free()"""
        if self._freeit and self._ptr is not None:
            _utils.NodeList_destroy(self._ptr)
            
    def __str__(self):
        return 'NodeList'+str(list(self))        
    
    @staticmethod
    def empty(conversion=NodeConversion(), freeit=True):
        """
        Creates a new empty list
        
        :param conversion: the conversion object allowing the transformation
           from pointer to object and vice versa
        :param freeit: a flag indicating whether or not this list should be 
           freed upon garbage collection
        """
        return NodeList(_utils.NodeList_create(), conversion, freeit)
    
    # from_list ~~> from node, not exposed => use NodeIter instead
    
    @staticmethod
    def from_list(lst, conversion=NodeConversion(), freeit=True):
        """
        :return: a NodeList equivalent to the pythonic list `lst`
        :param lst: the list which shall serve as basis for the created one
        :param conversion: the object encapsulating the conversion back and forth
          from and to pointer
        :param freeit: a flag indicating whether or not this list should be freed
          upon garbage collection
        """
        ret = NodeList.empty(conversion, freeit)
        for v in lst:
            ret.append(v)
            
        return ret
    
    def copy(self, freeit=True):
        """
        :param freeit: a flag indicating whether or not the copy shoudl be freed
          upon garbage collection
        :return: Returns a copy of this list
        """
        return self.__copy__(freeit)
    
    def __copy__(self, freeit=True):
        """
        :param freeit: a flag indicating whether or not the copy shoudl be freed
          upon garbage collection
        :return: Returns a copy of this list
        """
        pointer = _utils.NodeList_copy(self._ptr)
        return NodeList(pointer, self._conv, freeit)
    
    def append(self, node):
        """
        Adds the given node at the end of the list
        
        :param node: the node to append to the list
        """
        _utils.NodeList_append(self._ptr, self._conv.to_pointer(node))
        
    def prepend(self, node):
        """
        Adds the given node at the beginning of the list
        
        :param node: the node to append to the list
        """
        _utils.NodeList_prepend(self._ptr, self._conv.to_pointer(node))
        
    def __len__(self):
        """:return: the length of the list"""
        return _utils.NodeList_get_length(self._ptr)
    
    def reverse(self):
        """inverts the order of the items in the list"""
        _utils.NodeList_reverse(self._ptr)
        
    def extend(self, other, unique=False):
        """
        Appends all the iems of `other` to this list. If param unique is set to
        true, the items are only appended if not already present in the list.
        
        :param other: the other list to concatenate to this one
        :param unique: a flag to conditionally add the elements of the other list
        """
        if unique:
            _utils.NodeList_concat_unique(self._ptr, other._ptr)
        else:
            _utils.NodeList_concat(self._ptr, other._ptr)
        
    def __contains__(self, node):
        """
        :return: True iff node belongs to this list
        :param node: the node whose appartenance is being tested
        """ 
        return _utils.NodeList_belongs_to(self._ptr, self._conv.to_pointer(node))
    
    def count(self, node):
        """
        :return: the number of occurences of `node`
        :param node: the node whose number of occurrences is being counted
        """
        return _utils.NodeList_count_elem(self._ptr, self._conv.to_pointer(node))
    
    def __getitem__(self, idx):
        """
        :return: the idx-th item of the list
        :raise: KeyError when the idx is not one of the possible indices of the
          list
        .. warning:: This implementation is O(idx) despite the syntax sugar making
          it look like O(1) 
        """
        counter = 0
        for node in self:
            if idx == counter: 
                return node
            counter += 1
        raise KeyError("Index {} is out of the list bounds".format(idx))

    def __delitem__(self, idx):
        """
        .. warning:: This implementation is O(idx) despite the syntax sugar making
          it look like O(1) 
          
        .. warning:: In case no value corresponds to idx, no warning is issued
        """
        iterator = iter(self)
        for _ in range(idx):
            iterator.__next__()
        _utils.NodeList_remove_elem_at(self._ptr, iterator._ptr) 
    
    def __iter__(self):
        """:return: an iterator to walk through this list"""
        return NodeListIter(self)
    
    def insert_before(self, iterator, node):
        """
        inserts `node` right before the position pointed by iterator
        :param iterator: the iterator pointing the position where to insert
        :param node: the node to insert in the list
        """
        _utils.NodeList_insert_before(self._ptr, iterator._ptr, self._conv.to_pointer(node))
        
    def insert_after(self, iterator, node):
        """
        inserts `node` right after the position pointed by iterator
        :param iterator: the iterator pointing the position where to insert
        :param node: the node to insert in the list
        """
        if _utils.ListIter_is_end(iterator._ptr):
            raise ValueError("impossible to add after an end iterator")
        else:
            _utils.NodeList_insert_after(self._ptr, iterator._ptr, self._conv.to_pointer(node))
        
    def insert_at(self, idx, node):
        """
        inserts `node` right before the node at position `idx`
        :param idx: the the position where to insert
        """
        iterator = iter(self)
        for _ in range(idx):
            iterator.__next__()
        _utils.NodeList_insert_before(self._ptr, iterator._ptr, self._conv.to_pointer(node))
    
    def print_nodes(self, stdio_file):
        """
        Prints the list node to the given stream.
        :param stdio_file: an instance of StdioFile wrapping an open C stream
        """
        _utils.NodeList_print_nodes(self._ptr, stdio_file.handle)
    
class NodeListIter(Iterator):
    """
    An iterator to iterate over NodeList.
    
    .. note:: 
       Despite the fact that it wraps a pointer, this class does not extend
       the PointerWrapper class since there is no need to free the pointer.
    """
    def __init__(self, lst):
        """
        Creates a new instance from the given pointer
        :param lst: the node list that is being iterated
        """
        self._SENTINEL = Sentinel()
        self._lst      = lst
        self._ptr      = _utils.NodeList_get_first_iter(lst._ptr)
    
    def __str__(self):
        return 'NodeListIter'+str(list(self))
    
    def _peek(self):
        """
        :return: the item at the current position in the iteration or the
          sentinel if no value could be found
        """
        if _utils.ListIter_is_end(self._ptr):
            return self._SENTINEL
        else:
            node = _utils.NodeList_get_elem_at(self._lst._ptr, self._ptr)
            return self._lst._conv.to_object(node)
    
    def __next__(self):
        """
        Moves the cursor and returns the current value
        :return: the value of the item at the current position in the iterator
        """
        ret = self._peek() 
        if self._SENTINEL == ret:
            raise StopIteration()
        else:
            self._ptr = _utils.ListIter_get_next(self._ptr)
            return  ret
        
#===============================================================================
#====== Associative array type =================================================
#===============================================================================
class Assoc(PointerWrapper):
    """
    This class implements a pythonic abstraction to the NuSMV associative array
    encapsulated in st_table aka hash_ptr which is often used in the NuSMV
    internals.
    
    .. note:: I couldn't find any documentation about the ST_PFSR type. As a 
      consequence of this, I couldn't implement the iterable protocol
      
    .. warning:: BOTH the key AND the value are supposed to be of type Node.
      Hence, the conversion method must take care to return the nodes and 
      objects of the right types. 
    """
    
    def __init__(self, ptr, key_conversion=NodeConversion(), value_conversion=NodeConversion(), freeit=False):
        """
        Creates a new Assoc instance
        
        :param ptr: the NuSMV pointer to wrap
        :param key_conversion: the conversion for the key (object <--> pointer)
        :param value_conversion: the conversion of the value  (object <--> pointer)
        :param freeit: a flag indicating whether or not this object should be freed
                    upon garbage collection
                    
        .. warning:: BOTH the key AND the value are supposed to be of type 
          node_ptr in the undelying collection. Hence, the conversion method 
          must take care to return the nodes and those types.          
        """
        super().__init__(ptr, freeit=freeit)
        self._key_conv = key_conversion
        self._val_conv = value_conversion
        
    def _free(self):
        """
        Overrides the PointerWrapper api to enfore the release of the system
        resources allocated to this object.
        """
        if self._freeit and self._ptr is not None:
            _utils.free_assoc(self._ptr)
    
    @staticmethod    
    def empty(key_conversion=NodeConversion(), value_conversion=NodeConversion(), initial_capa=0, freeit=False):
        """
        Creates an empty assoc
        
        :param key_conversion: the conversion for the key (object <--> pointer)
        :param value_conversion: the conversion of the value  (object <--> pointer)
        :param initial capa: the initial capacity of the associative array
        :param freeit: a flag indicating whether or not this object should be freed
                    upon garbage collection
        :return: a new empty Assoc
        """
        if initial_capa == 0:
            return Assoc(_utils.new_assoc(), key_conversion, value_conversion, freeit=freeit)
        else:
            return Assoc(_utils.new_assoc_with_size(initial_capa), key_conversion, value_conversion, freeit=freeit)
    
    @staticmethod    
    def from_dict(dico, key_conversion=NodeConversion(), value_conversion=NodeConversion(), freeit=False):
        """
        Creates an assoc from a pythonic dict
        
        :param dico: python dictionary
        :param key_conversion: the conversion for the key (object <--> pointer)
        :param value_conversion: the conversion of the value  (object <--> pointer)
        :param freeit: a flag indicating whether or not this object should be freed
                    upon garbage collection
        :return: an assoc with the same contents as the given dico
        """
        me = Assoc(_utils.new_assoc_with_size(len(dico)), key_conversion, value_conversion, freeit=freeit)
        for k,v in dico.items():
            me[k] = v
        return me
    
    def copy(self):
        """Creates a copy of this Assoc"""
        return self.__copy__()
    
    def __copy__(self, freeit=True):
        """
        Creates a copy of this Assoc
        
        :param freeit: a flag indicating whether or not this object should be freed
                    upon garbage collection
        """
        return Assoc(_utils.copy_assoc(self._ptr), self._key_conv, self._val_conv, freeit=freeit)
    
    def __contains__(self, key):
        """
        :return: returns true if key belongs to the association
        :raise: In case the key is not a Node, raises TypeError (see mutable protocol)
        """
        result = _utils.find_assoc(self._ptr, self._key_conv.to_pointer(key))
        return result is not None
        
    
    def __getitem__(self, key):
        """
        :return: retrieves the item corresponding to the given key.
        :raise: In case the key wasn't found in this Assoc, raises KeyError
        .. warning:: key is supposed to be of type Node
        """
        result = _utils.find_assoc(self._ptr, self._key_conv.to_pointer(key))
        if result is not None: 
            return self._val_conv.to_object(result)
        else:
            raise KeyError("Value not found")
        
    def __setitem__(self, key, value):
        """
        Associates key to value in the container
        
        .. warning:: key is supposed to be of type Node
        """
        key_ptr = self._key_conv.to_pointer(key)
        val_ptr = self._val_conv.to_pointer(value)
        _utils.insert_assoc(self._ptr, key_ptr, val_ptr)
    
    def __delitem__(self, key):
        """
        Removes the key and the value associated with key from the container
        """
        key_ptr = self._key_conv.to_pointer(key)
        _utils.remove_assoc(self._ptr, key_ptr)
    
    def clear(self):
        """Empties the container"""
        _utils.clear_assoc(self._ptr)
    
    