from anygui.Components import AbstractComponent
from anygui.Exceptions import UnimplementedMethod
from anygui.Models import TextModel

class AbstractTextComponent(AbstractComponent):

    _text = '' # FIXME: Remove?
    _model = None
    _selection = (0, 0)
    _editable = 1

    def __init__(self, *arg, **kw):
        AbstractComponent.__init__(self, *arg, **kw)
        self.model = TextModel()

    # model handling:

    # FIXME: When it works, the model stuff should be lifted
    #        to AbstractComponent

    def _get_model(self):
        return self._model

    def _set_model(self, model):
        if self._model is not None:
            self._model.remove_view(self)
        self._model = model
        self._model.add_view(self) # FIXME: Should get all state at this point (?)
        self._text = str(self._model)
        self._ensure_text()

    def model_changed(self, target, change): # FIXME: Should use hints (?)
        if target is self._model:
            self._text = str(self._model)
            self._ensure_text()

    # text property:

    #def _get_text(self):
    #    text = self._backend_text()
    #    if text is not None:
    #        self._text = text
    #    return self._text

    #def _set_text(self, text):
    #    self._text = text
    #    self._ensure_text()

    def _ensure_text(self):
        raise UnimplementedMethod, (self, '_ensure_text')

    # selection property:
    
    def _get_selection(self):
        selection = self._backend_selection()
        if selection is not None:
            self._selection = selection
        return self._selection
    
    def _set_selection(self, selection):
        self._selection = selection
        self._ensure_selection()

    def _ensure_selection(self):
        raise UnimplementedMethod, (self, '_ensure_selection')

    # editable property

    def _get_editable(self):
        return self._editable

    def _set_editable(self, editable):
        self._editable = editable
        self._ensure_editable

    def _ensure_editable(self):
        raise UnimplementedMethod, (self, '_ensure_editable')


    def _finish_creation(self): # FIXME: Hm...
        AbstractComponent._finish_creation(self)
        self._ensure_text()
        self._ensure_selection()
        self._ensure_editable()
