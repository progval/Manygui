from manygui.TextComponents import TextComponent
from manygui import Defaults,backendModule

class TextField(TextComponent, Defaults.TextField):

    def wrapperFactory(self):
        return backendModule().TextFieldWrapper(self)
