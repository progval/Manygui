from anygui.Exceptions import UnimplementedMethod
from anygui.Components import Component
from anygui import Defaults,backendModule

class RadioButton(Component, Defaults.RadioButton):

    def wrapperFactory(self):
        return backendModule().RadioButtonWrapper(self)
