from Exceptions import UnimplementedMethod
from Attribs import Attrib
from Utils import flatten
from anygui.Utils import log
import anygui

class AbstractApplication(Attrib):

    _running = 0
    _name = "Anygui App"
    _version = "0"
    
    def __init__(self, **kwds):
        Attrib.__init__(self)
        self.parseKwds(**kwds)
        self._windows = []
        self._wrappers = []
        anygui._application = self

    def parseKwds(self, **kwds):
        keys = kwds.keys()
        if 'name' in keys:
            self._name = kwds['name']
        if 'version' in keys:
            self._version = kwds['version']

    def getName(self):
        return self._name

    def setName(self, name):
        self._name = name

    def getVersion(self):
        return self._version

    def setVersion(self, version):
        self._version = version

    def add(self, win):
        for w in flatten(win):
            self._windows.append(w)
            w.container = self            
            w.wrapper.prod()

    def remove(self, win):
        try:
            self._windows.remove(win)
            self.internalRemove()
        except: pass
	# FIXME: Temporary(?) fix to cover problem in mswgui _wndproc
        # FIXME: Destroy the window?

    def internalRemove(self):
        pass

    # FIXME: Allow external access to list of windows?

    def run(self):
        """
        Run the application until all windows are removed.
        """
        self._running = 1
        if not self._windows:
            return
        for wrapper in self._wrappers[:]: # FIXME: Paranoid?
            wrapper.prod()
        self.internalRun()
        self._running = 0

    def internalRun(self):
        raise UnimplementedMethod, (self, "mainloop")

    def isRunning(self):
        return self._running

    def manage(self, wrapper):
        """
        Tells the Application to manage a Wrapper.

        This means that when the Application is run, the Wrapper will
        be prodded.
        """
        if not wrapper in self._wrappers:
            self._wrappers.append(wrapper)

    # FIXME: Is this method really necessary?
    def ignore(self, wrapper):
        """
        Tells the Application to stop managing a Wrapper.
        """
        try:
            self._wrappers.remove(wrapper)
        except ValueError: pass

    def quit(self):
        raise UnimplementedMethod, (self, "quit")
