from anygui.Components import AbstractComponent

class AbstractListBox(AbstractComponent):

    _items = ()
    _selection = 0

    def _get_items(self):
        return self._items

    def _set_items(self, items):
        self._items = tuple(items) # Must be non-editable
        self._ensure_items()

    def _get_selection(self):
        selection = self._backend_selection()
        if selection is not None:
            self._selection = selection
        return self._selection
    
    def _set_selection(self, selection):
        self._selection = selection
        self._ensure_selection()
        
    def _finish_creation(self): # FIXME: Hm...
        AbstractComponent._finish_creation(self)
        self._ensure_items()
        self._ensure_selection()

    def _ensure_items(self):
        return UnimplementedMethod, '_ensure_items'

    def _ensure_selection(self):
        return UnimplementedMethod, '_ensure_selection'
