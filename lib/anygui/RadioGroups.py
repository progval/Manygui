from anygui.Exceptions import UnimplementedMethod
from anygui.Mixins import Attrib
from anygui.Messages import send, CallbackAdapter

class RadioGroup(Attrib, CallbackAdapter):
    _items = None
    _value = None

    def __init__(self, items=[], **kw):
        Attrib.__init__(self, **kw)
        CallbackAdapter.__init__(self)
        self._items = []
        self.add(items)

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        if self._value != value:
            self._value = value
            for item in self._items:
                item._update_state()
            #self.do_action()
            #send('action', self)

    def add(self, buttons):
        for btn in buttons:
            btn.group = self

    def remove(self, buttons):
        for btn in buttons:
            if btn in self._items:
                btn.group = None
