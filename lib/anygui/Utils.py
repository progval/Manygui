'Anygui utilities.'

from weakref import ref

# Support for using bound methods with weak references.
# See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81253

class WeakCallable:
    def __init__(self, obj, func):
        try:
            self.obj = ref(obj)
        except TypeError:
            self.obj = None
        self.meth = func
    def __call__(self, *args, **kwds):
        if self.obj is not None:
            return self.meth(self.obj, *args, **kwds)
        else:
            return self.meth(*args, **kwds)

class WeakMethod:
    def __init__(self, func):
        try:
            obj, func = func
        except TypeError:
            obj, func = None, func
        if obj and hasattr(func, 'im_self'):
            assert obj is func.im_self
        try:
            self.obj = ref(func.im_self)
            self.meth = func.im_func
        except AttributeError:
            self.obj = None
            self.meth = func
    def get_obj(self):
        if self.obj is None: return None
        return self.obj()
    def __eq__(self, other):
        if self.obj == other.obj:
            if self.meth == other.meth:
                return 1
        return 0
    def __call__(self):
        if self.dead(): return None
        obj = self.obj
        if obj is not None: obj = obj()
        return WeakCallable(obj, self.meth)
    def dead(self):
        return self.obj is not None and self.obj() is None

class HashableWeakRef:
    def __init__(self, obj):
        if obj is None:
            self.ref = None
        else:
            self.ref = ref(obj)
    def __call__(self):
        if self.ref is None:
            return None
        return self.ref()
#    def __cmp__(self, other):
#        if id(self.ref)<id(other_ref): return 1
#        if id(self.ref)>id(other_ref): return -1
#        return 0
    def __hash__(self):
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
