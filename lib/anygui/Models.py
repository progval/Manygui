from Attribs import Attrib
from Events import link, unlink, send, caller
from UserList import UserList
from UserString import UserString

# FIXME: Fix link(self, sync) to use the caller() function; deal with
# unlinking problems.

class Assignee:

    def __init__(self):
        self.names = []
        self.objects = []

    def installed(self, object, name):
        push = getattr(object, 'push', None)
        if push is not None:
            self.names.append(name)
            self.objects.append(object)
            
    def removed(self, object, name):
        push = getattr(object, 'push', None)
        if push is not None:
            self.objects.remove(object)
            self.names.remove(name)

    def send(self, **kwds):
        for object in self.objects:
            object.push(names=self.names)
        send(self, **kwds)


class Model(Assignee):

    def __init__(self, *arg, **kw):
        Assignee.__init__(self)
        #Attrib.__init__(self, **kw)


class BooleanModel(Model):

    _value = 0

    def setValue(self, value):
        self._value = value
        self.send()

    def getValue(self):
        return self._value

    def __repr__(self): return repr(self._value)

    def __str__(self): return str(self._value)

    def __int__(self): return self._value


class ListModel(Model, UserList):


    def __init__(self, *arg, **kw):
        Model.__init__(self, **kw)
        UserList.__init__(self, *arg, **kw)
        
    def setValue(self, value):
        self.data[:] = list(value)

    def getValue(self):
        return list(self)

    def __setitem__(self, i, item):
        UserList.__setitem__(self, i, item)
        self.send()

    def __delitem__(self, i):
        UserList.__delitem__(self, i)
        self.send()

    def __setslice__(self, i, j, other):
        UserList.__setslice__(self, i, j, other)
        self.send()
        
    def __delslice__(self, i, j):
        UserList.__delslice__(self, i, j)
        self.send()
        
    def __iadd__(self, other):
        UserList.__iadd__(self, other)
        self.send()
        
    def __imul__(self, n):
        UserList.__imul__(self, n)
        self.send()
        
    def append(self, item):
        UserList.append(self, item)
        self.send()
    
    def insert(self, i, item):
        UserList.insert(self, i, item)
        self.send()
        
    def pop(self, i=-1):
        result = UserList.pop(self, i)
        self.send()
        return result
    
    def remove(self, item):
        UserList.remove(self, item)
        self.send()
        
    def reverse(self):
        UserList.reverse(self)
        self.send()
        
    def sort(self, *args):
        UserList.sort(self, *args)
        self.send()
        
    def extend(self, other):
        UserList.extend(self, other)
        self.send()


class TextModel(ListModel):

    data = []

    def __init__(self, *arg, **kw):
        if len(arg) > 0:
            arg = (list(arg[0]),) + arg[1:]
        ListModel.__init__(self, *arg, **kw)

    def getValue(self):
        return str(self)

    def __repr__(self): return repr(''.join(self.data))

    def __str__(self): return ''.join(self.data)


# when 2.2 is the standard, just multiply inherit from Model
# and the appropriate builtin type and have appropriate _set_value
# and _get_value accessors depending on the type -- all of the
# boilerplate specialmethods as in the following class NumberModel
# won't be needed then.  For example:
#     class IntModel(int, ModelThatInheritsFromObject):
#         _value = 0
#         def _set_value(self, value):
#             self._value = value
#         def _get_value(self):
#             return self._value
# Note the setter/getter can be avoided for immutable builtins.

class NumberModel(Model):

    _value = 0

    def __abs__(self): return abs(self.value)
    def __add__(self, other): return self.value + other
    def __and__(self, other): return self.value & other
    def __cmp__(self, other): return cmp(self.value, other)
    def __coerce__(self, other): return coerce(self.value, other)
    def __div__(self, other): return self.value/other
    def __divmod__(self, other): return divmod(self.value, other)
    def __float__(self): return float(self.value)
    # not immutable, as _value can be set, so, no hash allowed:
    # def __hash__(self): return hash(self.value)
    def __hex__(self): return hex(self.value)
    def __int__(self): return int(self.value)
    def __invert__(self): return ~ self.value
    def __long__(self): return long(self.value)
    def __lshift__(self, other): return self.value << other
    def __mod__(self, other): return self.value % other
    def __mul__(self, other): return self.value * other
    def __neg__(self): return - self.value
    def __nonzero__(self): return self.value != 0
    def __oct__(self): return oct(self.value)
    def __or__(self, other): return self.value | other
    def __pos__(self): return self.value
    def __pow__(self, other): return self.value ** other
    def __radd__(self, other): return other + self.value
    def __rand__(self, other): return other & self.value
    def __rdiv__(self, other): return other / self.value
    def __rdivmod__(self, other): return divmod(other, self.value)
    def __repr__(self): return repr(self.value)
    def __rlshift__(self, other): return other << self.value
    def __rmod__(self, other): return other % self.value
    def __rmul__(self, other): return other * self.value
    def __ror__(self, other): return other | self.value
    def __rpow__(self, other): return other ** self.value
    def __rrshift__(self, other): return other >> self.value
    def __rshift__(self, other): return self.value >> other
    def __rsub__(self, other): return other - self.value
    def __rxor__(self, other): return other ^ self.value
    def __str__(self): return str(self.value)
    def __sub__(self, other): return self.value - other
    def __xor__(self, other): return self.value ^ other

