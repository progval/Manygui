from anygui.Exceptions import UnimplementedMethod
from anygui.GenericButtons import AbstractGenericButton

class AbstractToggleButton(AbstractGenericButton):

    _on = 0

    def __init__(self, *args, **kw):
        AbstractGenericButton.__init__(self, *args, **kw)

    def _get_on(self):
        try: return self._on.value
        except: return self._on

    def _set_on(self, on):
        try: self._on.value = on
        except: self._on = on

    def _finish_creation(self):
        AbstractGenericButton._finish_creation(self)
        self._ensure_state()

    def _ensure_state(self):
        raise UnimplementedMethod, (self, "_ensure_state")
