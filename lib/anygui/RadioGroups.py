from anygui.Exceptions import UnimplementedMethod
from anygui.Mixins import Attrib
from anygui.Events import send

class RadioGroup(Attrib):
    _items = None
    _value = None

    def __init__(self, items=[], **kw):
        Attrib.__init__(self, **kw)
        self._items = []
        self.add(items)

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        if 1 or self._value != value:
            self._value = value
            for item in self._items:
                item._update_state()
            #self.do_action()
            send(self, 'action')

    def add(self, buttons):
        for btn in buttons:
            btn.group = self

    def remove(self, buttons):
        for btn in buttons:
            if btn in self._items:
                btn.group = None
