"Mixins: mix-in classes for the anygui package"

from Exceptions import SetAttributeError, GetAttributeError
from Events import link, send
#import weakref
weakref = None

class Attrib:
    """Attrib: mix-in class to support attribute getting & setting

    Each attribute name may have a setter method _set_name and/or a getter
    method _get_name.  If only the latter, it's a read-only attribute.  If
    no _set_name, attribute is set directly in self.__dict__.

    If the value being set exposes a method .assigned, it's called just
    after the attribute assignment; if the previously-set value exposes
    a method .removed, it's called just before the attribute assignment.
    This supports Models as values for widget attributes.
    """
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
        self.set(*args, **kwds)

    def update(self, **kw):
        "this should ALWAYS be overridden by widgets -- here just for debug"
        print "update(%r,%r)"%(self, kw)


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

