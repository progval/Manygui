from anygui.Components import Component
from anygui import Defaults, backendModule, frontEndWrappers

class ComboBox(Component, Defaults.ComboBox):

    def wrapperFactory(self):
        try:
            return backendModule().ComboBoxWrapper(self)
        except(AttributeError):
            return frontEndWrappers().ComboBoxWrapper(self)