from anygui.Exceptions import UnimplementedMethod
from anygui.Mixins import Attrib
from anygui.ToggleButtons import AbstractToggleButton
from anygui import Defaults

class AbstractRadioButton(AbstractToggleButton, Defaults.RadioButton):

    _group = None
    _value = None

    def _get_group(self):
        return self._group

    def _set_group(self, new_group):
        old_group = self._group
        if new_group is not old_group:
            if old_group:
                old_group._items.remove(self)
            self._group = new_group
            if new_group:
                new_group._items.append(self)
                self._update_state()

    def _update_state(self):
        group = self._group
        if group:
            self.on = self._value == group._value
            self._ensure_state()

    def _get_value(self):
        return self._value

    def _set_value(self, new_value):
        if new_value != self._value:
            self._value = new_value
            self._update_state()

    def do_action(self):
        group = self._group
        if group:
            group.value = self._value
        AbstractToggleButton.do_action(self)
