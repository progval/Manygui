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


class BooleanModel(Attrib, Assignee):

    _value = 0

    def __init__(self, *arg, **kw):
        Assignee.__init__(self)
        Attrib.__init__(self, **kw)

    def _set_value(self, value):
        self._value = value
        send(self,_set_value=value)

    def _get_value(self):
        return self._value

    def __repr__(self): return repr(self._value)

    def __str__(self): return str(self._value)


class ListModel(Attrib, Assignee, UserList):

    def __init__(self, *arg, **kw):
        Attrib.__init__(self, **kw)
        Assignee.__init__(self)
        UserList.__init__(self, *arg, **kw)

    def _set_value(self, value):
        self.data = list(value)
        self.send(_set_value=value)

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
        # HACK: Make string argument into list:
        if len(arg) > 0:
            arg = (list(arg[0]),) + arg[1:]
        ListModel.__init__(self, *arg, **kw)

    def _get_value(self):
        return str(self)

    def __repr__(self): return repr(''.join(self.data))

    def __str__(self): return ''.join(self.data)

