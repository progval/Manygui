from Exceptions import SetAttributeError, GetAttributeError
from Events import link, send

class Attrib:
    # REWRITE THIS:
    TO_BE_REWRITTEN = """Attrib: mix-in class to support attribute getting & setting.


    Each attribute name may have a setter method _set_name and/or a getter
    method _get_name.  If only the latter, it's a read-only attribute.  If
    no _set_name, attribute is set directly in self.__dict__.  This only
    applies to attribute-names that do NOT start with '_'.

    If the value being set exposes a method .assigned, it's called just
    after the attribute assignment; if the previously-set value exposes
    a method .removed, it's called just before the attribute assignment.
    This supports Models as values for widget attributes.

    Besides __setattr__ and __getattr__ special methods with this
    functionality, Attrib supplies a set method to set many attributes
    and options, and an __init__ with similar functionality.  __init__
    also handles attributes listed in self.explicit_attributes.

    Another, similar feature of class Attrib: it supplies a modattr method
    that tries to change an attribute's value in-place, if feasible, rather
    than re-bind it.  Changing in-place means trying _modify_name (rather
    than _set_name), assigning to self.name[:], and assigning to
    self.name.value.  In the end, self.name is re-bound if in-place
    modification fails.  If the value being changed exposes a method
    .modified, it's called just after an in-place modification succeeds.

    Method modify has the same interface as set (to modify potentially
    more than one attribute at once) but uses modattr rather than setattr.

    Attrib also supplies a default sync method, which calls all the
    relevant methods named set* in the connected _dependant object if
    flag _inhibit_sync is false.  In this release, all set* are
    called; eventually, some kind of mechanism will use the hints to
    be more selective/optimizing.  Attrib's responsibilities include
    enforcing a calling order among set* methods.


    Note that Attrib embodies two patterns (attribute setting/getting
    and sync functionality) and is thus "Alexandrian dense"; cfr
    Vlissides, "Pattern Hatching", page 30, for pluses and minuses of
    such "dense" approaches and the resulting "profound" code.
    """

    # FIXME: Needed?
    _inhibit_sync = 0        # default Attribs are always sync-enabled

    # FIXME: Fix set() and modify() so they don't call sync repeatedly
    # for multiple arguments.

    def __init__(self, *args, **kwds):
        defaults = getattr(self, 'state', {})
        self.state = defaults.copy()
        self.rawSet(*args, **kwds)
        self.sync()

    def __setattr__(self, name, value):
        if name[0]!='_':
            try:
                setter = getattr(self, "_set_"+name)
            except AttributeError:
                if hasattr(self, "_get_"+name):
                    raise SetAttributeError(self, name)
            else:
                try: getattr(self, name).removed(self, name)
                except: pass
                inhibit_sync = setter(value)
                try: value.assigned(self, name)
                except: pass
                if not inhibit_sync: self.sync(name)
                return
        self.__dict__[name] = value
        if name[0]!='_':
            self.sync(name)

    def __getattr__(self, name):
        if name[0]=='_': raise GetAttributeError(self, name)
        try:
            getter = getattr(self, "_get_"+name)
        except AttributeError:
            raise GetAttributeError(self, name)
        else:
            return getter()

    def _set_or_mod(self, func, *args, **kwds):
        for opt in args:
            # kwds.update(opt.__dict__) # Doesn't work in Jython 2.1a1
            for key, val in opt.__dict__.items():
                kwds[key] = val
        for name, value in kwds.items():
            func(self, name, value)

    def set(self, *args, **kwds):
        return self._set_or_mod(setattr, *args, **kwds)

    def rawSet(self, *args, **kwds):
        raise NotImplementedError # FIXME

    def modify(self, *args, **kwds):
        return self._set_or_mod(self.__class__.modattr, *args, **kwds)

    def rawModify(self, *args, **kwds):
        raise NotImplementedError # FIXME

    def modattr(self, name, value):
        if name[0]!='_':
            try: modifier = getattr(self, '_modify_'+name)
            except AttributeError: pass
            else:
                # found a modifier-method, delegate the task to it
                inhibit_update = modifier(value)
                try: getattr(self, name).modified()
                except: pass
                if not inhibit_update: self.sync(name)
                return

        # we need to perform the modification-task directly
        old_value = getattr(self, name, None)
        # try assigning to the "all-object slice"
        try: old_value[:] = value
        except:
            # try assigning to the "value" attribute of the old-value
            try: old_value.value = value
            except:
                # no in-place mod, so, just set it (bind or re-bind)
                setattr(self, name, value)
                return
        # in-place modification has succeeded, alert the old_value (if
        # it supplies a suitable method) and any watchers of 'self'
        try: old_value.modified()
        except: pass
        if name[0]!='_':
            self.sync(name)
