from anygui.TextComponents import TextComponent
from anygui import Defaults,backendModule

class TextArea(TextComponent, Defaults.TextArea):

    def wrapperFactory(self):
        return backendModule().TextAreaWrapper(self)
