import anygui.backends.genericgui
from anygui.Components import Component
from anygui import Defaults, backendModule

class ComboBox(Component, Defaults.ComboBox):

    def wrapperFactory(self):
        try:
            return backendModule().ComboBoxWrapper(self)
        except(AttributeError):
            return anygui.backends.genericgui.ComboBoxWrapper(self)
