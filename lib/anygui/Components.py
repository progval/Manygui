from anygui.Proxies import Proxy
from anygui.Events import DefaultEventMixin
from anygui.Exceptions import UnimplementedMethod
from anygui.LayoutManagers import LayoutData


class Component(Proxy, DefaultEventMixin):
    """Component is an abstract base class representing a visual 
    component of the graphical user interface. A Component owns a rectangular
    region of screen space defined by its x, y, width and height properties.
    It may be contained within another Component.
    """
    
    def __init__(self, *args, **kw):
        self.layout_data = LayoutData() # ...
        DefaultEventMixin.__init__(self)
        Proxy.__init__(self, *args, **kw)

    # Is this used anymore? (mlh20020326)
    #def container_resized(self, cdw, cdh):
    #    """Called whenever the component's container changes size.
    #    Adjusts the component's size according to its moving and
    #    stretching options."""
    #    dx = 0
    #    dy = 0
    #    dw = 0
    #    dh = 0
    #    if self._hmove:
    #        dx = cdw
    #    elif self._hstretch:
    #        dw = cdw
    #    if self._vmove:
    #        dy = cdh
    #    elif self._vstretch:
    #        dh = cdh
    #    if dx != 0 or dy != 0 or dw != 0 or dh != 0:
    #        self.geometry = (self._x + dx, self._y + dy,
    #                         self._width + dw, self._height + dh)
