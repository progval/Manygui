from anygui import application
from anygui.Utils import topologicalSort, getSetter

"""
The back-end wrapper presents a unified and simple interface for
manipulating the native widget. It also installs event handlers so
that it can send the proper Anygui events (through the send function)
as a reaction to native events, and so that it can update the proxy
state (through the rawModify method) whenever the native widget is
modified by the user. The wrapper is responsible for creating and
destroying the native widget as needed. It should also destroy the
widget when explicitly told to do so through the destroy method.

The only methods that should be explicitly called by the Proxy are:

  update(state)
  getPrefs()
  prod()
  enableEvent(event)
  disableEvent(event)
  destroy()

"""

# TODO:
# - In __init__:
#   Add to list of wrappers that need to be prodded...
#   (In Application, e.g. addWrapper?)
#   Should the Wrapper realy prod itself?

class AbstractWrapper:

    """
    An abstract superclass for the backend Wrapper classes which,
    again, are generic superclasses for the more specific backend
    wrappers (such as ButtonWrapper etc.).
    """

    def __init__(self, proxy):
        """
        Store the proxy and perform general initialisation.

        If the main loop has been entered already, the Wrapper will
        prod itself. Otherwise, the Proxy should call prod() at some
        later point, when the event loop has been entered.

        The constructor sets up the self.aggregates dictionary with
        aggregate setters, by calling the setAggregate
        method. Subclasses wanting to add (or override) aggregates
        should use the same method.
        """
        self.proxy = proxy
        # Move DummyWidget code to front-end?

        #@@@ Hm. Some of this could be done globally/class-wide...
        
        self.aggregates = {}
        self.setAggregate('position', ('x', 'y'))
        self.setAggregate('size', ('width', 'height'))
        self.setAggregate('geometry', ('x', 'y', 'width', 'height'))

        self.constraints = []
        self.addConstraint('text', 'selection')
        # 'container' before everything... Handler through added sync call?

        self.inMainLoop = 0
        self.prod() #@@@ ?

    def setAggregate(self, name, signature):
        """
        Sets the signature of an aggregate setter function.

        The resulting mapping is used by getSetters() during setter
        dispatch in update().        
        """
        self.aggregates[signature] = name

    def addConstraint(self, before, after):
        """
        Adds a setter ordering constraint.

        This ensures that the before-name is set before the
        after-name, if possible.
        """
        # FIXME: Should handle aggregates automatically...
        # E.g. ('geometry', 'visible') should imply ('x', 'visible') and
        # ('x', 'visible') should imply ('geometry', 'visible') etc.
        constraint = before, after
        if not constraint in self.constraints:
            self.constraints.append((before, after))

    def getSetters(self, attrs):
        """
        Returns a pair (setters, unhandled) where setters is a
        sequence of the form [(setter, attrs), ...] and unhandled is a
        sequence of unhandled attributes.

        Each pair (setter, attrs) consists of a setter method and the
        names of the attributes it uses. When finding the set of
        setters, more specific aggregate setters (that can set more
        than one attribute) are preferred over less specific ones. For
        instance, if both 'x' and 'y' are found in the attrs argument,
        and there is an aggregate setter such as setPosition that
        handles both, it will be preferred over setX and setY
        individually. The dictionary self.aggregates is used to find
        such aggregate setters.
        """
        result = []
        names = []
        candidates = self.aggregates.items()
        attrs = attrs[:]
        def moreSpecific(aggr1, aggr2):
            return cmp(len(aggr1[0]), len(aggr2[0]))
        # Get the aggregates:
        candidates.sort(moreSpecific)
        candidates.reverse()
        for candidate in candidates:
            for attr in candidate[0]:
                if not attr in attrs: break
            else:
                setter = getSetter(self, candidate[1])
                if setter is not None:
                    for attr in candidate[0]: attrs.remove(attr)
                    result.append((setter, candidate[0]))
                    names.append(candidate[1])
        # Get the plain setters:
        unhandled = []
        for attr in attrs:
            setter = getSetter(self, attr)
            if setter is not None:
                result.append((setter, (attr,)))
                names.append(attr)
            else:
                unhandled.append(attr)

        # Make sure the order is legal:
        topologicalSort(names, result, self.constraints)
        return result, unhandled
    
    def update(self, state):
        """
        Updates native widget based on given name/value pairs.
        
        This method is called by the front-end proxy when
        necessary. The Wrapper itself may request such an update by
        calling the Proxy's sync() method, optionally supplying the
        names of the attributes whose values need updating. The
        Wrapper is free to ignore any or all of the state variables
        supplied. If no native widget has been created, this method
        will have no effect.

        # [Rewrite this:]
        The default implementation automatically looks for setter
        methods in the Wrapper object (with the function
        anygui.Utils.getSetters). This will find the most specific set
        of setters, either setting attributes individually such as
        setWidth and setHeight (not very specific) or setting more
        attributes simultaneously like setHeightAndWidth (more
        specific). The attribute names in the setters can be in any
        order, but cannot contain the word 'And', since that's used as
        a separator.

        Any attributes that aren't covered by an appropriate setter
        method are ignored.
        """
        # Use self.dependencies -- document it
        setters, unhandled = self.getSetters(state.keys())
        for setter, params in setters:
            kwds = {}
            for key in params:
                kwds[key] = state[key]
            setter(**kwds)

    def getPrefs(self):
        """
        Return a dictionary with preferences.
        
        If the Wrapper has any preferences (e.g. optimal size, minimal
        size) it may return those in this dictionary. There is no
        guarantee that these preferences will be used. By default a
        Wrapper has no preferences.        
        """
        return {}

    def prod(self):
        """
        Check environment for changes.
        
        The front-end Proxy should call this every time something has
        changed in the environment that it believes the Wrapper may be
        interested in. One such condition is that the main even loop
        has been entered, since many backend Wrappers will then be
        able to instantiate their native widgets.
        """
        if application().isRunning() and not self.inMainLoop:
            self.inMainLoop = 1
            self.enterMainLoop()
        self.internalProd()

    def enterMainLoop(self):
        """
        Make the adjustments needed when entering the main event loop.

        This method should be implemented by subclasses in order to
        create the native widget etc. It will be called the first time
        prod() is called after entering the main event loop.
        """
        raise NotImplementedError, 'should be implemented by subclasses'
        
    def internalProd(self):
        """
        Internal template method used in prod().

        Should be implemented in subclasses that rely on the default
        implementation of prod() but require some extra
        processing. The default implementation of internalProd is to
        do nothing.
        """
        pass

    def enableEvent(self, event):
        """
        Called when the Proxy is the source in a call to link().

        All event sources may optionally implement this method, and
        are not required to produce the event in question until
        enableEvent is called, since there will be no event handlers
        around to handle them anyway.

        After this method has been called once, the Wrapper must
        generate the event. If the native widget is destroyed and
        recreated, the Wrapper is responsible for removing old native
        event handlers and registering new ones.

        This method is mainly an optimization; it is perfectly
        acceptable for a Wrapper to generate all its events before
        enableEvent is called. The default implementation does
        nothing.
        """
        # TODO: Add default implementation with some registry of
        # activated events?

    def disableEvent(self, event):
        """
        Called when the Wrapper need no longer worry about an event.

        This method may be called by the Proxy object which will, in
        turn, be told to do so by the event system, in the event that
        no event handlers exist that rely on the given event with the
        Proxy as the source. The Wrapper is the free to stop
        generating the given event until enableEvent is called again
        (if ever).

        Note that the Wrapper is free to ignore this method. Note also
        that this method is not currently used by the event system,
        but may be used in a future version.        
        """

    def destroy(self):
        """
        Dispose of the native widget.

        In general, the Wrapper handles creation and destruction of
        native widgets in a manner completely transparent to the
        frontend Proxy. This method should not be used to handle
        adding/removing to/from parent containers etc., since the
        Wrapper will take care of widget destruction in those cases,
        if necessary. This method should only be used in the cases
        where the native widget must be destroyed e.g. to save
        resources. This method is used by the Proxy's destroy()
        method.
        """
        raise NotImplementedError, 'should be implemented by subclasses'


    def widgetFactory(self, *args, **kwds):
        """
        Used internally to create a new native Widget.

        This is an abstract method that should be overridden in each
        Wrapper subclass.
        """
        raise NotImplementedError
