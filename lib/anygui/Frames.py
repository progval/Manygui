import sys
from anygui.Components import Component
from types import TupleType, InstanceType, IntType, ListType
from anygui.Exceptions import ArgumentError, UnimplementedMethod
from anygui.Utils import flatten
from anygui import Defaults
from anygui.LayoutManagers import Placer
from anygui import backendModule

class Frame(Component, Defaults.Frame):

    def __init__(self, *args, **kw):
        self.contents = []
        Component.__init__(self, *args, **kw)
        self.layout = Placer()

    def wrapperFactory(self):
        return backendModule().FrameWrapper(self)
        
    def add(self,items,options=None,**kws):
        """
        Add the given items to this container, passing the items and
        the keyword arguments along to the layout manager, if one is
        present. Note that different layout managers may have
        different expectations about **kwds, and may impose
        restrictions on the contents of items. See LayoutManagers.py.
        """
        items = flatten(items)

        # Now add to self.contents.
        for component in items:
            if component not in self.contents: # @@@ Hm. Shouldn't this be changed to _contents?
                component.container = self
                self.contents.append(component)

        # Inform the layout manager, if any.
        if self.layout:
            self.layout.add(items,options,**kws)
            self.resized(0,0)

    def remove(self, component):
        "If the given component is among the contents of this Frame, removes it."
        if component in self.contents:
            self.contents.remove(component)
            component.container = None
            self.layout.remove(component)
            self.resized(0,0)

    def destroy(self):
        while self.contents:
            self.contents[0].destroy()
        Component.destroy(self)

    def resized(self, dw, dh):
        """ Ensure all contents are layed out properly. """
        oldSizes = {}
        for item in self.contents:
            try:
                oldSizes[item] = item.width,item.height
            except:
                pass
        try:
            self.layout.resized(dw,dh)
            for item in self.contents:
                ow,oh = oldSizes[item]
                idw = item.width-ow
                idh = item.height-oh
                try:
                    item.resized(idw,idh)
                except:
                    pass
        except:
            print "Layout error, please contact Anygui team:",sys.exc_info()
            pass

    def setLayout(self,lo):
        """ Special handling for setting the layout manager. """
        if 'layout' in self.state.keys():
            self.layout.container = None
            ct = self.contents
            for item in ct:
                self.remove(item)
        self.state['layout'] = lo
        lo.container = self

class GroupBox(Frame):
    """A widget for grouping components.  Draws a labeled box around
    the components it contains.  The label is obtained from the text
    attribute.  Otherwise behaves like a normal frame.  Behaves like
    a normal frame for back-ends that do not support group boxes
    natively."""
    def wrapperFactory(self):
        try:
            return backendModule().GroupBoxWrapper(self)
        except AttributeError:
            return Frame.wrapperFactory(self)
