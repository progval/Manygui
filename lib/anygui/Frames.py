from anygui.Components import AbstractComponent
from types import TupleType, InstanceType, IntType, ListType
from anygui.Exceptions import ArgumentError, UnimplementedMethod
from anygui.Utils import flatten
from anygui import Defaults
from anygui.LayoutManagers import Placer

class AbstractFrame(AbstractComponent, Defaults.Frame):

    def __init__(self, *args, **kw):
        self._contents = []
        AbstractComponent.__init__(self, *args, **kw)
        self._layout = None
        self.layout = Placer()

    def ensure_created(self):
        if self._ensure_created():
            for item in self._contents:
                item.ensure_created()
                # Redundant:
                #if item.ensure_created():
                #    item._finish_creation()
            self._finish_creation()
            return 1
        return 0

    def _get_contents(self):
        return self._contents
        
    def add(self,items,options=None,**kws):
        """ Add the given items to this container, passing the items and
        the keyword arguments along to the layout manager, if one is
        present. Note that different layout managers may have different
        expectations about **kwds, and may impose restrictions on the
        contents of items. See LayoutManagers.py. """

        items = flatten(items)

        # Now add to self._contents.
        for component in items:
            # _set_container() adds component to self._contents.
            # layout manager may have already called it, though.
            if component not in self._contents:
                component._set_container(self)

        # Inform the layout manager, if any.
        if self._layout:
            self._layout.add(items,options,**kws)

    def remove(self, component):
        "If the given component is among the contents of this Frame, removes it."
        if component in self._contents:
            component._set_container(None)
            self.layout.remove(component)
            self.layout.resized(0,0)

    def destroy(self):
        while self._contents:
            self._contents[0].destroy()
        AbstractComponent.destroy(self)

    def resized(self, dw, dh):
        try:
            self.layout.resized(dw,dh)
            for item in self._contents:
                try:
                    item.resized(dw,dh)
                except:
                    pass
        except:
            pass

    def _add(self, comp):
        self._contents.append(comp)
        if self._is_created():
            comp.ensure_created()
            # Redundant:
            #if comp.ensure_created():
            #    comp._finish_creation()

    def _remove(self, comp):
        try:
            self._contents.remove(comp)
            comp.destroy()
        except ValueError:
            pass

    def _set_layout(self,lo):
        if self._layout:
            self._layout._container = None
            ct = self._contents
            for item in ct:
                self._remove(item)
        self._layout = lo
        lo._container = self

    def _get_layout(self):
        return self._layout
