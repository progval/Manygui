from anygui import application
from anygui.Frames import AbstractFrame
from anygui.Exceptions import UnimplementedMethod
from anygui import Defaults
import inspect

class AbstractWindow(AbstractFrame, Defaults.Window):

    class CreationSentinel:
        'Calls win.ensure_created() when leaving local scope'
        def __init__(self, win):
            self.win = win
        def __del__(self):
            self.win.ensure_created()

    def __init__(self, *args, **kw):
        AbstractFrame.__init__(self, *args, **kw)

        # Window staggering code:
        # FIXME: Should be offset from current top window, if any
        self._x = Defaults.Window._x
        self._y = Defaults.Window._y
        Defaults.shift_window()
        
        application()._add_window(self)

        # If we are inside a function call, set up a CreationSentinel
        # in surrounding local scope -- otherwise, just call
        # ensure_created:                               (mlh20011110)
        stack = inspect.stack()
        if len(stack) > 2: # Is this check correct?
            scope = stack[1][0].f_locals
            name = 0
            while scope.has_key(`name`): name += 1
            scope[`name`] = self.CreationSentinel(self)
        else:
            pass # Do something here?
        del stack # Needed to make the sentinel work (odd...)
        
    def destroy(self):
        self._ensure_destroyed()
        application()._remove_window(self)

    def _set_title(self, text):
        if self._title != text:
            self._title = text
            self._ensure_title()

    def _get_title(self):
        return self._title

    def _ensure_title(self):
        raise UnimplementedMethod, (self, "_ensure_title")
