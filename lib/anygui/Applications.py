#from Mixins import Action
from Exceptions import UnimplementedMethod
import anygui

class AbstractApplication:#(Action): # FIXME: Is Action needed here?
    
    def __init__(self):
        self._windows = []
        anygui._application = self

    def _add_window(self, win):
        self._windows.append(win)

    def _remove_window(self, win):
        if win in self._windows:
            self._windows.remove(win)

    def windows(self):
        """Return a list of all the currently existing window objects."""
        # XXX Or should ApplicationImp also derive from Attrib,
        # and implement a _get_windows method?
        return self._windows

    def run(self):
        """Run the application until all windows are destroyed."""
        if not self._windows:
            return
        for win in self._windows:
            win.ensure_created()
        self._mainloop()

    def _mainloop(self):
        raise UnimplementedMethod, (self, "mainloop")
