from anygui.Exceptions import UnimplementedMethod
from anygui.Components import Component
import anygui

class GenericButton(Component):

    def __init__(self, *args, **kwds):
        self._dependant = anygui._backend.ButtonWrapper(self)
        Component.__init__(self, *args, **kwds)

    def _get_text(self):
        return self._text

    def _set_text(self, text):
        if self._text != text:
            self._text = text

    def _ensure_text(self):
        raise UnimplementedMethod, (self, "_ensure_text")
