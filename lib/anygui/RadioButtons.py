from anygui.Exceptions import UnimplementedMethod
from anygui.Components import Component
from anygui import Defaults,backendModule

class RadioButton(Component, Defaults.RadioButton):

    def __init__(self,value=1,*args,**kws):
        Component.__init__(self,*args,**kws)
        self.value = int(value) # @@@ This should be done through the default mechanism
        self.on = 0 # @@@ This should be done through the default mechanism

    def wrapperFactory(self):
        return backendModule().RadioButtonWrapper(self)
