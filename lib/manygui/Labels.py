from .Components import Component
from manygui import Defaults, backendModule

class Label(Component, Defaults.Label):

    def wrapperFactory(self):
        return backendModule().LabelWrapper(self)


'''
    _original_text = Defaults.Label._text

    def _get_text(self):
        return self._original_text

    def _set_text(self, text):
        if self._original_text != text:
            self._original_text = text
            text = text.replace('\r\n', ' ')
            text = text.replace('\n', ' ')
            text = text.replace('\r', ' ')
            self._text = text
            # self._ensure_text()

    #def _set_font(self, font):
    #    if self._font != font:
    #        self._font = font
    #        self._ensure_font()

    #def _getfont(self):
    #    return self._font

    #def _set_color(self, color):
    #    if self._color != color:
    #        self._color = color
    #        self._ensure_color()

    def _ensure_text(self):
        raise UnimplementedMethod, (self, "_ensure_text")

    #def _ensure_font(self):
    #    raise UnimplementedMethod, (self, "_ensure_font")

    #def _ensure_color(self):
    #    raise UnimplementedMethod, (self, "_ensure_color")
'''