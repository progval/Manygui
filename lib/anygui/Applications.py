from Exceptions import UnimplementedMethod
from Attribs import Attrib
from Utils import flatten
import anygui

# FIXME: Update to work with Wrapper and. Proxy Should maintain a list
# of proxies, to be able to prod them when entering the main event
# loop.

class AbstractApplication(Attrib):

    _running = 0

    # Needed by Attrib:
    def refresh(self, **ignore): pass
    
    def __init__(self):
        Attrib.__init__(self)
        self._windows = []
        anygui._application = self

    def _get_contents(self):
        return tuple(self._windows)

    def add(self, win):
        for w in flatten(win):
            self._windows.append(w)
        #if self._running:
        #    win.wrapper.prod()
            

    def remove(self, win):
        try:
            self._windows.remove(win)
        except: pass
	# FIXME: Temporary(?) fix to cover problem in mswgui _wndproc
        # FIXME: Destroy the window?

    #def _add_window(self, win):
    #    self._windows.append(win)

    #def _remove_window(self, win):
    #    if win in self._windows:
    #        self._windows.remove(win)

    #def windows(self):
    #    """Return a list of all the currently existing window objects."""
    #    # XXX Or should ApplicationImp also derive from Attrib,
    #    # and implement a _get_windows method?
    #    return self._windows

    def run(self):
        """Run the application until all windows are destroyed."""
        self._running = 1
        if not self._windows:
            return
        self._mainloop()
        self._running = 0

    def _mainloop(self):
        raise UnimplementedMethod, (self, "mainloop")

    def isRunning(self):
        return self._running
