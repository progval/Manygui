from anygui.Exceptions import UnimplementedMethod
from anygui.GenericButtons import GenericButton

class ToggleButton(GenericButton):

    _on = 0

    def __init__(self, *args, **kw):
        GenericButton.__init__(self, *args, **kw)

    def _get_on(self):
        try: return self._on.value
        except: return self._on

    def _set_on(self, on):
        try: self._on.value = on
        except: self._on = on

    # def _finish_creation(self):
        # GenericButton._finish_creation(self)
        # self._ensure_state()

    def _ensure_state(self):
        raise UnimplementedMethod, (self, "_ensure_state")
