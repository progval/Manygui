from anygui.Exceptions import UnimplementedMethod
from anygui.Utils import flatten

# TODO: Use Container mixin
#       Use contents instead of items?

# Isn't a Component, but reimplements some Component methods;
# create common superclass?

class Menu(Attrib):

    _inhibit_refresh = 1         # See Component for explanation
    
    def __init__(self, *args, **kwds):
        Attrib.__init__(self, *args, **kwds)
        self._items = []

    def add(self, items, options=None, **kwds):
        # Current version ignores options/kwds
        self._items.add(flatten(items))
        self.refresh()

    def remove(self, item):
        if item in self._items:
            self._items.remove(item)
            self.refresh()
    
    # _set_items/_get_items needed?
    
    def _ensure_items(self):
        raise UnimplementedMethod, (self, "_ensure_items")

    def ensure_created(self):
        if self._ensure_created():
            self._finish_creation()

    def _finish_creation(self):
        self._ensure_events()
        self._inhibit_refresh = 0
        self.refresh()

    # destroy()?

    # visible/enabled?

    # backend api

    def _is_created(self):
        raise UnimplementedMethod, (self, "_is_created")

    def _ensure_created(self):
        raise UnimplementedMethod, (self, "_ensure_created")

    #def _ensure_enabled_state(self):
    #    raise UnimplementedMethod, (self, "_ensure_enabled_state")

    #def _ensure_destroyed(self):
    #    raise UnimplementedMethod, (self, "_ensure_destroyed")

    def _ensure_events(self):
        raise UnimplementedMethod, (self, "_ensure_events")
