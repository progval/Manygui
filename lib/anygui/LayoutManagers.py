from anygui import Defaults
from anygui.Utils import *
from anygui.Exceptions import UnimplementedMethod, Error
from types import *

class LayoutData:
    """ Each component may have an associated LayoutData object,
    maintained by the LayoutManager. You call self.getLayoutData(w)
    within a LayoutManager in order to get the LayoutData for
    widget w. A LayoutManager can stash any kind of data in
    here that it needs in order to lay the widget out properly. """
    pass

class LayoutManager:

    """ Base class for layout managers. Subclasses should implement at
    least the resized() method, which is called when self.container
    changes size. The resized() method should simply assign
    appropriate geometry values to the self.container.contents. The
    dw and dh arguments to resized() are not well-defined at this
    point, so don't rely on them. Do *not* call any sync() methods
    from the resized() method; the container will deal with that.

    You may also implement, if desired:

    add_components(items,options=None,**kws):
        to be informed when items are added to self.container.
        <items> may be either a single component or a
        list; options is an Option object that the LayoutManager may
        interpret however it pleases; **kws are keyword arguments the
        LayoutManager may interpret as it pleases.

    remove_component(item):
        to be informed when an item is removed from self.container.

    """

    def __init__(self):
        self.container = None
        self.layoutData = {}

    def getLayoutData(self,widget):
        if not widget in self.container.contents:
            try:
                del self.layoutData[widget]
            except KeyError:
                pass
            return None
        try:
            return self.layoutData[widget]
        except KeyError:
            self.layoutData[widget] = LayoutData()
            return self.layoutData[widget]

    def add(self,items,options=None,**kws):
        """ Add items to container. Parse options and kws as approppriate for
        the specific layout manager. """
        items = flatten(items)

        for item in items:
            if item not in self.container.contents:
                item.container=self.container

        if options:
            options.__dict__.update(kws)
            kws.update(options.__dict__)
        self.add_components(*items,**kws)

        # Lay out all components.
        #self.resized(0,0)
        # Not necessary - Frame.add() calls resized() for itself
        # and all contents, and resized() calls self.layout.resized().

    def remove(self,item):
        self.remove_component(item)

        # Rearrange remaining components.
        #self.resized(0,0)
        # Not necessary; see above.

    def configure(self,**kws):
        pass

    def add_components(self,*items,**kws):
        pass

    def remove_component(self,item):
        pass

    def resized(self,dw,dh):
        raise UnimplementedMethod(self,"resized")

##############################################################################

from math import sin,cos,sqrt
class CircleManager(LayoutManager):
    """ A simple layout manager to demonstrate how to implement one.
    All components are spaced equiradially in a circle; all components
    are laid out as equally-sized squares. Run test_circle.py to see
    the results. """

    def __init__(self):
        LayoutManager.__init__(self)

    def resized(self,dw,dh):
        # Here we just compute where all the container's contents
        # should be and assign the geometry.
        w = self.container.width
        h = self.container.height

        # Center of the container...
        cx = w/2.0
        cy = h/2.0

        # Approximate radius of the circle...
        radius = min((w,h))/2.0
        radius = int(radius)
        
        # How many radians per object?
        cts = self.container.contents
        try:
            rads = 2.0*3.14159/len(cts)
        except ZeroDivisionError:
            # Nothing to do.
            return

        # Compute the approximate maximum size of each object.
        if len(cts)<6:
            # Special handling until sin(rads) gets to a reasonable range.
            csize = radius/2
            radius -= radius/3
        else:
            csize = int(radius*sin(rads))/2
            radius -= csize

        for (item,n) in zip(cts,list(range(len(cts)))):
            # Find center of component.
            ix = cx + sin(n*rads)*radius
            iy = cy + cos(n*rads)*radius

            # Adjust for top-left corner.
            ix -= csize/2.0
            iy -= csize/2.0

            # Set geometry.
            item.geometry = (int(ix),int(iy),csize,csize)

##############################################################################

class SimpleGridException(Error):

    def __init__(self,obj,msg):
        Error.__init__(self,obj,msg)

class SimpleGridManager(LayoutManager):
    """ A simple gridder like Java's GridLayout.

    The layout uses a grid of equally-sized cells. A component may
    occupy one or more rows and columns. As the container expands and
    contracts, all rows and columns get an equal share of the vertical
    and horizontal space. The constructor accepts row and column
    keywords indicating the initial number of rows and columns in the
    grid, but the grid expands as needed if additional rows or columns
    are specified when adding a particular component. Row and column
    numbers are 0-based.

    The add() method accepts keyword arguments as follows:

    row = the row in which to place the top of the first component.
    col = the column in which to place the left side of the first component.
    rowspan = the number of rows the component occupies.
    colspan = the number of columns the component occupies.
    insets = a tuple (x_inset,y_inset), where the insets specify the
             number of pixels to be left empty surrounding the
             component, along the x and y axes.

    If row or col is omitted, the manager attempts to choose a
    "reasonable" location. rowspan and colspan default to 1. insets
    defaults to (0,0). If more than one component is specified,
    they are placed in subsequent columns until the grid's maximum
    number of columns is reached; then a new row is started. The
    rowspan, colspan, and insets are applied to all components
    of a single add() call.

    """

    def __init__(self,cols=1,rows=1,minwidth=30,minheight=30):
        LayoutManager.__init__(self)
        self.rows = rows
        self.cols = cols
        self.minw = minwidth
        self.minh = minheight
        self.cur_row = 0
        self.cur_col = 0

    def add_components(self, *items, **kwds):
        # Record each item's grid location and span.
        if 'row' in list(kwds.keys()):
            self.cur_row = kwds['row']
        if 'col' in list(kwds.keys()):
            self.cur_col = kwds['col']
        rs = 1
        cs = 1
        if 'rowspan' in list(kwds.keys()):
            rs = kwds['rowspan']
        if 'colspan' in list(kwds.keys()):
            cs = kwds['colspan']
        insets = (0,0)
        if 'insets' in list(kwds.keys()):
            insets = kwds['insets']
        for comp in items:
            ld = self.getLayoutData(comp)
            ld.row = self.cur_row
            ld.col = self.cur_col
            ld.rows = rs
            ld.cols = cs
            ld.insets = insets
            if self.rows < self.cur_row + rs:
                self.rows = self.cur_row + rs
            if self.cols < self.cur_col + cs:
                self.cols = self.cur_col + cs
            self.cur_col += cs
            if self.cur_col >= self.cols:
                self. cur_col = 0
                self.cur_row += rs

    def resized(self,dw,dh):
        # Compute the proper width and height for each
        # component.
        w = self.container.width
        h = self.container.height
        rowh = h/self.rows
        colw = w/self.cols
        if rowh < self.minh: rowh = self.minh
        if colw < self.minw: colw = self.minw
        for comp in self.container.contents:
            ld = self.getLayoutData(comp)
            x = ld.col * colw + ld.insets[0]
            y = ld.row * rowh + ld.insets[1]
            comp.geometry = (x,y,colw*ld.cols-(2*ld.insets[0]),rowh*ld.rows-(2*ld.insets[1]))

##############################################################################

class GridException(Error):

    def __init__(self,obj,msg):
        Error.__init__(self,obj,msg)

class RowColData:
    """ Data about a GridManager's rows and columns.
    Size, minimum size, weight. """

    def __init__(self,**kws):
        self.__dict__.update(kws)

class GridManager(LayoutManager):
    """ A gridder like Java's GridBagLayout or Tk's gridder.

    This is a lot like SimpleGridManager, except the rows and columns
    can be of different sizes. Rows and columns expand and contract
    according to a proportional weight as the container is resized.
    A row or column with weight 0 is fixed in size and will never
    expand or contract; others receive an amount of space proportional
    to their weight divided by the total weight of all rows or columns.

    You can also specify a minimum size for a row or column, in which
    case it will never be smaller than the size you specify.

    The add() method accepts the following keyword arguments:

    row = the row in which to place the top of the first component.
    col = the column in which to place the left side of the first component.
    rowspan = the number of rows the component occupies.
    colspan = the number of columns the component occupies.
    insets = a tuple (x_inset,y_inset), where the insets specify the
             number of pixels to be left empty surrounding the
             component, along the x and y axes.
    xweight = the weight to assign to each column affected by the
             add() call. The most recent weight assigned to a column
             is the one used.
    yweight = the weight to assign to each row affected by the
             add() call. The most recent weight assigned to a row
             is the one used.
    xsize = the size (in pixels) to assign to each column affected by
             the add() call. The largest size assigned to a column
             is the one used. If the column weight is not 0, this
             option has no effect.
    ysize = the size (in pixels) to assign to each row affected by
             the add() call. The largest size assigned to a row
             is the one used. If the row weight is not 0, this
             option has no effect.
    minwidth = the minimum width to assign to each column affected
             by the add() call. The largest minwidth assigned to a
             column is the one used.
    minheight = the minimum height to assign to each row affected
             by the add() call. The largest minheight assigned to a
             row is the one used.

    Any of the keyword arguments xweight, yweight, xsize, ysize,
    minwidth, or minheight can be used with the configure() method
    in order to set row/column parameters independently of the
    add() method. configure() also expects a row and/or column
    keyword, to tell it which row/column to configure.

    """

    def __init__(self,cols=1,rows=1,xweight=1,yweight=1):
        LayoutManager.__init__(self)
        self.rows = rows
        self.cols = cols
        self.xweight = xweight
        self.yweight = yweight
        self.cur_row = 0
        self.cur_col = 0
        self.rowinfo = []
        self.colinfo = []
        for i in range(rows):
            self.rowinfo.append(RowColData(weight=yweight,size=0,minsize=0))
        for i in range(cols):
            self.colinfo.append(RowColData(weight=xweight,size=0,minsize=0))

    def add_components(self, *items, **kwds):

        # Which row+col do we start with?
        if 'row' in list(kwds.keys()):
            self.cur_row = kwds['row']
        if 'col' in list(kwds.keys()):
            self.cur_col = kwds['col']

        # What's the column and row span of the component(s)?
        rs = 1
        cs = 1
        if 'rowspan' in list(kwds.keys()):
            rs = kwds['rowspan']
        if 'colspan' in list(kwds.keys()):
            cs = kwds['colspan']

        # Are insets specified?
        insets = (0,0)
        if 'insets' in list(kwds.keys()):
            insets = kwds['insets']

        # Ensure the row and column arrays are large enough.
        self.expand_rowcoldata(rs,cs)

        # Extract any row/column attributes.
        xsize,ysize = self.compute_rowcol_data(**kwds)

        # Place each component in the grid.
        for comp in items:
            self.expand_rowcoldata(rs,cs)
            self.compute_rowcol_data(**kwds)
            if xsize == 0:
                self.colinfo[self.cur_col].size = comp.width
            if ysize == 0:
                self.rowinfo[self.cur_row].size = comp.height
            ld = self.getLayoutData(comp)
            ld.row = self.cur_row
            ld.col = self.cur_col
            ld.rows = rs
            ld.cols = cs
            ld.insets = insets
            self.cur_col += 1
            if self.cur_col >= self.cols:
                self.cur_col = 0
                self.cur_row += 1

        # Lay out all components.
        #self.resized(0,0)

    def configure(self,**kws): self.add_components(**kws)

    def resized(self,dw,dh):
        # Actually compute the proper width and height for each
        # component.

        # First, figure out the proper sizes of all rows and columns.
        self.w = self.container.width
        self.h = self.container.height

        self.compute_leftover_wh()
        
        self.trw = self.get_total_row_wt()
        self.tcw = self.get_total_col_wt()
        
        for i in range(0,self.rows):
            self.compute_row_size(self.rowinfo[i])
        for i in range(0,self.cols):
            self.compute_col_size(self.colinfo[i])

        # Then figure out the dimensions of each component.
        for comp in self.container.contents:
            ld = self.getLayoutData(comp)
            x,y = self.get_comp_xy(comp)
            w = self.get_comp_width(comp)
            h = self.get_comp_height(comp)
            comp.geometry = (x+ld.insets[0],y+ld.insets[1],w-(2*ld.insets[0]),h-(2*ld.insets[1]))

    def get_comp_xy(self,comp):
        x = 0
        y = 0
        ld = self.getLayoutData(comp)
        for i in range(0,ld.col):
            x += self.colinfo[i].size
        for i in range(0,ld.row):
            y += self.rowinfo[i].size
        return (x,y)

    def get_comp_width(self,comp):
        w = 0
        ld = self.getLayoutData(comp)
        for i in range(ld.col,ld.col+ld.cols):
            w += self.colinfo[i].size
        return w

    def get_comp_height(self,comp):
        h = 0
        ld = self.getLayoutData(comp)
        for i in range(ld.row,ld.row+ld.rows):
            h += self.rowinfo[i].size
        return h

    def get_total_row_wt(self):
        wt = 0
        for i in range(0,self.rows):
            wt += self.rowinfo[i].weight
        return wt

    def get_total_col_wt(self):
        wt = 0
        for i in range(0,self.cols):
            wt += self.colinfo[i].weight
        return wt

    def compute_leftover_wh(self):
        # Find extra width and height left over after fixed-width rows
        # and columns are subtracted from the total available space.
        width = self.container.width
        for i in range(0,self.cols):
            if self.colinfo[i].weight == 0:
                width -= self.colinfo[i].size
            else:
                width -= self.colinfo[i].minsize
        self.extra_w = width
        height = self.container.height
        for i in range(0,self.rows):
            if self.rowinfo[i].weight == 0:
                height -= self.rowinfo[i].size
            else:
                height -= self.rowinfo[i].minsize
        self.extra_h = height

    def compute_row_size(self,row):
        if row.weight != 0:
            row.size = row.minsize + int((float(row.weight)/float(self.trw))*self.extra_h)

    def compute_col_size(self,col):
        if col.weight != 0:
            col.size = col.minsize + int((float(col.weight)/float(self.tcw))*self.extra_w)

    def expand_rowcoldata(self,rs=1,cs=1):
        while self.rows < self.cur_row + rs:
            self.rows += 1
            self.rowinfo.append(RowColData(weight=0,size=0,minsize=0))
        while self.cols < self.cur_col + cs:
            self.cols = self.cols+1
            self.colinfo.append(RowColData(weight=0,size=0,minsize=0))

    def compute_rowcol_data(self,**kwds):
        # What weights should we use? Last weight specified for
        # a particular row/column wins.
        xw = 1
        yw = 1
        if 'xweight' in list(kwds.keys()):
            xw = kwds['xweight']
            self.colinfo[self.cur_col].weight = xw
        if 'yweight' in list(kwds.keys()):
            yw = kwds['yweight']
            self.rowinfo[self.cur_row].weight = yw

        # Are row or column sizes specified? Last one specified for a
        # particular row or column wins. We use the maximum size of any
        # added component by default.
        xsize = 0
        ysize = 0
        if 'xsize' in list(kwds.keys()):
            xsize = kwds['xsize']
            if self.colinfo[self.cur_col].size < xsize:
                self.colinfo[self.cur_col].size = xsize
        if 'ysize' in list(kwds.keys()):
            ysize = kwds['ysize']
            if self.rowinfo[self.cur_row].size < ysize:
                self.rowinfo[self.cur_row].size = ysize

        # Are row or column -minimum- sizes specified? Largest one
        # specified for a particular row or column wins.
        xmsize = 0
        ymsize = 0
        if 'minwidth' in list(kwds.keys()):
            xmsize = kwds['minwidth']
            if self.colinfo[self.cur_col].minsize < xmsize:
                self.colinfo[self.cur_col].minsize = xmsize
        if 'minheight' in list(kwds.keys()):
            ymsize = kwds['minheight']
            if self.rowinfo[self.cur_row].minsize < ymsize:
                self.rowinfo[self.cur_row].minsize = ymsize

        return (xsize,ysize)

##############################################################################

class Placer(LayoutManager):
    """ Implements the placement mechanism described in Greg Ewing's
    Python GUI API proposal. """

    def __init__(self):
        LayoutManager.__init__(self)

    def add_components(self, *items, **kwds):
        """Add a list of components to the Frame with positioning,
        resizing  and scrolling options. See the manual for details.
        (Yes, I'm too lazy to write it all out here again.)"""

        left       = kwds.get('left',       None)
        right      = kwds.get('right',      None)
        top        = kwds.get('top',        None)
        bottom     = kwds.get('bottom',     None)
        position   = kwds.get('position',   None) # Shortcut for (left, top)
        hmove      = kwds.get('hmove',      None)
        vmove      = kwds.get('vmove',      None)
        hstretch   = kwds.get('hstretch',   None)
        vstretch   = kwds.get('vstretch',   None)
        direction  = kwds.get('direction',  Defaults.direction)
        space      = kwds.get('space',      Defaults.space)

        def side(spec, name, self=self):
            if spec is not None:
                if isinstance(spec, tuple):
                    return spec
                elif isinstance(spec, int):
                    return None, spec
                elif isinstance(spec, object):
                    return spec, 0
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
        if position != None:
            assert left == None and top == None, "position shouldn't be overspecified"
            left, top = position
        left_obj, left_off = side(left, 'left')
        right_obj, right_off = side(right, 'right')
        top_obj, top_off = side(top, 'top')
        bottom_obj, bottom_off = side(bottom, 'bottom')
        # Process the items
        items = flatten(items)
        for item in items:
            x = item.x
            y = item.y
            w = item.width
            h = item.height
            # Calculate left edge position
            if left_obj:
                l = left_obj.x + left_obj.width + left_off
            elif left_off is not None:
                l = left_off
            else:
                l = None
            # Calculate top edge position
            if top_obj:
                t = top_obj.y + top_obj.height + top_off
            elif top_off is not None:
                t = top_off
            else:
                t = None
            # Calculate right edge position
            if right_obj:
                r = right_obj.x - right_off
            elif right_off is not None:
                r = self.container.width - right_off
            else:
                r = None
            # Calculate bottom edge position
            if bottom_obj:
                b = bottom_obj.y - bottom_off
            elif bottom_off is not None:
                b = self.container.height - bottom_off
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
            # Record resizing and border options
            ld = self.getLayoutData(item)
            ld._hmove = hmove
            ld._vmove = vmove
            ld._hstretch = hstretch
            ld._vstretch = vstretch
            #item._border = border
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


    def resize_component(self, comp, cdw, cdh):
        """Called whenever the component's container changes size.
        Adjusts the component's size according to its moving and
        stretching options."""
        dx = 0
        dy = 0
        dw = 0
        dh = 0
        ld = self.getLayoutData(comp)
        if ld._hmove:
            dx = cdw
        elif ld._hstretch:
            dw = cdw
        if ld._vmove:
            dy = cdh
        elif ld._vstretch:
            dh = cdh
        if dx != 0 or dy != 0 or dw != 0 or dh != 0:
            comp.geometry = (comp.x + dx, comp.y + dy,
                             comp.width + dw, comp.height + dh)

    def resized(self,dw,dh):
        #log("Resized",dw,dh,self.container)
        for c in self.container.contents:
            self.resize_component(c,dw, dh)

