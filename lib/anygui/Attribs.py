from Events import link, send

# FIXME: Add mechanism for internal attributes (not in state[]). Use
# _foo naming convention? :I

class Attrib:
    # TODO: Add new docstring (see below for old one)

    def __init__(self, *args, **kwds):
        defaults = getattr(self, 'state', {})
        self.state = defaults.copy()
        self.rawSet(*args, **kwds)
        self.sync()

    def sync(self, *names): pass

    def __setattr__(self, name, value):
        if name == 'state':
            self.__dict__[name] = value
        else: self.set(**{name: value})

    def __getattr__(self, name):
        if name == 'state' or not self.state.has_key(name):
            raise AttributeError
        return self.state[name]

    def set(self, *args, **kwds):
        names = self.rawSet(*args, **kwds)
        self.sync(*names)

    def rawSet(self, *args, **kwds):
        names = []
        for key, val in optsAndKwdsItems(args, kwds):
            old_val = getattr(self, key, None)
            try: old_val.removed(self, key)
            except: pass
            self.state[key] = val
            try: val.assigned(self, key)
            except: pass
            names.append(key)
        return names

    def modify(self, *args, **kwds):
        names = self.rawModify(*args, **kwds)
        self.sync(*names)

    def rawModify(self, *args, **kwds):
        names = []
        for key, val in optsAndKwdsItems(args, kwds):
            modattr(self, key, val)
            names.append(key)
        return names


def optsAndKwdsItems(args, kwds):
    items = kwds.items()
    for opt in args:
        items.extend(opt.__dict__.items())
    return items


def modattr(obj, name, value):
    old_value = getattr(obj, name, None)
    # try assigning to the "all-object slice"
    try: old_value[:] = value
    except:
        # try assigning to the "value" attribute of the old-value
        try: old_value.value = value
        except:
            # no in-place mod, so, just set it (bind or re-bind)
            # Use rawSet() if available:
            setter = getattr(obj, 'rawSet', None)
            if callable(setter):
                setter(**{name: value})
            else: setattr(obj, name, value)
            return
    # in-place modification has succeeded, alert the old_value (if
    # it supplies a suitable method)
    try: old_value.sync()
    except: pass




OLD_DOCSTRING = """Attrib: mix-in class to support attribute getting & setting.


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
