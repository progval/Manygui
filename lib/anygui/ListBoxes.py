from anygui.Components import AbstractComponent
from anygui.Exceptions import UnimplementedMethod
from anygui.Models import ListModel
from UserList import UserList

class AbstractListBox(AbstractComponent):

    _items = () # FIXME: Remove?
    _model = None
    _selection = 0

    # FIXME: When it works, the model stuff should be lifted
    #        to AbstractComponent

    def __init__(self, *args, **kw):
        AbstractComponent.__init__(self, *args, **kw)
        self._set_model(ListModel()) # Default model

    def _get_model(self):
        return self._model

    def _set_model(self, model):
        if self._model is not None:
            self._model.remove_view(self)
        self._model = model
        self._model.add_view(self) # FIXME: Should get all state at this point (?)
        self._items = UserList(model)
        self._ensure_items()

    def model_changed(self, target, change):
        if target is self._model:
            for mname, args, kw in change:
                method = getattr(self._items, mname)
                method(*args, **kw)
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
        raise UnimplementedMethod, (self, '_ensure_items')

    def _ensure_selection(self):
        raise UnimplementedMethod, (self, '_ensure_selection')
