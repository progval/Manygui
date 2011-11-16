import manygui.backends.genericgui
from manygui.Components import Component
from manygui import Defaults, backendModule

class ComboBox(Component, Defaults.ComboBox):

    def wrapperFactory(self):
        try:
            return backendModule().ComboBoxWrapper(self)
        except(AttributeError):
            return manygui.backends.genericgui.ComboBoxWrapper(self)
