from anygui.Exceptions import UnimplementedMethod
from anygui.Mixins import Attrib, DefaultEventMixin
from anygui.Events import send
from anygui import Defaults

class RadioGroup(Attrib, Defaults.RadioGroup, DefaultEventMixin):
    _items = None
    _value = None

    def __init__(self, items=[], **kw):
        Attrib.__init__(self, **kw)
        DefaultEventMixin.__init__(self)
        self._items = []
        self.add(items)

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        if 1 or self._value != value: # FIXME: Why is this "commented out"?
            self._value = value
            for item in self._items:
                item._update_state()
        send(self, 'select', loop=1)

    def add(self, buttons):
        for btn in buttons:
            btn.group = self

    def remove(self, buttons):
        for btn in buttons:
            if btn in self._items:
                btn.group = None
                #self._items.remove(btn)
