
import UserList, UserDict, sys, types

weakref = None

from Utils import generic_hash

# Possible additions:
# - Add callbacks to CallableReference
# - Reimplement RefValueList

def ref(obj, weak, plain=0):
    if not plain and is_callable(obj):
        return CallableReference(obj, weak)
    if weak:
        return WeakReference(obj)
    else:
        return StrongReference(obj)

def mapping(init={}): return RefKeyDictionary(init)

def is_callable(obj):
    if callable(obj): return 1
    try:
        return callable(obj[1])
    except:
        return 0

def ref_is(ref1, ref2):
    if ref1 is ref2: return 1
    o1 = ref1()
    o2 = ref2()
    if o1 is None or o2 is None: return 0
    return o1 is o2

class Hashable:
    def __hash__(self):
        return self.hash

class Reference(Hashable):
    def callback(self, obj):
        for cb in self.callbacks:
            cb(obj, self)
        self.callbacks = []
    def __init__(self, obj):
        self.obj = self.ref(obj, self.callback)
        self.callbacks = []
        self.hash = generic_hash(obj)
    def __call__(self):
        return self.deref(self.obj)
    def __eq__(self,other):
        return ref_is(self, other)

class WeakReference(Reference):
    def ref(self, obj, cb):
        global weakref
        if not weakref: import weakref
        return weakref.ref(obj, cb)
    def deref(self, obj):
        return obj()

class StrongReference(Reference):
    def ref(self, obj, cb):
        return obj
    def deref(self, obj):
        return obj

class CallableWrapper:
    def __init__(self, obj, func):
        self.obj = obj
        self.func = func
    def __call__(self, *args, **kwds):
        if self.obj is None:
            return self.func(*args, **kwds)
        else:
            return self.func(self.obj, *args, **kwds)

def is_callable_instance(obj):
    return type(obj) is types.InstanceType and \
           hasattr(obj, '__call__')

def is_method(obj):
    return hasattr(obj, 'im_self')

def unwrap(func):
    try:
        obj, func = func
    except:
        obj = None
    if is_callable_instance(func):
        func = func.__call__
    if is_method(func):
        if func.im_self is not None:
            if obj is None: obj = func.im_self
            else: assert obj is func.im_self
        func = func.im_func
    return obj, func

class CallableReference(Hashable):
    
    def __init__(self, func, weak):
        obj, func = unwrap(func)

        self.hash = hash((obj, func))

        if obj is not None:
            obj = ref(obj, weak, plain=1)
        self.obj = obj
        
        self.func = ref(func, weak, plain=1)

    def is_dead(self):
        return self.obj is not None and self.obj() is None \
               or self.func() is None

    def __call__(self):
        if self.is_dead(): return None
        obj = self.obj
        if obj is not None: obj = obj()
        func = self.func()
        return CallableWrapper(obj, func)

    def __eq__(self,other):
        return (ref_is(self.obj,other.obj) and
                ref_is(self.func,self.func))

class RefKeyDictionary(UserDict.UserDict):

    def __repr__(self):
        return "<RefKeyDictionary at %s>" % id(self)

    def callback(self, obj, key):
        del self[key]

    def add_callback(self, key):
        key.callbacks.append(self.callback)

    def __setitem__(self, key, value):
        obj = key()
        if obj is not None:
            self.add_callback(key)
            self.data[key] = value

    def copy(self):
        new = RefKeyDictionary()
        for key, value in self.data.items():
            obj = key()
            if obj is not None:
                new[obj] = value
        return new

    def items(self):
        L = []
        for key, value in self.data.items():
            obj = key()
            if obj is not None:
                L.append((key, value))
        return L

    def iteritems(self):
        return RefKeyedItemIterator(self)

    def iterkeys(self):
        return RefKeyedKeyIterator(self)
    __iter__ = iterkeys

    def itervalues(self):
        return self.data.itervalues()

    def keys(self):
        L = []
        for key in self.data.keys():
            obj = key()
            if obj is not None:
                L.append(key)
        return L

    def popitem(self):
        while 1:
            key, value = self.data.popitem()
            obj = key()
            if obj is not None:
                return key, value

    def update(self, dict):
        for key, value in dict.items():
            self[key] = value

class BaseIter:
    def __iter__(self):
        return self


class RefKeyedKeyIterator(BaseIter):
    def __init__(self, refdict):
        self._next = refdict.data.iterkeys().next

    def next(self):
        while 1:
            key = self._next()
            obj = key()
            if obj is not None:
                return key


class RefKeyedItemIterator(BaseIter):
    def __init__(self, refdict):
        self._next = refdict.data.iteritems().next

    def next(self):
        while 1:
            key, value = self._next()
            obj = key()
            if obj is not None:
                return key, value

class RefValueList(UserList.UserList):
    pass # TBD
