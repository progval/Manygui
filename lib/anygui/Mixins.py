"Mixins: mix-in classes for the anyguy package"

from Exceptions import SetAttributeError, GetAttributeError

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
