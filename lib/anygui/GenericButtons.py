from anygui.Exceptions import UnimplementedMethod
from anygui.Components import Component

class GenericButton(Component):

    def _get_text(self):
        return self._text

    def _set_text(self, text):
        if self._text != text:
            self._text = text

    def _ensure_text(self):
        raise UnimplementedMethod, (self, "_ensure_text")
