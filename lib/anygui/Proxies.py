from Attribs import Attrib

# NOTE: Make sure that inheriting defaults still works with the new
# Attrib mechanism (e.g. "inherit" by updating the state dictionary
# with a default one).

class Proxy(Attrib):

    # TBD: Add docstring for class

    def __init__(self, *args, **kwds):
        Attrib.__init__(self, *args, **kwds)
        self.wrapper = self.wrapperFactory()

    def wrapperFactory(self):
        """
        Creates a backend Wrapper object from the current backend.

        Each Proxy subclass should implement this method to return an
        instance of the correct Wrapper subclass. For instance, in a
        Button class, this method would return an instance of the
        class anygui.backend.ButtonWrapper.
        """
        raise NotImplementedError, 'should be implemented by subclasses'

    def sync(self, *names):
        """
        Synchronises the Proxy and its Wrapper.

        The synchronisation is done by calling the Wrapper's
        update() with the current state dictionary as argument. If
        any attribute names are supplied, the Proxy may reduce the
        state dictionary to only those items whose keys are
        explicitly mentioned. (Whether this is done or not is not
        defined as part of the interface.) If no names are
        supplied, all state variables must be supplied. If names
        are supplied, these must at a minimum be supplied.
        """
        state = {}
        if not names: state.update(self.state)
        else:
            for name in names: state[name] = self.state[name]
        self.wrapper.update(state)
        

    def destroy(self):
        """
        Calls the destroy() method of the backend Wrapper.

        This is used by the application programmer in the occasions
        where a native widget must be explicitly destroyed.
        """
        self.wrapper.destroy()
