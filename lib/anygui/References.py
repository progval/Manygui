
import weakref, UserList, UserDict

# TODO:
# - Add callbacks to CallableReference
# - Reimplement RefKeyDictionary and RefValueList

def ref(obj, weak, plain=0):
    if not plain and is_callable(obj):
        return CallableReference(obj, weak)
    if weak:
        return WeakReference(obj)
    else:
        return StrongReference(obj)

def is_callable(obj):
    if callable(obj): return 1
    try:
        return callable(obj[1])
    except:
        return 0

class Hashable:
    def __hash__(self):
        return self.hash
    def __cmp__(self, other):
        return cmp(self.hash, other.hash)

class Reference(Hashable):
    def callback(self, obj):
        for cb in self.callbacks:
            cb(obj, self)
        self.callbacks = []
    def __init__(self, obj):
        self.obj = self.ref(obj, self.callback)
        self.callbacks = []
        self.hash = id(obj)
    def __call__(self):
        return self.deref(self.obj)

class WeakReference(Reference):
    def ref(self, obj, cb):
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

def unwrap(func):
    try:
        obj, func = func
    except:
        obj = None
    if hasattr(func, '__call__'):
        func = func.__call__
    if hasattr(func, 'im_self'):
        if func.im_self is not None:
            if obj is None: obj = func.im_self
            else: assert obj is func.im_self
        func = func.im_func
    return obj, func

class CallableReference(Hashable):
    
    def __init__(self, func, weak):
        obj, func = unwrap(func)

        if obj is not None:
            obj = ref(obj, weak, plain=1)
        self.obj = obj
        
        self.func = ref(func, weak, plain=1)
        
        self.hash = hash((obj, func))

    def is_dead(self):
        return self.obj is not None and self.obj() is None \
               or self.func() is None

    def __call__(self):
        if self.is_dead(): return None
        obj = self.obj
        if obj is not None: obj = obj()
        func = self.func()
        return CallableWrapper(obj, func)

class RefKeyDictionary(UserDict.UserDict): pass

class RefValueList(UserList.UserList): pass
