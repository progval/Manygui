from anygui import application
from anygui.Frames import AbstractFrame
from anygui.Exceptions import UnimplementedMethod
from anygui import Defaults

class AbstractWindow(AbstractFrame, Defaults.Window):

    def __init__(self, *args, **kw):
        #self.visible = 0
        AbstractFrame.__init__(self, *args, **kw)
        application()._add_window(self)
        
    def destroy(self):
        self._ensure_destroyed()
        application()._remove_window(self)

    def show(self):
        "Alias for window.visible = 1. Needed?"
        self._set_visible(1)

    def hide(self):
        "Alias for window.visible = 0. Needed?"
        self._set_visible(0)

    def _set_title(self, text):
        if self._title != text:
            self._title = text
            self._ensure_title()

    def _get_title(self):
        return self._title

    def _ensure_title(self):
        raise UnimplementedMethod, (self, "_ensure_title")
