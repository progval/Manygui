from manygui.TextComponents import TextComponent
from manygui import Defaults,backendModule

class TextArea(TextComponent, Defaults.TextArea):

    def wrapperFactory(self):
        return backendModule().TextAreaWrapper(self)
