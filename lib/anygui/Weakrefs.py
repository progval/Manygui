'Utility classes for dealing with weak references.'

from weakref import ref

# Support for using bound methods and hashable objects
# with weak references.

# Based on the weak callable recipe from the Python Cookbook:
# See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81253

# These weakref wrappers may have their weakref behaviour
# turned off by supplying the keyword argument weak=0 to their
# constructors.

class WeakCallable:
    def __init__(self, obj, func, weak=1):
        self.weak = weak
        if weak:
            try:
                self.obj = ref(obj)
            except TypeError:
                self.obj = None
        else:
            self.obj = obj
        self.meth = func
    def __call__(self, *args, **kwds):
        if self.obj is not None:
            if self.weak:
                return self.meth(self.obj(), *args, **kwds)
            else:
                return self.meth(self.obj, *args, **kwds)
        else:
            return self.meth(*args, **kwds)

class WeakMethod:
    def __init__(self, func, weak=1):
        self.weak = weak
        try:
            obj, func = func
        except TypeError:
            obj, func = None, func
        if obj and hasattr(func, 'im_self'):
            assert obj is func.im_self
        try:
            if weak:
                self.obj = ref(func.im_self)
            else:
                self.obj = func.im_self
            self.meth = func.im_func
        except AttributeError:
            if weak:
                self.obj = ref(obj)
            else:
                self.obj = obj
            self.meth = func
    def get_obj(self):
        if self.obj is None: return None
        if self.weak:
            return self.obj()
        else:
            return self.obj
    def __eq__(self, other):
        if self.weak:
            self_obj = self.obj()
        else:
            self_obj = self.obj
        if other.weak:
            other_obj = other.obj()
        else:
            other_obj = other.obj
        if self_obj == other_obj:
            if self.meth == other.meth:
                return 1
        return 0
    def __call__(self):
        if self.dead(): return None
        obj = self.obj
        if obj is not None and self.weak: obj = obj()
        return WeakCallable(obj, self.meth, weak=self.weak)
    def dead(self):
        return self.obj is not None and \
               self.weak and self.obj() is None

class HashableWeakRef:
    def __init__(self, obj, weak=1):
        self.weak = weak
        if obj is None:
            self.ref = None
        elif weak:
            self.ref = ref(obj)
        else:
            self.ref = obj
    def __call__(self):
        if self.ref is None:
            return None
        elif self.weak:
            return self.ref()
        else:
            return self.ref
    def __eq__(self, other):
        if self.weak:
            self_ref = self.ref()
        else:
            self_ref = self.ref
        if other.weak:
            other_ref = other.ref()
        else:
            other_ref = other.ref
        if self_ref == other_ref:
                return 1
        return 0
    def __hash__(self):
        if self.weak:
            return id(self.ref())
        else:
            return id(self.ref)

# To be phased out with the place() method
def flatten(seq):
    '''Flatten a sequence. If seq is not a sequence, return [seq].
    If seq is empty, return [].'''
    try:
        if len(seq) > 0:
            seq[0]
    except:
        return [seq]
    result = []
    for item in seq:
        result += flatten(item)
    return result
