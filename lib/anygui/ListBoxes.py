from anygui.Components import AbstractComponent
from anygui.Exceptions import UnimplementedMethod
from anygui.Models import ListModel
from UserList import UserList
from anygui import Defaults

class AnyguiList(UserList):

    def __init__(self,items=[]):
        UserList.__init__(self,items)

    def _set_value(self,items):
        self.data = items

class AbstractListBox(AbstractComponent, Defaults.ListBox):

    def __init__(self, *args, **kw):
        AbstractComponent.__init__(self, *args, **kw)

    def _get_items(self):
        return self._items

    def _set_items(self, items):
        self._items = items

    def _get_selection(self):
        selection = self._backend_selection()
        if selection is not None:
            self._selection = selection
        return self._selection
    
    def _set_selection(self, selection):
        self._selection = selection
        # self._ensure_selection()
        
    def _finish_creation(self): # FIXME: Hm...
        AbstractComponent._finish_creation(self)
        # self._ensure_items()
        # self._ensure_selection()

    def _ensure_items(self):
        raise UnimplementedMethod, (self, '_ensure_items')

    def _ensure_selection(self):
        raise UnimplementedMethod, (self, '_ensure_selection')
