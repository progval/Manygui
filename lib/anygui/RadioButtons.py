from anygui.Exceptions import UnimplementedMethod
from anygui.Components import Component
from anygui import Defaults,backendModule

class RadioButton(Component, Defaults.RadioButton):

    def __init__(self,value=1,*args,**kws):
        Component.__init__(self,*args,**kws)
        self.value = int(value)
        self.on = 0

    def wrapperFactory(self):
        return backendModule().RadioButtonWrapper(self)
