from anygui.ToggleButtons import ToggleButton
from anygui import Defaults, backendModule

class CheckBox(ToggleButton, Defaults.CheckBox):

    def wrapperFactory(self):
        return backendModule().CheckBoxWrapper(self)
