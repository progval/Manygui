# TBD: Add Proxy class to interact with AbstractWrapper class. (No
# need to call it AbstractProxy since, unlike Wrapper, there will only
# be one "main superclass".)

class Proxy:

    # Subclass Attrib... Modify Attrib to use state dictionary etc.
    # Move rawModify and modify to Attrib...

    # Stores state variables in a dictionary named state. When the
    # state is modified in a manner detectable by the Proxy
    # (i.e. through __setattr__, set(), or modify()) the sync()
    # method is called to synchronise with the backend wrapper.

    def rawModify(self, **kwds):
        """
        Performs modification without calling sync().
        
        This method is used by the backend Wrapper to perform
        modifications based on user actions. The modifications are
        done in-place if possible (as described in the
        documentation), only rebinding an attribute if the
        modification fails.
        """           

    def modify(self, **kwds):
        """
        Similar to rawModify, but also calls sync() with the
        appropriate attribute names.
        """

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

    def destroy(self):
        """
        Calls the destroy() method of the backend Wrapper.

        This is used by the application programmer in the occasions
        where a native widget must be explicitly destroyed.
        """

    
