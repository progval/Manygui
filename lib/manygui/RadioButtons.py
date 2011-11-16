from manygui.Exceptions import UnimplementedMethod
from manygui.Components import Component
from manygui import Defaults,backendModule

class RadioButton(Component, Defaults.RadioButton):

    def wrapperFactory(self):
        return backendModule().RadioButtonWrapper(self)
