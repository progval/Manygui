"Mixins: mix-in classes for the anygui package"

from Exceptions import SetAttributeError, GetAttributeError, UnimplementedMethod
from Events import link, send
#import weakref
weakref = None

# _ensure_* methods that it might be dangerous to auto-call
_no_auto_ensures = '_ensure_created _ensure_destroyed'.split()

# get all names of methods starting with _ensure_ for a class & its bases,
# except those listed in _no_auto_ensures
def _get_all_ensures(klass, theset):
    for name in dir(klass):
        if name.startswith('_ensure_'):
            if name in _no_auto_ensures: continue
            value = getattr(klass,name)
            if callable(value): theset[name]=1
    for base in klass.__bases__: _get_all_ensures(base, theset)


class Attrib:
    """Attrib: mix-in class to support attribute getting & setting

    Each attribute name may have a setter method _set_name and/or a getter
    method _get_name.  If only the latter, it's a read-only attribute.  If
    no _set_name, attribute is set directly in self.__dict__.

    If the value being set exposes a method .assigned, it's called just
    after the attribute assignment; if the previously-set value exposes
    a method .removed, it's called just before the attribute assignment.
    This supports Models as values for widget attributes.

    Besides __setattr__ and __getattr__ special methods with this
    functionality, Attrib supplies a set method to set many attributes
    and options, and an __init__ with similar functionality.  __init__
    also handles attributes listed in self.explicit_attributes.

    Attrib also supplies a default update method, which calls all the
    relevant methods named _ensure_* if flag _inhibit_update is false.
    In this release, all _ensure_* are called; eventually, some kind
    of mechanism will use the hints to be more selective/optimizing.

    Note that Attrib embodies two patterns (attribute setting/getting
    and update functionality) and is thus "Alexandrian dense"; cfr
    Vlissides, "Pattern Hatching", page 30, for pluses and minuses of
    this "dense" approach and the resulting "profound" code.
    """

    _all_ensures = []
    _inhibit_update = 0         # default Attribs are always update-enabled

    def __setattr__(self, name, value):
        if name[0]!='_':
            try:
                setter = getattr(self, "_set_"+name)
            except AttributeError:
                if hasattr(self, "_get_"+name):
                    raise SetAttributeError(self, name)
            else:
                try: getattr(self.name).removed(self, name)
                except: pass
                setter(value)
                try: value.assigned(self, name)
                except: pass
                self.update(name=name)
                return
        self.__dict__[name] = value
        if name[0]!='_':
            self.update(name=name)

    def __getattr__(self, name):
        if name[0]=='_': raise GetAttributeError(self, name)
        try:
            getter = getattr(self, "_get_"+name)
        except AttributeError:
            raise GetAttributeError(self, name)
        else:
            return getter()

    def set(self, *args, **kwds):
        for opt in args:
            #kwds.update(opt.__dict__) # Doesn't work in Jython 2.1a1
            for key, val in opt.__dict__.items():
                kwds[key] = val
        for name, value in kwds.items():
            setattr(self, name, value)

    def __init__(self, *args, **kwds):
        enset = {}
        _get_all_ensures(self.__class__, enset)
        self.__dict__['_all_ensures'] = enset.keys()
        self._all_ensures.sort()

        # handle explicit-attributes
        try: explicit_attributes_names = self.explicit_attributes
        except AttributeError: pass
        else:
            for internal_name in explicit_attributes_names:
                external_name = internal_name[1:]
                if not kwds.has_key(external_name):
                    kwds[external_name] = getattr(self, internal_name)

        self.set(*args, **kwds)

    def update(self, **ignore_kw):
        if self._inhibit_update: return
        for ensure_name in self._all_ensures:
            getattr(self, ensure_name)()


class DefaultEventMixin:

    def __init__(self):
        if hasattr(self, '_default_event'):
            link(self, self._default_event, self._default_event_handler,
                 weak=1, loop=1)

    def _default_event_handler(self, **kw):
        kw = kw.copy()
        del kw['event']
        del kw['source']
        send(self, 'default', **kw)

