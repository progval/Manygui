from manygui.ToggleButtons import ToggleButton
from manygui import Defaults, backendModule

class CheckBox(ToggleButton, Defaults.CheckBox):

    def wrapperFactory(self):
        return backendModule().CheckBoxWrapper(self)
