from anygui import application
from anygui.Frames import AbstractFrame
from anygui.Exceptions import UnimplementedMethod
from anygui import Defaults
#import inspect

class AbstractWindow(AbstractFrame, Defaults.Window):

    def __init__(self, *args, **kw):
        AbstractFrame.__init__(self, *args, **kw)

        # Window staggering code:
        # FIXME: Should be offset from current top window, if any
        self._x = Defaults.Window._x
        self._y = Defaults.Window._y
        Defaults.shift_window()
        
    def destroy(self):
        self._ensure_destroyed()
        try:
            application().remove(self)
        except ValueError:
            # Already removed
            pass
