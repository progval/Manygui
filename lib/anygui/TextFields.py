from anygui.TextComponents import TextComponent
from anygui import Defaults,backendModule

class TextField(TextComponent, Defaults.TextField):

    def wrapperFactory(self):
        return backendModule().TextFieldWrapper(self)
