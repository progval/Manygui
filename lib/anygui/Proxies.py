from Attribs import Attrib

class Proxy(Attrib):

    # TBD: Add docstring for class

    def __init__(self, *args, **kwds):
        Attrib.__init__(self, *args, **kwds)
        self.rawSet(container=None)
        self.rawSet(wrapper=self.wrapperFactory()) # wrapper in state?
        self.push() # Hm... Move to wrapper.internalProd?

    def wrapperFactory(self):
        """
        Creates a backend Wrapper object from the current backend.

        Each Proxy subclass should implement this method to return an
        instance of the correct Wrapper subclass. For instance, in a
        Button class, this method would return an instance of the
        class anygui.backend.ButtonWrapper.
        """
        raise NotImplementedError, 'should be implemented by subclasses'

    def _partialState(self, *names, **kwds):
        """
        Create a copy of the Proxy's state dict with only the
        keys in *names.
        """
        state = {}
        try: blocked = kwds['blocked']
        except KeyError: blocked = []
        if not names: state.update(self.state)
        else:
            for name in names: state[name] = self.state[name]
        for name in blocked:
            try: del state[name]
            except KeyError: pass
        return state

    def pull(self, *names, **kws):
        """
        Pulls state from the Wrapper to its Proxy.

        The pull is performed by creating a state dictionary
        containing the names to be pulled and their current
        values. That dict is passed to the Wrapper's pull()
        method, which updates it appropriately. (The Wrapper
        may not add new keys to the state dict, however.)
        Upon return, the Proxy updates its own state dictionary
        with the result.
        """
        try:
            # Never pull if our widget is a dummy - we need
            # to keep all proxy state until a real widget
            # exists.
            assert self.wrapper.widget.isDummy()
            return
        except (AttributeError, AssertionError):
            pass
        state = self._partialState(*names)
        self.wrapper.pull(state)
        self.state.update(state)

    def push(self, *names, **kwds):
        """
        Pushes state from the Proxy to its Wrapper.

        The synchronisation is done by calling the Wrapper's update()
        with the current state dictionary as argument. If any
        attribute names are supplied, the Proxy may reduce the state
        dictionary to only those items whose keys are explicitly
        mentioned. (Whether this is done or not is not defined as part
        of the interface.) If no names are supplied, all state
        variables must be supplied. If names are supplied, these must
        at a minimum be supplied. Before Proxy/Wrapper
        synchronisation, the internalPush method is called.

        There is one exception to the above:

          - If the keyword argument 'blocked' is used, it must contain
            a sequence of names. These names will not be supplied to
            the backend either.
          
        """
        # We may need to modify names, so...
        names = list(names)
        self.internalPush(names) # @@@ May no longer be needed
        try:
            assert(self.wrapper)
        except (AttributeError,AssertionError):
            return
        self.wrapper.push(self._partialState(*names,**kwds))

    #def expandAliasedName(self,names,name):
    #    """
    #    Expands an aliased attribute into its aliases, and adds
    #    the aliases to names.
    #    """
    #    pass

    #def blockedNames(self):
    #    """
    #    Returns a sequence of names that should not be passed to the backend Wrapper.
    #
    #    Should be overridden by subclasses which need to block
    #    names. The default is an empty list.
    #    """
    #    return []

    def internalPush(self, names): # @@@ May no longer be needed!
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
