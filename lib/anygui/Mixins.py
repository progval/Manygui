"Mixins: mix-in classes for the anygui package"

from Exceptions import SetAttributeError, GetAttributeError

try:
    import weakref
except ImportError:
    # Evil hack to make Jython work. This is not a very
    # good solution, but code should run at least.
    class ref:
        def __init__(self,obj):
            self.obj = obj
        def __call__(self):
            return self.obj
    class weakref:
        ref = ref

class Attrib:
    """Attrib: mix-in class to support attribute getting & setting

    Each attribute name may have a setter method _set_name and/or a getter
    method _get_name.  If only the latter, it's a read-only attribute.  If
    no _set_name, attribute is set directly in self.__dict__.
    """
    def __setattr__(self, name, value):
        if name[0]!='_':
            try:
                setter = getattr(self, "_set_"+name)
            except AttributeError:
                if hasattr(self, "_get_"+name):
                    raise SetAttributeError(self, name)
            else:
                setter(value)
                return
        self.__dict__[name] = value

    def __getattr__(self, name):
        if name[0]=='_': raise GetAttributeError(self, name)
        try:
            getter = getattr(self, "_get_"+name)
        except AttributeError:
            raise GetAttributeError(self, name)
        else:
            return getter()

    def set(self, **kwds):
        for name, value in kwds.items():
            setattr(self, name, value)

    def __init__(self, **kwds):
        self.set(**kwds)

class Action:
    """Action: mix-in class recording a user-specified action procedure

    Action may be any callable, or a sequence of one item (callable),
    two (callable & args) or three (callable, args, keywords).  Action
    may be None or empty sequence to reset a previously recorded action.
    _get_action always returns a 3-item tuple.

    The do_action method calls the action (if any) with the args
    (positional and keyword) as specified.
    """

    _action = None
    _action_args = ()
    _action_kwds = {}

    def _set_action(self, action, args=None, kwds=None):
        if action is not None and not callable(action):
            # ensure action is sequence of 0 to 3 items
            try: nitems = len(action)
            except TypeError:
                raise TypeError, "action must be callable or sequence"
            if nitems>3: raise TypeError, "action must have at most 3 items"
            action, args, kwds = (tuple(action)+3*(None,))[:3]
        if callable(action) or action is None:
            self.__dict__['_action']=action
            # contextually ensure that args is sequence or None, that
            # kwds is mapping or None, and that copies are made if needed
            use_args = tuple(args or ())
            use_kwds = {}; use_kwds.update(kwds or {})
            self.__dict__['_action_args']=use_args
            self.__dict__['_action_kwds']=use_kwds
        else: raise TypeError, "action must be callable or sequence"

    def _get_action(self):
        return self._action, self._action_args, self._action_kwds

    def do_action(self):
        if self._action:
            return self._action(*self._action_args, **self._action_kwds)

class Observable:
    """
    Implements the "observed" role in the Observer design pattern.

    Views call add_view(<view_object>,<callback_name>) to add themselves
    to the observer list for the model. Models may call self.raw_notify_views()
    with arbitrary arguments to notify all existing views via their
    callback method, or via their "model_changed" method if no callback name
    is supplied in the add_view() call. All arguments passed to
    raw_notify_views() are passed on intact to the views' callback.
    In addition, a "target=modelself" keyword argument is passed.

    Models may also record "hints" using the add_hint() method. A hint
    is a (method_name,*args,**kwargs) tuple describing a method call
    on the model object since the last time the model notified its
    views of a state change. A model that uses the hint facility may call
    self.notify_views() to deliver all accumulated hint
    data to all views, again using the views' named callback method
    or "model_changed()" by default; the accumulated hints are then discarded.
    """

    def __init__(self):
        self.views = []
        self.hints = []

    def add_view(self,view,callback=None):
        """
        Add <view> to the list of views to be notified when the model changes.
        If <callback> is supplied, it must be a string naming a method of the
        view object to call. Otherwise view.notify() will be called with the
        model and any additional arguments the model chooses to pass. DO NOT
        pass a code object in <callback>.
        """
        self.views.append((weakref.ref(view),callback))

    def remove_view(self,view):
        """
        Remove <view> from the list of views to be notified. Since we keep
        weak references to views here, it should rarely if ever be
        necessary to call this explicitly.
        """
        def notview(v,view=view): return (v[0]() is not view)
        self.views = filter(notview,self.views)

    def raw_notify_views(self,*args,**kw):
        """
        Notify all registered, non-GC'd views of a model change. Any arguments
        and keywords passed to notify_views are passed along intact to the
        views' callback methods.
        """

        # Get rid of views that've been GC'd.
        self.remove_view(None)

        # Notify everything that's left... carefully.
        for vv in self.views:
            view = vv[0]()
            if view is not None:
                if vv[1] is not None:
                    # Call the custom callback. We have to use a name for this; if
                    # we try using a bound method we end up back in circular-reference
                    # land.
                    meth = getattr(view,vv[1])
                    meth(target=self,*args,**kw)
                else:
                    # No custom callback, so just try to notify().
                    view.model_changed(self,*args,**kw)
        
        self._last_updater = None

    def add_hint(self,meth,*args,**kw):
        """
        Record a hint for later delivery to views. A hint is a model method name,
        a list of positional arguments, and a dictionary of keyword arguments.
        Or any other data the model would like to send :-)
        """
        self.hints.append((meth,args,kw))

    def notify_views(self):
        """
        Notify all registered, non-GC'd views of a model change using
        the recorded hint list, then discard the hints.
        """
        self.raw_notify_views(change=self.hints)
        self.hints = []
