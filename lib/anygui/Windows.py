from anygui import application, Defaults
from anygui.Frames import Frame
from anygui.Exceptions import UnimplementedMethod
import anygui

class Window(Frame, Defaults.Window):

    def __init__(self, *args, **kw):
        self._dependant = anygui._backend.WindowWrapper(self)
        Frame.__init__(self, *args, **kw)

        self._x = Defaults.Window._x
        self._y = Defaults.Window._y
        Defaults.shift_window()
    
    def destroy(self):
        self._dependant.destroy()
        try:
            application().remove(self)
        except ValueError:
            # Already removed
            pass
