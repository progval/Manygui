from anygui.Components import AbstractComponent
from types import TupleType, InstanceType, IntType, ListType
from anygui.Exceptions import ArgumentError, UnimplementedMethod

class AbstractFrame(AbstractComponent):

    def __init__(self, *args, **kw):
        self._contents = []
        AbstractComponent.__init__(self, *args, **kw)

    def ensure_created(self):
        if self._ensure_created():
            for item in self._contents:
                if item._ensure_created():
                    item._finish_creation()
            self._finish_creation()
            return 1
        return 0

    def _get_contents(self):
        return self._contents
        
    def add(self, component):
        """Adds the given component to the contents of this Frame."""
        component._set_container(self)

    def remove(self, component):
        "If the given component is among the contents of this Frame, removes it."
        if component in self._contents:
            component._set_container(None)

    def destroy(self):
        while self._contents:
            self._contents[0].destroy()
        AbstractComponent.destroy(self)

    def place(self, items,
              left = None, right = None,
              top = None, bottom = None,
              hmove = 0, vmove = 0,
              hstretch = 0, vstretch = 0,
##              hscroll = 0, vscroll = 0,
              direction = 'right', space = 0,
              border = 0):
        """Add a list of components to the Frame with positioning,
        resizing  and scrolling options. See the manual for details.
        (Yes, I'm too lazy to write it all out here again.)"""

        def side(spec, name, self=self):
            if spec:
                t = type(spec)
                if t == TupleType:
                    return spec
                elif t == InstanceType:
                    return spec, 0
                elif t == IntType:
                    return None, spec
                else:
                    raise ArgumentError(self, 'place', name, spec)
            else:
                return None, None

        # Translate the direction argument
        try:
            dir = {'right':0, 'down':1, 'left':2, 'up':3}[direction]
        except KeyError:
            raise ArgumentError(self, 'place', 'direction', direction)
        # Unpack the side arguments
        left_obj, left_off = side(left, 'left')
        right_obj, right_off = side(right, 'right')
        top_obj, top_off = side(top, 'top')
        bottom_obj, bottom_off = side(bottom, 'bottom')
        # Process the items
        if type(items) != ListType:
            items = [items]
        for item in items:
            x = item.x
            y = item.y
            w = item.width
            h = item.height
            # Calculate left edge position
            if left_obj:
                l = left_obj.x + left_obj.width + left_off
            elif left_off:
                l = left_off
            else:
                l = None
            # Calculate top edge position
            if top_obj:
                t = top_obj.y + top_obj.height + top_off
            elif top_off:
                t = top_off
            else:
                t = None
            # Calculate right edge position
            if right_obj:
                r = right_obj.x - right_off
            elif right_off:
                r = self._width - right_off
            else:
                r = None
            # Calculate bottom edge position
            if bottom_obj:
                b = bottom_obj.y - bottom_off
            elif bottom_off:
                b = self._height - bottom_off
            else:
                b = None
            # Fill in unspecified positions
            if l == None:
                if r != None:
                    l = r - w
                else:
                    l = x
            if r == None:
                if l != None:
                    r = l + w
                else:
                    r = x + w
            if t == None:
                if b != None:
                    t = b - h
                else:
                    t = y
            if b == None:
                if t != None:
                    b = t + h
                else:
                    b = y + h
            # Create scroll bars if specified and allow for their sizes
            rs = r
            bs = b
##            if vscroll:
##                vsb = ScrollBar(container = self, client = item, height = b - t)
##                if hmove or hstretch:
##                    vsb._hmove = 1
##                vsb._vstretch = vstretch
##                rs = r - vsb.width - 1
##                vsb.set_position(rs + 1, t)
##            if hscroll:
##                hsb = ScrollBar(container = self, client = item, width = rs - l)
##                if vmove or vstretch:
##                    hsb._vmove = 1
##                hsb._hstretch = hstretch
##                bs = b - hsb.height - 1
##                hsb.set_position(l, bs + 1)
            # Position and size the item
            item.geometry = l, t, rs - l, bs - t
            self.add(item)
            # Record resizing and border options
            item._hmove = hmove
            item._vmove = vmove
            item._hstretch = hstretch
            item._vstretch = vstretch
            item._border = border
            # Step to the next item
            if dir == 0:
                left_obj = item
                left_off = space
            elif dir == 1:
                top_obj = item
                top_off = space
            elif dir == 2:
                right_obj = item
                right_off = space
            else:
                bottom_obj = item
                bottom_off = space

    def resized(self, dw, dh):
        for c in self._contents:
            c.container_resized(dw, dh)

    def _add(self, comp):
        self._contents.append(comp)
        if self._is_created():
            comp._ensure_created()

    def _remove(self, comp):
        self._contents.remove(comp)
        comp.destroy()
