"""
The :mod:`pynusmv.utils` module contains some secondary functions and classes
used by PyNuSMV internals.

"""


__all__ = ['PointerWrapper', 'fixpoint', 'update', 'StdioFile','writeonly',
           'indexed']

from pynusmv_lower_interface.nusmv.utils import utils
from pynusmv.init import _register_wrapper


class PointerWrapper(object):

    """
    Superclass wrapper for NuSMV pointers.

    Every pointer to a NuSMV structure is wrapped in a PointerWrapper
    or in a subclass of PointerWrapper.
    Every subclass instance takes a pointer to a NuSMV structure as constructor
    parameter.

    It is the responsibility of PointerWrapper and its subclasses to free
    the wrapped pointer. Some pointers have to be freed like `bdd_ptr`,
    but other do not have to be freed since NuSMV takes care of this;
    for example, `BddFrm_ptr` does not have to be freed.
    To ensure that a pointer is freed only once, PyNuSMV ensures that
    any pointer is wrapped by only one PointerWrapper (or subclass of it)
    if the pointer have to be freed.

    """

    def __init__(self, pointer, freeit=False):
        """
        Create a new PointerWrapper.

        :param pointer: the pointer to wrap
        :param freeit: whether the pointer has to be freed when this wrapper
                       is destroyed

        """
        self._ptr = pointer
        self._freeit = freeit
        _register_wrapper(self)

    def _free(self):
        """
        Every subclass must implement `_free` if there is something to free.

        """
        pass

    def __del__(self):
        if self._freeit and self._ptr is not None:
            self._free()


    def __hash__(self):
        """
        Makes this object hashable.

        .. warning::

            Beware it uses the pointer to implement the hashing function.
            So it is IDENTITY dependent (in C) and not value dependant.

        :return: an object that can serve as key to perform the lookup in a dict.
        """
        return self._ptr.__hash__()

    def __eq__(self, other):
        """
        Equality test between two objects.

        .. warning::

            Beware it uses the pointer to implement the hashing function.
            So it is IDENTITY dependent (in C) and not value dependant.

        :return: True iff the two object are the same
        """
        return self._ptr == other._ptr


class AttributeDict(dict):

    """
    An `AttributeDict` is a dictionary for which elements can be accessed by
    using their keys as attribute names.

    """

    def __init__(self, *args, **kwargs):
        super(AttributeDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def fixpoint(funct, start):
    """
    Return the fixpoint of `funct`, as a BDD, starting with `start` BDD.

    :rtype: :class:`BDD <pynusmv.dd.BDD>`

    .. note:: mu Z.f(Z) least fixpoint is implemented with
              `fixpoint(funct, false)`.
              nu Z.f(Z) greatest fixpoint is implemented with
              `fixpoint(funct, true)`.

    """

    old = start
    new = funct(start)
    while old != new:
        old = new
        new = funct(old)
    return old


def update(old, new):
    """
    Update `old` with `new`. `old` is assumed to have the `extend` or `update`
    method, and `new` is assumed to be a good argument for the corresponding
    method.

    :param old: the data to update.
    :param new: the date to update with.

    """
    try:
        old.extend(new)
    except AttributeError:
        old.update(new)


class StdioFile:
    """
    Wrapper class that provides a context manager to access a FILE* whenever the
    lower interface needs one. This makes for a more pythonic way to interact
    with APIs that need a standard file handle without having to deal with the
    low level open/close instructions. Example::

        # opens an arbitrary file of your choice.
        with StdioFile.for_name('my_output_file', 'w') as f:
            lower_interface_do_something_smart(f)

    This wrapper also gives you access to stdin, stdout and stderr which, are
    never closed despite the fact that they may be used with a `with` statement::

        # stdio is ALREADY open at this time
        with StdioFile.stdout() as out:
            lower_interface_do_something_smart(out)
        # stdio is STILL open here
    """

    def __init__(self, fname, mode):
        """
        Creates a new instance that will open the file `fname` in the `mode`
        mode.

        :param fname: the name of the file to be opened (more info -> stdio.h)
        :param  mode: the mode in which to open the file (more info -> stdio.h)
        """
        self._fname     = fname
        self._mode      = mode
        self._ptr       = None
        self._isspecial = False

    @staticmethod
    def for_name(fname=None, mode='w'):
        """
        This function acts like a generic factory that either return a handle
        for standard file if the name is specified or to stdin or stdout if the
        name is not specified (it depends on the mode)

        :return: a stdiofile for the given name or stdin/stdout if no name is
                 specified depending on the value of the mode
        """
        if fname is None:
            return StdioFile.stdin() if mode == "r" else StdioFile.stdout()
        else:
            return StdioFile(fname, mode)

    @staticmethod
    def stdin():
        """Standard input"""
        ret = StdioFile("(standard input)", "r")
        ret._ptr = utils.stdio_stdin()
        ret._isspecial = True
        return ret

    @staticmethod
    def stdout():
        """standard output"""
        ret = StdioFile("(standard output)", "w")
        ret._ptr = utils.stdio_stdout()
        ret._isspecial = True
        return ret

    @staticmethod
    def stderr():
        """standard error"""
        ret = StdioFile("(standard error)", "w")
        ret._ptr = utils.stdio_stderr()
        ret._isspecial = True
        return ret


    def __enter__(self):
        """Opens the file"""
        if not self._isspecial:
            self._ptr = utils.stdio_fopen(self._fname, self._mode)
        return self

    def __exit__(self, exception_type, exception_value, trace):
        """Makes sure the file is closed"""
        if self._ptr is not None and not self._isspecial:
            utils.stdio_fclose(self._ptr)
            self._ptr = None

    @property
    def handle(self):
        """:return: a FILE* handle to the opened stream"""
        return self._ptr

#===============================================================================
#====== Decorators =============================================================
#===============================================================================

class writeonly:
    """
    writeonly provides a write only decorator for properties that do not
    have a getter accessor. This makes for pythonic property-lik APIs where your
    class defines should have defined a setter. Example::

        class Dummy(PointerWrapper):
          # .. code elided ...

          @writeonly
          def config_tweak(self, new_value_of_tweak):
            lower_interface_set_tweak(self._ptr, new_value_of_tweak)

    Can be used the following way::

        d = Dummy()
        # this is now perfectly OK
        d.config_tweak = 42

        # this will however fail since no getter was defined
        d.config_tweak
    """

    def __init__(self, fn):
        """Creates the decorator memeorizing the decorated func"""
        self._fn     = fn
        self.__doc__ = fn.__doc__ # be nice with the user documentation

    def __call__(self):
        """
        Executes the decoration (takes care itself to apply the decorated fn
        """
        return self

    def __set__(self, obj, value):
        """
        Executes the decorated setter function
        """
        self._fn(obj, value)

    def __get__(self, obj, _type):
        """
        Makes sure this property is only accessed in write only mode
        """
        msg = '{} is defined as a write only property'.format(self._fn.__name__)
        raise AttributeError(msg)

class indexed:
    """
    indexed provides a set of decorators that enable the use of 'pythonic' indexed
    get/setters. These give you the possibility to automagically add syntax sugar
    to the classes you write.

    The easiest (and most flexible way) to get started with the indexed series
    of decorator is to use `@indexed.property(<name>)`. But if you are after
    something more limited, you might want to give a look to the other decorators
    that are provided: namely, `@indexed.getter`, `@indexed.setter` and
    `@indexed.deleter`.
    """

    def __init__(self, target, fget=None, fset=None, fdel=None):
        """
        Creates a new indexed callback instance configured to use `fget` as
        indexed getter, `fset` as indexed setter and where args[0] is a reference
        to the target object to which the get/set function are going to be
        directed to.

        :param target: the receiver object who will receive the indexed messages
           translated with the getter, setter, deleter functions
        :param fget: the 'getter' function (the one to call to __getitem__)
        :param fset: the 'setter' function (the one to call to __setitem__)
        :param fdel: the 'deleter' function(the one to call to __delitem__)
        """
        self._targ = target
        self._get  = indexed.__prepare_fget(fget)
        self._set  = indexed.__prepare_fset(fset)
        self._del  = indexed.__prepare_fdel(fdel)

    def __getitem__(self, key):
        """
        performs the key based lookup using the configured getter
        :param key: the key to use as 'lookup' key
        :return: the output of target.getter(key)
        """
        return self._get(self._targ, key)

    def __setitem__(self, key, value):
        """
        performs the key based assignment of value to the key-th variable
        :param key: the key to use as 'lookup' key
        :param value: the value to give to whatever corresponds to key in the
               underlying structure.
        :return: whatever target.setter(key, value) returns (more than likely,
               it should be None)
        """
        return self._set(self._targ, key, value)

    def __delitem__(self, key):
        """
        performs the key based suppression using the configured deleter function
        :param key: the key to use as 'deletion' key
        :return: whatever target.deleter(key) returns (more than likely,
               it should be None)
        """
        return self._del(self._targ, key)

    @staticmethod
    def __wrap(fget=None, fset=None, fdel=None, doc=None):
        """
        wraps the given function into a runtime property that can be accessed
        in an indexed way.

        .. note::

            This method is private and should not be used from the outside.

        :param fget: the 'getter' function (the one to call to __getitem__)
        :param fset: the 'setter' function (the one to call to __setitem__)
        :param fdel: the 'deleter' function(the one to call to __delitem__)
        :param doc: the docstring to set to the returned property
        """
        wrap = lambda *args: indexed(args[0], fget=fget, fset=fset, fdel=fdel)
        wrap.doc = doc
        return property(wrap)

    @staticmethod
    def __prepare_fget(fn):
        """
        Prepares the fget function from the given fn.

        This function returns the raw code to be executed for fget. If the given
        `fn` is an indexed instance (ie. because the getter has been decorated),
        then it is undecorated and the _get function is returned. If the obtained
        callable is a method (not a function), then its __fun__ attribute is
        returned in order to avoid weird behaviors (case where the given self is
        actually of the right type, albeit not the expected behavior)

        .. note::

            This method is private and should not be used from the outside.

        :param fn: the getter 'function'
        :return: the raw getter code
        """
        return indexed.__prepare(fn._get if isinstance(fn, indexed) else fn)

    @staticmethod
    def __prepare_fset(fn):
        """
        Prepares the fset function from the given fn.

        This function returns the raw code to be executed for fset. If the given
        `fn` is an indexed instance (ie. because the setter has been decorated),
        then it is undecorated and the _set function is returned. If the obtained
        callable is a method (not a function), then its __fun__ attribute is
        returned in order to avoid weird behaviors (case where the given self is
        actually of the right type, albeit not the expected behavior)

        .. note::

            This method is private and should not be used from the outside.

        :param fn: the setter 'function'
        :return: the raw setter code
        """
        return indexed.__prepare(fn._set if isinstance(fn, indexed) else fn)

    @staticmethod
    def __prepare_fdel(fn):
        """
        Prepares the fdel function from the given fn.

        This function returns the raw code to be executed for fdel. If the given
        `fn` is an indexed instance (ie. because the deleter has been decorated),
        then it is undecorated and the _del function is returned. If the obtained
        callable is a method (not a function), then its __fun__ attribute is
        returned in order to avoid weird behaviors (case where the given self is
        actually of the right type, albeit not the expected behavior)

        .. note::

            This method is private and should not be used from the outside.

        :param fn: the deleter 'function'
        :return: the raw deleter code
        """
        return indexed.__prepare(fn._del if isinstance(fn, indexed) else fn)

    @staticmethod
    def __prepare(fn):
        """
        Returns the raw code of the given `fn`.

        If `fn` is a method (not a function), then its __fun__ attribute is
        returned in order to avoid weird behaviors (case where the given self is
        actually of the right type, albeit not the expected behavior) otherwise
        `fn` is returned as is.

        .. note:: This method is private and should not be used from the outside.

        :param fn: the function to prepare. (fn is assumed not to be an indexed)
        :return: the raw code of the given `fn`
        """
        return fn.__func__ if hasattr(fn, '__func__') else fn

    @staticmethod
    def getter(fn):
        """
        Wraps a function `fn` and turns it into  pythonic indexed-like acessor.

        :param fn: the function to use to perform the keyed-lookup

        Example usage::

            class GetterOnly:
                # ... code elided ...

                # using @indexed or @indexed.getter is perfectly equivalent although
                # the use of @indexed.getter is considered slightly cleaner
                @indexed.getter
                def clause(self, index):
                  return lower_interface_get_clause_at(self._ptr, index)

            # example of use:
            g = GetterOnly()
            g.clause[42] # returns the 42th clause
        """
        return indexed.__wrap(fget=fn, doc=fn.__doc__)

    @staticmethod
    def setter(fn):
        """
        wraps a function `fn` and turns it into  pythonic indexed-like acessor.

        :param fn: the function to use to perform the keyed-assignment

        Example usage::

            class SetterOnly:
                # ... code elided ...

                @indexed.setter
                def clause(self, index, new_value):
                  lower_interface_set_clause_at(self._ptr, index, new_value)

            # example of use:
            s = GetterOnly()
            s.clause[42] = another_clause # changes the value of the clause
        """
        return indexed.__wrap(fset=fn, doc=fn.__doc__)

    @staticmethod
    def deleter(fn):
        """
        wraps a function `fn` and turns it into  pythonic indexed-like deleter.

        :param fn: the function to use to perform the keyed-lookup

        Example usage::

            class DeleterOnly:
                # ... code elided ...

                @indexed.deleter
                def clause(self, index, new_value):
                  return lower_interface_delete_clause_at(self._ptr, index)

            # example of use:
            d = DeleterOnly()
            del d.clause[42] # 42th clause has been deleted
        """
        return indexed.__wrap(fdel=fn, doc=fn.__doc__)

    @staticmethod
    def property(name, **kwargs):
        """
        Wraps the constructor of the decorated class to add a virtual indexed
        property called `name`

        By **default**, the generated indexed getter, indexed setter and
        indexed deleted are assumed to be called respectively:

            - get_`name`
            - set_`name`
            - del_`name`

        However, these names are not enforced and can be customized if you pass the
        keywords fget=<the_name_of_your_getter_fn>, fset=<the_name_of_your_setter_fn>
        and/or fdel=<the_name_of_your_deleter_fn>.

        .. note:: The keyword parameters also let you provide a docstring for
                  the virtual property you define. To this end, simply use the
                  `doc` keyword.

        .. warning:: The getter, setter and deleter functions MUST BE CALLABLE
                     objects ! This means, you MAY NOT decorate any of the
                     functions you intend to use in your virtual property with
                     any of the @property, @indexed.getter, @indexed.setter or
                     @indexed.deleter since you resulting property would simply
                     not work.

        Simple example::

            @indexed.property('smartlst')
            class Cls:
                def __init__(self):
                    self._lst  = [4,5,6]

                def get_smartlst(self, idx):
                    return self._lst[idx]

                def set_smartlst(self, idx, v):
                    self._lst[idx] = v

                def del_smartlst(self, idx):
                    del self._lst[idx]

            # Usage:
            c = Cls()
            c.smartlst[1]     # calls _get_smartlst and returns 5
            c.smartlst[1]=42  # calls _set_smartlst and changes _slt to be [4,42,6]
            del c.smartlst[1] # calls _del_smartlst and changes _slt to be [4, 6]

        Example with custom property names::

            @indexed.property('smartlst', fget='glst', fset='slst', fdel='dlst')
            class Cls:
                def __init__(self):
                    self._lst  = [4,5,6]

                def glst(self, idx):
                    return self._lst[idx]

                def slst(self, idx, v):
                    self._lst[idx] = v

                def dlst(self, idx):
                    del self._lst[idx]

            # Usage:
            c = Cls()
            c.smartlst[1]     # calls glst and returns 5
            c.smartlst[1]=42  # calls slst and changes _slt to be [4,42,6]
            del c.smartlst[1] # calls dlst and changes _slt to be [4, 6]

        If you don't like to use the decorator 'magic' but still want to define
        a virtual property with very little effort: you should then use the
        indexed constructor itself as such::

            class Dummy:
                def __init__(self):
                    self.clause= indexed(self, fget=self.get_clause, fset=self.set_clause,fdel=self.del_clause)

                @indexed.getter
                def get_clause(self, clause_idx):
                    return lower_interface_get_clause_at(self._ptr, index)

                @indexed.setter
                def set_clause(self, clause_idx, value):
                    lower_interface_set_clause_at(self._ptr, index, new_value)

                @indexed.deleter
                def del_clause(self, clause_idx):
                    lower_interface_delete_clause_at(self._ptr, index)

            # example of use:
            d = Dummy()
            d.clause[42]                # returns the 42th clause
            d.clause[42] = other_clause # updates the 42th clause
            del d.clause[42]            # drops the 42th clause
        """
        def decorate_init(init, fget, fset, fdel):
            """
            Internal function used to decorate the __init__ method of the decorated
            class.

            .. note:: You should may not use this function for yourself

            :param init: the __init__ method to decorate
            :param fget: the function to use as indexed getter in the virtual prop
            :param fset: the function to use as indexed setter in the virtual prop
            :param fdel: the function to use as indexed deleter in the virtual prop
            """
            def decorated(self, *args, **kw2):
                """The function that will be used instead of `init`"""
                init(self, *args, **kw2)
                self.__dict__[name] = indexed(self, fget=fget, fset=fset, fdel=fdel)

                # set the docstring of the virtual property
                if 'doc' in kwargs:
                    self.__dict__[name].__doc__ = kwargs['doc']
                else:
                    self.__dict__[name].__doc__ = "Virtual indexed property"
            return decorated

        def class_deco(cls):
            """
            Function that actually decorates the given `cls` class.
            :param cls: the class being decorated.
            """
            _dict= cls.__dict__
            fget = None
            fset = None
            fdel = None

            # default settings
            if 'get_'+name in _dict:
                fget = _dict['get_'+name]
            if 'set_'+name in _dict:
                fset = _dict['set_'+name]
            if 'del_'+name in _dict:
                fdel = _dict['del_'+name]

            # override default settings
            if 'fget' in kwargs:
                fget = cls.__dict__[kwargs['fget']]
            if 'fset' in kwargs:
                fset = cls.__dict__[kwargs['fset']]
            if 'fdel' in kwargs:
                fdel = cls.__dict__[kwargs['fdel']]

            cls.__init__ = decorate_init(cls.__init__, fget, fset, fdel)
            return cls

        return class_deco
