from Attribs import Attrib

class Proxy(Attrib):

    # TBD: Add docstring for class

    def __init__(self, *args, **kwds):
        Attrib.__init__(self, *args, **kwds)
        self.rawSet(wrapper=self.wrapperFactory()) # wrapper in state?
        self.sync() # Hm... Move to wrapper.internalProd?

    def wrapperFactory(self):
        """
        Creates a backend Wrapper object from the current backend.

        Each Proxy subclass should implement this method to return an
        instance of the correct Wrapper subclass. For instance, in a
        Button class, this method would return an instance of the
        class anygui.backend.ButtonWrapper.
        """
        raise NotImplementedError, 'should be implemented by subclasses'

    def sync(self, *names, **kwds):
        """
        Synchronises the Proxy and its Wrapper.

        The synchronisation is done by calling the Wrapper's update()
        with the current state dictionary as argument. If any
        attribute names are supplied, the Proxy may reduce the state
        dictionary to only those items whose keys are explicitly
        mentioned. (Whether this is done or not is not defined as part
        of the interface.) If no names are supplied, all state
        variables must be supplied. If names are supplied, these must
        at a minimum be supplied. Before Proxy/Wrapper
        synchronisation, the internalSync method is called.

        There are two exceptions to the above:

          - Names in the sequence returned by self.blockedNames()
            should never be supplied to the backend.

          - If the keyword argument 'blocked' is used, it must contain
            a sequence of names. These names will not be supplied to
            the backend either.
          
        """
        self.internalSync(names)

        # FIXME: Acceptable?
        try: self.wrapper
        except AttributeError: return

        state = {}
        try: blocked = kwds['blocked']
        except KeyError: blocked = []
        blocked.extend(self.blockedNames())
        if not names: state.update(self.state)
        else:
            for name in names: state[name] = self.state[name]
        for name in blocked:
            try: del state[name]
            except KeyError: pass
        self.wrapper.update(state)

    def blockedNames(self):
        """
        Returns a sequence of names that should not be passed to the backend Wrapper.

        Should be overridden by subclasses which need to block
        names. The default is an empty list.
        """
        return []

    def internalSync(self, names):
        """
        Used for internal synchronisation in the Proxy.

        This method is especially important for dealing with aliased
        attributes (e.g. position being an alias for (x, y)). It
        should be implemented by subclasses, if needed.
        """

    def enableEvent(self, event):
        """
        Called when the Proxy is the source in a call to link().

        All event sources may optionally implement this method, and
        are not required to produce the event in question until
        enableEvent is called, since there will be no event handlers
        around to handle them anyway. The Proxy implementation simply
        calls the corresponding method in the backend Wrapper.
        """
        # FIXME: try/except not really acceptable... (Create backlog?
        # Rearrange __init__ stuff to avoid loop?
        try: self.wrapper.enableEvent(event)
        except AttributeError: pass

    def destroy(self):
        """
        Calls the destroy() method of the backend Wrapper.

        This is used by the application programmer in the occasions
        where a native widget must be explicitly destroyed.
        """
        self.wrapper.destroy()
