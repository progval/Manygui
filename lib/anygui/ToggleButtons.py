from anygui.Exceptions import UnimplementedMethod
from anygui.GenericButtons import AbstractGenericButton

class AbstractToggleButton(AbstractGenericButton):
    _text = "ToggleButton"
    _on = 0
    
    def _set_on(self, value):
        value = not not value
        if not self._on == value:
            self._on = value
            self._ensure_state()

    def _get_on(self):
        return self._on

    def _finish_creation(self):
        AbstractGenericButton._finish_creation(self)
        self._ensure_state()

    def _ensure_state(self):
        raise UnimplementedMethod, (self, "_ensure_state")
