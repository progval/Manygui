from anygui.Mixins import Attrib
from Events import link, unlink, send
from UserList import UserList
from UserString import UserString


class Assignee:

    def __init__(self):
        self.names = []

    def assigned(self, object, name):
        update = getattr(object, 'update', None)
        if update is not None:
            self.names.append(name)
            link(self, update)

    def removed(self, object, name):
        update = getattr(object, 'update', None)
        if update is not None:
            unlink(self, update)
            self.names.remove(name)

    def send(self, **kw):
        send(self, names=self.names, **kw)


class Model(Attrib, Assignee):

    def update(self, **kwds):
        self.send(**kwds)

    def __init__(self, *arg, **kw):
        Assignee.__init__(self)
        Attrib.__init__(self, **kw)


class BooleanModel(Model):

    _value = 0

    def _set_value(self, value):
        self._value = value

    def _get_value(self):
        return self._value

    def __repr__(self): return repr(self._value)

    def __str__(self): return str(self._value)


class ListModel(Model, UserList):

    def __init__(self, *arg, **kw):
        Model.__init__(self, **kw)
        UserList.__init__(self, *arg, **kw)

    def _set_value(self, value):
        self.data[:] = list(value)

    def _get_value(self):
        return list(self)

    def __setitem__(self, i, item):
        UserList.__setitem__(self, i, item)
        self.send(__setitem__=(i,item))

    def __delitem__(self, i):
        UserList.__delitem__(self, i)
        self.send(__delitem__=i)

    def __setslice__(self, i, j, other):
        UserList.__setslice__(self, i, j, other)
        self.send(__setslice__=(i,j,other))
        
    def __delslice__(self, i, j):
        UserList.__delslice__(self, i, j)
        self.send(__delslice__=(i,j))
        
    def __iadd__(self, other):
        UserList.__iadd__(self, other)
        self.send(__iadd__=other)
        
    def __imul__(self, n):
        UserList.__imul__(self, n)
        self.send(__imul__=n)
        
    def append(self, item):
        UserList.append(self, item)
        self.send(append=item)
    
    def insert(self, i, item):
        UserList.insert(self, i, item)
        self.send(insert=(i,item))
        
    def pop(self, i=-1):
        result = UserList.pop(self, i)
        self.send(pop=i)
        return result
    
    def remove(self, item):
        UserList.remove(self, item)
        self.send(remove=item)
        
    def reverse(self):
        UserList.reverse(self)
        self.send(reverse=1)
        
    def sort(self, *args):
        UserList.sort(self, *args)
        self.send(sort=1)
        
    def extend(self, other):
        UserList.extend(self, other)
        self.send(extend=other)


class TextModel(ListModel):

    data = []

    def __init__(self, *arg, **kw):
        if len(arg) > 0:
            arg = (list(arg[0]),) + arg[1:]
        ListModel.__init__(self, *arg, **kw)

    def _get_value(self):
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
    def __hash__(self): return hash(self.value)
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

