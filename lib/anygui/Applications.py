#from Mixins import Action
from Exceptions import UnimplementedMethod
from Mixins import Attrib
import anygui

class AbstractApplication(Attrib):#(Action): # FIXME: Is Action needed here?
    
    def __init__(self):
        self._windows = []
        anygui._application = self

    # FIXME: Move functionality from _add_window and _remove_window to
    # add/remove, and from windows() to _get_contents when the rest of
    # the code has been modified to use these.        [mlh 2001-12-10]

    def _get_contents(self):
        return self.windows()

    def add(self, win):
        self._add_window(win)

    def remove(self, win):
        self._remove_window(self, win)

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
