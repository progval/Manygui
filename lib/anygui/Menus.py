from anygui.Exceptions import UnimplementedMethod
from anygui.Utils import flatten

# TODO: Use Container mixin?
#       Subclass Component?
#       Create MenuItem class...
#       Use contents instead of items?
#       Add items to defaults...

class Menu(Proxy, DefaultEventMixin, Default.Menu):
    
    def __init__(self, *args, **kwds):
        DefaultEventMixin.__init__(self)
        Proxy.__init__(self, *args, **kwds)

    def wrapperFactory(self):
        return backendModule().MenuWrapper(self)

    def add(self, items, options=None, **kwds):
        # Current version ignores options/kwds
        self.items.add(flatten(items))
        self.sync()

    def remove(self, item):
        if item in self.items:
            self.items.remove(item)
            self.sync()
