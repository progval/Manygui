from .Components import Component
from manygui import Defaults, backendModule

class Button(Component, Defaults.Button):

    def wrapperFactory(self):
        return backendModule().ButtonWrapper(self)
