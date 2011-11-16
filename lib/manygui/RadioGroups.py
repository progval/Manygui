from manygui.Exceptions import UnimplementedMethod
from manygui.Attribs import Attrib
from manygui import Defaults
from .Utils import flatten,log

class RadioGroup(Attrib, Defaults.RadioGroup):

    def __init__(self, buttons=[], **kw):
        Attrib.__init__(self, **kw)
        self._items = []
        self.add(buttons)

    def getValue(self):
        log(self,"getValue",self._items)
        for btn in self._items:
            if btn.on:
                return int(btn.value)
        return None

    def setValue(self, value):
        for btn in self._items:
            btn.on = 0
            if btn.value == value:
                btn.on = 1

    def add(self, buttons):
        for btn in flatten(buttons):
            if btn.group != self:
                self._items.append(btn)
                btn.group = self

    def remove(self, buttons):
        for btn in buttons:
            if btn in self._items:
                btn.group = None
                self._items.remove(btn)
