
import weakref

def ref(obj, weak):
    if weak:
        return WeakReference(obj)
    else:
        return StrongReference(obj)

class Hashable:
    def __hash__(self):
        return self.hash
    def __cmp__(self, other):
        return cmp(self.hash, other.hash)

class Reference(Hashable):
    def __init__(self, obj):
        self.obj = self.ref(obj)
        self.hash = id(obj)
    def __call__(self):
        return self.deref(self.obj)

class WeakReference(Reference):
    def ref(self, obj):
        return weakref.ref(obj)
    def deref(self, obj):
        return obj()

class StrongReference(Reference):
    def ref(self, obj):
        return obj
    def deref(self, obj):
        return obj

class CallableWrapper(Hashable):
    def __init__(self, func):
        pass
    def __call__(self, *args, **kwds):
        pass

class CallableReference: pass

class RefKeyDictionary: pass

class RefValueList: pass
