from Components import Component
from anygui import Defaults, backendModule

class Button(Component, Defaults.Button):

    def wrapperFactory(self):
        return backendModule().ButtonWrapper(self)
