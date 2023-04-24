"""This is my base class for constructing SecDb-like evaluation graphs in memory--
which is to say, instantiating objects that are unique by their initialization variables,
and which cache their calculated results automatically,
but which enable clearing (invalidating) those cached results on demand or under desired circumstances.
"""
import functools
from inspect import signature


class CachedInstance(type):
    """For unique instances of a class by calling args.
        class X(metaclass=CachedInstance):
            def __init__(self, vara, varb):
                self.vara = vara
                self.varb = varb
            etc.
        Treat all named arguments correctly, whether positional or explicitly named in the instantiation call.
        Ref: https://stackoverflow.com/questions/50820707/python-class-instances-unique-by-some-property
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Use inspection to form an explicit dict of args by name,
           whether those args are supplied positionally, or by name, or by default"""
        explicit_args = {}
        poppable_args = list(args)
        for name, parm in signature(cls.__init__).parameters.items():
            if name == 'self':
                continue
            if len(poppable_args):
                val = poppable_args.pop(0)
            elif name in kwargs:
                val = kwargs[name]
            else:
                val = parm.default
            explicit_args[name] = val
        # Class itself plus explicit dict of args in alpha order form a key which defines object uniqueness
        key = cls, tuple(sorted(explicit_args.items()))
        if key not in cls._instances:
            cls._instances[key] = super(CachedInstance, cls).__call__(*args, **kwargs)
        return cls._instances[key]

    @staticmethod
    def pop_reference(obj):
        """Enable an object instance to have itself removed from cache, for memory cleanup"""
        key = None
        for k, o in CachedInstance._instances.items():
            if o == obj:
                key = k
        if key:
            del CachedInstance._instances[key]


class Node(metaclass=CachedInstance):
    """Base class for forming nodes in an evaluation graph. All classes should inherit this Node class."""
    @property
    def cached_methods(self):
        return {vt for vt in self.value_types if isinstance(self.__class__.__dict__[vt], functools._lru_cache_wrapper)}

    @property
    def cached_properties(self):
        return {vt for vt in self.value_types if isinstance(self.__class__.__dict__[vt], functools.cached_property)}

    def clear(self):
        for vt in self.value_types:
            self.invalidate(vt)

    def invalidate(self, vt):
        if self.is_cached_method(vt):
            self.__getattribute__(vt).cache_clear()
        elif self.is_cached_property(vt):
            if vt in self.__dict__:
                del self.__dict__[vt]

    def is_cached_method(self, vt):
        return vt in self.cached_methods

    def is_cached_property(self, vt):
        return vt in self.cached_properties

    @property
    def value_types(self):
        return [m for m in self.__class__.__dict__.keys() if not m.startswith('_')]
