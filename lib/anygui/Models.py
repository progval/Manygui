from anygui.Mixins import Attrib, Observable
from UserList import UserList

class ListModel(Attrib, Observable, UserList):

    def __init__(self, *arg, **kw):
        Attrib.__init__(self, **kw)
        Observable.__init__(self)
        UserList.__init__(self, *arg, **kw)
        self._selection = -1

    def _set_selection(self, selection):
        self._selection = selection
        self.notify_views()

    def _get_selection(self):
        return self._selection

    def __setitem__(self, i, item):
        UserList.__setitem__(self, i, item)
        self.notify_views()

    def __delitem__(self, i):
        UserList.__delitem__(self, i)
        self.notify_views()

    def __setslice__(self, i, j, other):
        UserList.__setslice__(self, i, j, other)
        self.notify_views()
        
    def __delslice__(self, i, j):
        UserList.__delslice__(self, i, j)
        self.notify_views()
        
    def __iadd__(self, other):
        UserList.__iadd__(self, other)
        self.notify_views()
        
    def __imul__(self, n):
        UserList.__imul__(self, n)
        self.notify_views()
        
    def append(self, item):
        UserList.__append__(self, item)
        self.notify_views()
    
    def insert(self, i, item):
        UserList.insert(self, i, item)
        self.notify_views()
        
    def pop(self, i=-1):
        result = UserList.pop(self, i)
        self.notify_views()
        return result
    
    def remove(self, item):
        UserList.remove(self, item)
        self.notify_views()
        
    def reverse(self):
        UserList.reverse(self)
        self.notify_views()
        
    def sort(self, *args):
        UserList.sort(self, *args)
        self.notify_views()
        
    def extend(self, other):
        UserList.extend(self, other)
        self.notify_views()
