"""txtwgts.py - a collection of textual UI widgets that work on a plain
dumb terminal or under curses.
"""
import sys
import os

from manygui.Utils import log

# Some useful event codes.
DOWN_ARROW=258
UP_ARROW=259
LEFT_ARROW=260
RIGHT_ARROW=261
ESCAPE=27
BACKSPACE=127
LEFT_BRACKET=91
WINMENU_EVENT=990
FOCUS_FORWARD_EVENT=991
FOCUS_BACKWARD_EVENT=992
REFRESH_EVENT=997
QUIT_EVENT=998
HELP_EVENT=999
COMMAND_EVENT=1000
SCROLL_LEFT=951
SCROLL_RIGHT=952
SCROLL_UP=953
SCROLL_DOWN=954
SELECT_BEGIN_EVENT=955
SELECT_END_EVENT=956
APPMENU_EVENT=957

# Map of character codes to names.
_charnames = {ord(' '):'space',
              DOWN_ARROW:'down arrow',
              UP_ARROW:'up arrow',
              LEFT_ARROW:'left arrow',
              RIGHT_ARROW:'right arrow',
              ESCAPE:'ESC',
              BACKSPACE:'backspace',
              HELP_EVENT:'ESC-?',
              COMMAND_EVENT:'ESC-ESC',
              QUIT_EVENT:'ESC-q-u-i-t',
              SCROLL_LEFT:'ESC-leftarrow',
              SCROLL_RIGHT:'ESC-rightarrow',
              SCROLL_UP:'ESC-uparrow',
              SCROLL_DOWN:'ESC-downarrow',
              WINMENU_EVENT:'ESC-w',
              SELECT_BEGIN_EVENT:'ESC-s',
              SELECT_END_EVENT:'ESC-e',
              APPMENU_EVENT:'ESC-m',
              1:'^A',
              2:'^B',
              3:'^C',
              4:'^D',
              5:'^E',
              6:'^F',
              7:'^G',
              8:'^H',
              9:'^I',
              10:'linefeed (^J)',
              11:'^K',
              12:'^L',
              13:'return (^M)',
              14:'^N',
              15:'^O',
              16:'^P',
              17:'^Q',
              18:'^R',
              19:'^S',
              20:'^T',
              21:'^U',
              22:'^V',
              23:'^W',
              24:'^X',
              25:'^Y',
              26:'^Z'
              }

# Screen-management package.
# FIX ME!
#import scr_curses
#import scr_text
#_scr = scr_curses
global _scr
_scr = None

refresh_all_flag = 0
def refresh_all():
    global refresh_all_flag
    refresh_all_flag = 1

_all_components = [] # List of all controls. Used for focus management.
_focus_control = None
_focus_capture_control = None
_focus_dir = 1
def discard_focus():
    global _focus_control
    old_fc = _focus_control
    _focus_control = None
    old_fc.focus_lost()

def add_to_focus_list(comp):
    """ Add comp to _all_components in the proper focus-visit position. """
    #_scr.dbg("Adding %s to focus list"%comp)
    prev_comp = None
    if comp.parent:
        # Find last control in the container in _all_components
        # that is not comp.
        c = comp.parent
        prev_comp = c # Insert after container by default.
        rcs = c._contents[:]
        rcs.reverse()
        for cc in rcs:
            if cc is not comp and cc in _all_components:
                prev_comp = cc
                break
    #_scr.dbg("prev_comp: %s"%prev_comp)
    if prev_comp:
        ii = _all_components.index(prev_comp)
        _all_components.insert(ii+1,comp)
        #_scr.dbg("_all_components: %s"%(_all_components))
        return
    _all_components.append(comp)
    #_scr.dbg("_all_components: %s"%(_all_components))

def remove_from_focus_list(comp):
    #_scr.dbg("Removing from focus list",comp,'\n')
    if _focus_control is comp:
        _app.change_focus()
    if _focus_control is comp:
        discard_focus()
    try:
        _all_components.remove(comp)
    except ValueError:
        pass

def in_focus_purview(comp):
    if _focus_capture_control is None:
        return 1
    return contains(_focus_capture_control,comp)

def contains(cont,comp):
    while comp:
        if comp == cont: return 1
        try:
            comp = comp.parent
        except AttributeError:
            return 0
    return 0

def set_scale(x,y):
    ComponentMixin._horiz_scale = float(x)/640.0
    ComponentMixin._vert_scale = float(y)/480.0

class ComponentMixin:
    """ Mixin class for components.
    We're really only using curses as a screen-addressing
    library, since its implementation of "windows" isn't
    really very much like a GUI window. """

    def __repr__(self): return "%s %s"%(self.__class__,self.text)
    def __str__(self): return "%s %s"%(self.__class__,self.text)

    # We'll map coordinates according to these scaling factors.
    # This lets normal manygui programs run under curses without
    # having to scroll the screen. This might not be such a
    # good idea, but it's worth a try.
    _horiz_scale = 80.0/640.0
    _vert_scale = 24.0/480.0
    #_horiz_scale = 1.0
    #_vert_scale = 1.0

    x=100
    y=100
    width=100
    height=100

    # If true for a particular class or component, we'll draw
    # a border around the component when it's displayed.
    _border = 1 # For debugging.
    visible = 1
    parent = None
    _needs_parent = 0
    title = "txtgui"
    _gets_focus = 1
    text = "txtgui"
    _use_text = 1
    _textx = 1
    _texty = 1
    _tiny_LLCORNER = ord('<')
    _tiny_LRCORNER = ord('>')

    # Event-handler maps.
    _event_map = {}
    _event_range_map = {}

    #refresh = 1

    def __init__(self,parent=None,geometry=(0,0,100,100),text="",*args,**kws):
        ##_scr.dbg("Creating %s"%self)
        self._created = 0
        self._cpos = 1,1 # Cursor position when in focus.
        # Border characters:
        self._LVLINE = _scr.SCR_LVLINE
        self._RVLINE = _scr.SCR_RVLINE
        self._UHLINE = _scr.SCR_UHLINE
        self._LHLINE = _scr.SCR_LHLINE
        self._ULCORNER = _scr.SCR_ULCORNER
        self._URCORNER = _scr.SCR_URCORNER
        self._LLCORNER = _scr.SCR_LLCORNER
        self._LRCORNER = _scr.SCR_LRCORNER
        self._attr = _scr.ATTR_NORMAL
        self.resize_command = None
        self.focus_lost_cmd = None
        self.set_parent(parent)
        self.set_geometry(geometry)
        self.set_text(text)

    def __str__(self):
        return("%s (%s)@(%d,%d)"%(self.__class__.__name__,self.text,self.x,self.y))

    def curs_resized(self,dw,dh):
        if self.resize_command:
            self.resize_command(dw,dh)

    def set_geometry(self, xxx_todo_changeme,event=0):
        (x,y,w,h) = xxx_todo_changeme
        self.x = x
        self.y = y
        dw = w-self.width
        dh = h-self.height
        self.width = w
        self.height = h
        if event:
            self.curs_resized(dw,dh)
        #self.redraw()

    def get_control_help(self):
        helpstr = ""
        if hasattr(self,"_help"):
            helpstr = helpstr + self._help + '\n\n'
        if type(self.__class__.__doc__) == type(""):
            helpstr = helpstr + self.__class__.__doc__
        return helpstr

    def get_event_help(self):
        items = []
        evmap = self._event_map
        kk = list(evmap.keys())
        kk.sort()
        for ch in kk:
            f = evmap[ch]
            if f == ComponentMixin.ignore_event:
                continue
            doc = f.__doc__
            try:
                c = _charnames[ch]
            except KeyError:
                try:
                    c = chr(ch)
                except (TypeError,ValueError):
                    c = str(ch)
            if doc is not None:
                item = c+": "+str(doc)
                items += item.split('\n')
                items.append(' ')
        try:
            if self.parent:
                items += self.parent.get_event_help()
        except:
            a,b,c = sys.exc_info()
            items.append("*** Exception gathering help data!"+str(b))
        return items

    def is_visible(self):
        #_scr.dbg("is_visible %s"%self)
        if self.visible: return self.parent.is_visible()

    def set_visible(self,vis):
        #_scr.dbg("set_visible",vis,self)
        self.visible = vis

    def focus_gained(self):
        pass

    def focus_lost(self):
        pass
        #self.redraw()

    def set_focus(self,val):
        #self._ensureenabled_state()
        global _focus_control
        if val:
            _focus_control = self
            #_scr.dbg("set_focus:",self._gets_focus,self.is_visible(),self._created,in_focus_purview(self),self)
            if self._gets_focus and self.is_visible() and self._created \
               and in_focus_purview(self):
                self.focus_gained()
                return
            else:
                _app.change_focus(_focus_dir)
        else:
            if _focus_control is self:
                discard_focus()

    def set_focus_capture(self,val):
        global _focus_capture_control
        if val:
            _focus_capture_control = self
            _app.change_focus()
        else:
            if _focus_capture_control is self:
                _focus_capture_control = None

    def scale_xy(self,x,y):
        return (int(x*self._horiz_scale),int(y*self._vert_scale))
    def scale_yx(self,y,x):
        nx,ny = self.scale_xy(x,y)
        return ny,nx

    def screen_height(self):
        w,h = self.scale_xy(self.width,self.height)
        if h<1: h=1
        return h

    def screen_width(self):
        w,h = self.scale_xy(self.width,self.height)
        if w<2: w=2
        return w

    def effective_texty(self):
        return min(self._texty,self.screen_height()-1)

    def get_screen_coords(self):
        if not self._created: return 0,0
        #if self._needs_parent and not self.parent: return 0,0
        x,y = self.scale_xy(self.x,self.y)
        ##_scr.dbg("_gsc: %s,%s: %s"%(x,y,self.text))
        if not self.parent:
            return x,y
        cx,cy = self.parent.get_screen_coords()
        return x+cx, y+cy

    def _parent_intersect(self,x,y,w,h):
        #_scr.dbg("_parent_instersect",self)
        # Get the screen rectangle representing the intersection of
        # the component and its parent.
        if not self._created:
            #_scr.dbg("0,0,0,0")
            return 0,0,0,0
        #if self._needs_parent and not self.parent: return 0,0,0,0
        if not self.parent:
            return x,y,w,h
        cx,cy,cw,ch = self.parent.get_bounding_rect()
        ix = max(x,cx)
        iy = max(y,cy)
        ix2 = min(x+w,cx+cw)
        iy2 = min(y+h,cy+ch)
        iw = ix2-ix
        ih = iy2-iy
        if iw<0: iw=0
        if ih<0: ih=0
        ##_scr.dbg("parent_intersect (%s,%s) %s,%s,%s,%s: %s"%(x,y,ix,iy,iw,ih,self))
        #_scr.dbg(ix,iy,iw,ih)
        return ix,iy,iw,ih

    def addstr(self,x,y,str,attr=0):
        if attr == 0:
            attr = self._attr
        sx,sy,w,h = self.get_bounding_rect()
        if y>=h: return
        x += sx
        y += sy
        _scr.addstr(x,y,str,sx+w-x,attr)

    def get_bounding_rect(self):
        # Get the screen x,y,w,h of the visible portion of the component.
        # If the control is invisible or completely clipped, w and h
        # are both 0.
        if not self.visible or not self._created:
            return 0,0,0,0
        x,y = self.get_screen_coords()
        ##_scr.dbg("%s,%s: %s"%(x,y,self))
        w,h = self.screen_width(), self.screen_height()
        x,y,w,h = self._parent_intersect(x,y,w,h)
        return x,y,w,h

    def redraw(self):
        #_scr.dbg("Redrawing %s"%(self))
        if not self._created:
            #_scr.dbg("\tnot created")
            return
        ##_scr.dbg("Visible: %s"%self)
        #x,y = self.get_screen_coords()
        if self.is_visible():
            self.erase()
            self.draw_border()
            self.draw_contents()
            ety = self.effective_texty()
            #_scr.dbg("ety ",ety,self,self._height*self._vert_scale)
            if self._use_text:
                self.addstr(self._textx,ety,str(self.text))
        else:
            #_scr.dbg("\tnot visible")
            pass

    def erase(self):
        if not self._created: return
        x,y,w,h = self.get_bounding_rect()
        #_scr.dbg("Erasing %s"%self)
        _scr.erase(x,y,w,h)

    def draw_border(self):
        if not self._created: return
        if not self._border: return
        x,y = self.get_screen_coords()
        w,h = self.screen_width(), self.screen_height()
        ##_scr.dbg("Screen coords %s for %s"%((x,y,w,h),self))
        x,y,w,h = self._parent_intersect(x,y,w,h)
        if w == 0 or h == 0: return
        ##_scr.dbg("Parent intersect %s for %s"%((x,y,w,h),self))

        llcorner = self._LLCORNER
        lrcorner = self._LRCORNER
        if self.screen_height() < 2:
            llcorner = self._tiny_LLCORNER
            lrcorner = self._tiny_LRCORNER
        else:
            for xx in range(x+1,x+w-1):
                _scr.addch(y,xx,self._UHLINE)
                _scr.addch(y+h-1,xx,self._LHLINE)
            for yy in range(y+1,y+h-1):
                _scr.addch(yy,x,self._LVLINE)
                _scr.addch(yy,x+w-1,self._RVLINE)
            _scr.addch(y,x,self._ULCORNER)
            _scr.addch(y,x+w-1,self._URCORNER)

        _scr.addch(y+h-1,x,llcorner)
        _scr.addch(y+h-1,x+w-1,lrcorner)

    def draw_contents(self):
        if not self._created: return
        pass

    def ensure_focus(self):
        if not self._created: return
        x,y = self.get_screen_coords()
        #_scr.dbg("Ensuring focus %s,%s on %s"%(x,y,self))
        if _focus_control is self:
            #_scr.dbg("Ensuring focus on ",self)
            #_scr.dbg("   HAS FOCUS!")
            ety = self.effective_texty()
            #_scr.dbg("focus ety ",ety,self,self._height*self._vert_scale)
            _scr.move_cursor(x+self._textx,y+ety)

    def handle_event(self,ev):
        handled = self.event_handler(ev)
        if handled: return 1
        if self.parent:
            # Propagate unhandled events to parent.
            return self.parent.handle_event(ev)
        return 0

    def event_handler(self,ev):
        try:
            handled = self._event_map[ev](self,ev)
            return handled
        except KeyError:
            for (lo,hi) in list(self._event_range_map.keys()):
                if ev>=lo and ev<=hi:
                    handled = self._event_range_map[(lo,hi)](self,ev)
                    return handled
        return 0

    def ignore_event(self,ev):
        return 0

    def iscreated(self):
        return self._created

    def create(self):
        #_scr.dbg("Creating: %s"%self)
        if self._created:
            #_scr.dbg("\talready created")
            return 0
        if self._needs_parent and not self.parent:
            #_scr.dbg("\tNo parent")
            return 0
        self._created = 1
        add_to_focus_list(self)
        return 1

    def set_enabled(self,enabled):
        #_scr.dbg("ENSURING ENABLED",self)
        # UNTESTED!
        if not enabled:
            #_scr.dbg("   NOT ENABLED")
            self._gets_focus = 0
            if _focus_control is self:
                _app.change_focus()
        else:
            #_scr.dbg("   ENABLED")
            self._gets_focus = self.__class__._gets_focus

    def destroy(self):
        #_scr.dbg("Destroying: %s"%self)
        self.set_focus_capture(0)
        remove_from_focus_list(self)
        self.erase()
        self._created = 0

    def set_parent(self,cont):
        if self.parent:
            self.parent.remove(self)
        if cont:
            cont.add(self)
        self.parent = cont

    def set_text(self,text):
        self.text=text

class ParentMixin(ComponentMixin):
    """ Special handling for parents. These are mostly the
    same, presentation-wise, as regular components, but they
    manage their focus differently. """

    def __init__(self,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        self._contents = []

    def is_visible(self):
        #_scr.dbg("Parent: is_visible %s"%self)
        if self.parent:
            return ComponentMixin.is_visible(self)
        if self.visible: return 1
        return 0

    def redraw(self):
        #_scr.dbg("Parent redraw",self,self._contents)
        if not self._created:
            #_scr.dbg("\tnot created")
            return
        ComponentMixin.redraw(self)
        for comp in self._contents:
            comp.redraw()

    def create(self):
        ComponentMixin.create(self)
        if self._created:
            for comp in self._contents:
                comp.create()

    def destroy(self):
        #_scr.dbg("Destroying ",self)
        self.set_focus_capture(0)
        remove_from_focus_list(self)
        for comp in self._contents:
            comp.destroy()
        ##_scr.dbg("Focus on ",_focus_control,"after dtoy",self)
        self.erase()
        self._created = 0

    def ensure_focus(self):
        #_scr.dbg("Ensuring focus in %s"%self)
        ComponentMixin.ensure_focus(self)
        for win in self._contents:
            win.ensure_focus()

    def remove(self, comp):
        try:
            # Fix the focus.
            if _focus_control is self:
                _app.change_focus()

            comp.destroy()
            self._contents.remove(comp)
            comp.parent=None

            ##_scr.dbg("Refreshing %s"%self)
            #self.redraw()
        except ValueError:
            pass

    def add(self,comp):
        #_scr.dbg("Parent %s adding %s"%(self,comp))
        try:
            self._contents.remove(comp)
        except ValueError:
            pass
        self._contents.append(comp)
        comp.parent = self

class Label(ComponentMixin):

    _gets_focus = 0
    texty = 0
    _border=0

    def __init__(self,text="",*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        self.text=text
        self._LVLINE = ord('.')
        self._RVLINE = ord('.')
        self._UHLINE = ord('.')
        self._LHLINE = ord('.')
        self._ULCORNER = ord('.')
        self._URCORNER = ord('.')
        self._LLCORNER = ord('.')
        self._LRCORNER = ord('.')

class ListBox(ComponentMixin):

    _use_text = 0

    def __init__(self,items=[],command=None,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        self.selection=0
        self.items=items
        self.command=command

    def set_items(self,items):
        self.items = items
        #self.redraw()

    #def ensure_items(self):
    #    pass
    #
    #def ensure_selection(self):
    #    pass

    def get_selection(self):
        if self._created:
            return self.selection

    def set_selection(self,sel):
        self._selection=sel
        #self.redraw

    def draw_contents(self):
        lh = self.screen_height()-2
        start = 0
        if lh<len(self.items):
            start = self.selection - lh + 1
            if start<0: start = 0

        x=2;y=1
        for ii in range(start,len(self.items)):
            item = str(self.items[ii])
            if self.selection == ii:
                self.addstr(x-1,y,'>')
            self.addstr(x,y,item)
            y+=1
            if y>lh: return

    def select_down(self,ev):
        """Move listbox selection down."""
        self.selection += 1
        if self.selection >= len(self.items):
            self.selection=0
        self.redraw()
        return 1

    def select_up(self,ev):
        """Move listbox selection up."""
        self.selection -= 1
        if self.selection < 0:
            self.selection=len(self.items)-1
        self.redraw()
        return 1

    def do_click(self,ev):
        """Click on selected item."""
        if self.command:
            self.command(self,self.selection,self.items[self.selection])

    _event_map = { DOWN_ARROW:select_down,
                   UP_ARROW:select_up,
                   ord(' '):do_click }

#from bmpascii import *
#from manygui.Colors import black,white
#class Canvas(ComponentMixin):
#    #_text = "Canvas not supported in text mode."
#    _gets_focus = 0
#    _use_text = 0
#
#    def __init__(self,*args,**kws):
#        ComponentMixin.__init__(self,*args,**kws)
#        self._mustrender = 1
#        w,h = self.screen_width(),self.screen_height()
#        self._bmpw = w*4
#        self._bmph = h*6
#        line = [0] * (self._bmpw+1)
#        self._bitmap = []
#        for ll in range(self._bmph+1):
#            self._bitmap.append(line[:])
#        self._scalew = float(self._bmpw)/float(self._width)
#        self._scaleh = float(self._bmph)/float(self._height)
#        #_scr.dbg("w,h = ",self._width,self._height)
#        #_scr.dbg("bmpw,bmph = ",self._bmpw,self._bmph)
#        #_scr.dbg("scalew,scaleh = ",self._scalew,self._scaleh)
#
#    def draw_line(self,point1,point2,color=None):
#        if color is None:
#            color = self.defaultLineColor
#        if color != white:
#            color = 1
#        else:
#            color = 0
#        x1,y1 = point1
#        x2,y2 = point2
#        #_scr.dbg("draw_line",x1,y1,"->",x2,y2)
#        if x1 == x2:
#            if y1>y2: y2,y1 = y1,y2
#            for y in range(y1,y2+1):
#                ey = int(y*self._scaleh)
#                ex = int(x1*self._scalew)
#                #_scr.dbg("Setting x,y --> ez,ey",x1,y,ex,ey)
#                try:
#                    self._bitmap[ey][ex] = color
#                except:
#                    pass
#            return
#        if x1<0 or x1>self._width or x2<0 or x2>self._width:
#            return
#        if y1<0 or y1>self._height or y2<0 or y2>self._height:
#            return
#
#        if x1>x2:
#            #x1,y1,x2,y2 = x2,y2,x1,y1
#            x1,x2 = x2,x1
#            y1,y2 = y2,y1
#        # y = mx+b, so
#        # y1 = m*x1+b
#        # y2 = m*x2+b
#        # y1-y2 = m*x1 - m*x2
#        # y1-y2 = m(x1-x2)
#        m = (float(y1)-float(y2))/(float(x1)-float(x2))
#        # and
#        b = float(y1)-m*float(x1)
#        for x in range(x1,x2+1):
#            y = m*x+b
#            ey = int(y*self._scaleh)
#            ex = int(x*self._scalew)
#            #_scr.dbg("Setting x,y --> ez,ey",x,y,ex,ey)
#            try:
#                self._bitmap[ey][ex] = color
#            except:
#                pass
#            #self._bitmap[ey][ex] = not self._bitmap[ey][ex]
#    
#    def drawLine(self, x1, y1, x2, y2, color=None, width=None):
#        "Draw a straight line between x1,y1 and x2,y2."
#        self.draw_line((x1,y1),(x2,y2),color)
#
#    def drawPolygon(self, pointlist,
#                    edgeColor=None, edgeWidth=None, fillColor=None, closed=0):
#        #_scr.dbg("FILLING, fillColor is",fillColor)
#        self._fillColor = fillColor
#        for ip in range(len(pointlist)-1):
#            self.draw_line(pointlist[ip],pointlist[ip+1],edgeColor)
#        if closed:
#            #_scr.dbg("CLOSED POLY",pointlist)
#            self.draw_line(pointlist[-1],pointlist[0],edgeColor)
#            self.fillPoly(pointlist)
#        self._mustrender = 1
#
#    def fillPoly(self,ps):
#        if self._fillColor is None:
#            return
#        if self._fillColor != white:
#            color = 1
#        else:
#            color = 0
#        #_scr.dbg("FILLING, fillColor is",self._fillColor)
#        x1 = 9999
#        y1 = 9999
#        x2 = 0
#        y2 = 0
#        for p in ps:
#            if p[0]<x1:
#                x1 = p[0]
#            if p[0]>x2:
#                x2 = p[0]
#            if p[1]<y1:
#                y1=p[1]
#            if p[1]>y2:
#                y2=p[1]
#        #_scr.dbg("FILLING in rect",x1,y1,"x",x2,y2)
#        for x in range(x1+1,x2-1):
#            for y in range(y1+1,y2-1):
#                if self.pnpoly(ps,x,y):
#                    #_scr.dbg(x,y,"is in poly",ps)
#                    ey = int(y*self._scaleh)
#                    ex = int(x*self._scalew)
#                    #_scr.dbg("Clearing x,y --> ez,ey",x,y,ex,ey)
#                    try:
#                        self._bitmap[ey][ex] = color
#                    except:
#                        pass
#                    #self._bitmap[ey][ex] = not self._bitmap[ey][ex]
#
#    def render(self):
#        if not self._mustrender: return
#        self._mustrender = 0
#        self._str = bmp2ascii(self._bitmap)
#
#    def draw_contents(self):
#        self.render()
#        strs = self._str.split('\n')
#        y = 0
#        for line in strs:
#            self.addstr(0,y,line)
#            y += 1
#        
#    def pnpoly(self,ps, x, y):
#        i=0
#        j=0
#        c=0
#        npol = len(ps)
#        for i,j in zip(range(0,npol),range(-1,npol-1)):
#            if ((((ps[i][1]<=y) and (y<ps[j][1])) or
#                 ((ps[j][1]<=y) and (y<ps[i][1]))) and
#                (x < (ps[j][0] - ps[i][0]) * (y - ps[i][1]) / (ps[j][1] - ps[i][1]) + ps[i][0])):
#                c = not c
#        return c

class Button(ComponentMixin):

    def __init__(self,command=None,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        self.command = command
        #self._LVLINE = ord('<')
        #self._RVLINE = ord('>')
        #self._UHLINE = ord(' ')
        #self._LHLINE = ord(' ')
        #self._ULCORNER = ord('<')
        #self._URCORNER = ord('>')
        #self._LLCORNER = ord('<')
        #self._LRCORNER = ord('>')
        self._attr = _scr.ATTR_UNDERLINE

    def do_click(self,ev):
        """Click on button."""
        log("CLICKED")
        if self.command:
            self.command(self)
        else:
            log("NO COMMAND!")

    _event_map = { ord(' '):do_click }

class ToggleButtonMixin(ComponentMixin):

    textx = 2
    _on_ind = '+'
    _off_ind = '-'

    def __init__(self,on=0,value=0,command=None,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        self.command=command
        self.on=on
        self.value=value

    def curs_clicked(self,ev):
        """Click on button."""
        self.on = not self.on
        _scr.dbg(self,"clicked, now",self.on)
        self.redraw()
        if self.command:
            self.command(self,self.value)

    _event_map = { ord(' '):curs_clicked }

    def set_state(self,on):
        _scr.dbg(self,"set_state",on)
        self.on = on
        #self.redraw()

    def get_state(self):
        _scr.dbg(self,"get_state",self.on)
        return self.on

    def draw_contents(self):
        ind = self._off_ind
        if self.on:
            ind = self._on_ind
        ety = self.effective_texty()
        self.addstr(self._textx-1,ety,ind)

class CheckBox(ToggleButtonMixin):

    _border = 0

    def __init__(self,*args,**kws):
        ToggleButtonMixin.__init__(self,*args,**kws)

class RadioGroup:

    def set_value(self,val):
        for b in self._contents:
            if b.__class__ is RadioButton:
                if b.value==val:
                    b.set_state(1)
                else:
                    b.set_state(0)

class RadioButton(ToggleButtonMixin):

    _on_ind = '*'
    _off_ind = '.'
    _border = 0

    def __init__(self,group=None,*args,**kws):
        ToggleButtonMixin.__init__(self,*args,**kws)
    
    #def set_container(self,cont):
    #    ComponentMixin.set_container(self,cont)
    #    if cont:
    #        cont.set_value(self.value)

    #def curs_clicked(self,ev):
    #    """Click on button."""
    #    if self.parent is not None:
    #        self.parent.set_value(self.value)
    #    if self.command:
    #        self.command(self,self.value)

    #_event_map = { ord(' '):curs_clicked }

class DisabledTextBindings: pass

import string
class TextMixin(ComponentMixin):

    _use_text = 0 # Prevent naive text presentation.
    editable=1
    selection=(0,0)

    def __init__(self,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        self._tpos=0
        self._cur_pos=(1,1)
        self._cur_line = 0
        self._cur_col = 0
        self._startline = 0
        self._startcol = 0
        #self._curs_selection = (0,0)
        #self._curs_text = str(self.text)

    def set_editable(self,ed):
        self.editable = ed
        #_scr.dbg("ENSURING EDITABLE",self)
        # UNTESTED!
        if not self.editable:
            #_scr.dbg("   NOT EDITABLE")
            self._gets_focus = 0
            if _focus_control is self:
                _app.change_focus()
        else:
            #_scr.dbg("   EDITABLE")
            self._gets_focus = self.__class__._gets_focus

    def ensure_focus(self):
        if not self._created: return
        ComponentMixin.ensure_focus(self)
        x,y = self.get_screen_coords()
        #_scr.dbg("Ensuring focus %s,%s on %s"%(x,y,self))
        if _focus_control is self:
            ##_scr.dbg("Ensuring focus on ",self)
            ##_scr.dbg("   HAS FOCUS!")
            #ety = self.effective_texty()
            #_scr.dbg("focus ety ",ety,self,self._height*self._vert_scale)
            tx,ty = self._cur_pos
            _scr.move_cursor(x+tx+1,y+ty+1)

    def set_selection(self, xxx_todo_changeme1):
        (start,end) = xxx_todo_changeme1
        self.selection=(start,end)
        #st,en = self.selection
        #self._curs_selection = (st,en)

    def set_text(self,txt):
        self._curs_text = str(txt)
        #self.redraw()

    def get_selection(self):
        #_scr.dbg("BACKEND_SELECTION",self.selection)
        #return self._curs_selection
        if self._created:
            return self.selection

    #def ensure_editable(self):
    #    pass

    def get_text(self):
        if self._created:
            return str(self._curs_text)

    def focus_lost(self):
        pass
        #self.redraw()

    ### Event handlers ###
    def backspace(self,ev):
        """Erase character before cursor."""
        if not self.editable: return
        if self._tpos < 1: return 1
        ##self.modify(text=self.text[:self._tpos-1] + self.text[self._tpos:])
        self._curs_text=self._curs_text[:self._tpos-1] + self._curs_text[self._tpos:]
        self._tpos -= 1
        self.redraw()
        return 1

    def insert(self,ev):
        """Insert character before cursor."""
        if not self.editable: return
        if not chr(ev) in string.printable:
            return 0
        ##self.modify(text=self.text[:self._tpos] + chr(ev) + self.text[self._tpos:])
        self._curs_text=self._curs_text[:self._tpos] + chr(ev) + self._curs_text[self._tpos:]
        self._tpos += 1
        self.redraw() # FIXME: only really need to redraw current line.
        return 1

    def back(self,ev):
        """Move cursor back one character."""
        self._tpos -= 1
        if self._tpos<0: self._tpos=0
        self.redraw()
        return 1

    def fwd(self,ev):
        """Move cursor forward one character."""
        self._tpos += 1
        if self._tpos>len(self._curs_text): self._tpos=len(self._curs_text)
        self.redraw()
        return 1

    def change_focus(self,ev):
        """Focus on the next control."""
        if self.focus_lost_cmd:
            self.focus_lost_cmd()
        _app.change_focus()
        return 1

    def down_line(self,ev):
        """Move cursor down one line."""
        self.move_line(1)
        return 1
        
    def up_line(self,ev):
        """Move cursor up one line."""
        self.move_line(-1)
        return 1

    def select_start(self,ev):
        """Set the start of the selection to the current
        cursor location."""
        st,en = self.selection
        #_scr.dbg("SELECTION START 1:",st,en)
        st = self._tpos
        if en<st: en = st
        #self._curs_selection=(st,en)
        #self.modify(selection=(st,en))
        #_scr.dbg("SELECTION START:",st,en)
        self.redraw()
        return 1

    def select_end(self,ev):
        """Set the end of the selection to the current
        cursor location."""
        st,en = self.selection
        #_scr.dbg("SELECTION END 1:",st,en)
        en = self._tpos
        if en<st: st = en
        #self._curs_selection=(st,en)
        #self.modify(selection=(st,en))
        #_scr.dbg("SELECTION END:",st,en)
        self.redraw()
        return 1

    _event_map = {BACKSPACE:backspace,
                  8:backspace, #^H
                  DOWN_ARROW:down_line,
                  UP_ARROW:up_line,
                  #27:change_focus,
                  LEFT_ARROW:back,
                  RIGHT_ARROW:fwd,
                  SELECT_BEGIN_EVENT:select_start,
                  SELECT_END_EVENT:select_end,
                  15:ComponentMixin.ignore_event
                  }
    _event_range_map = {(8,255):insert}

    ### Event handler end ###

    def move_line(self,n):
        lines = str(self._curs_text).split('\n')
        nlines = len(lines)
        self._cur_line += n
        cur_line_not_0 = 1
        if self._cur_line <= 0:
            self._cur_line = 0
            cur_line_not_0 = 0
        if self._cur_line >= nlines:
            self._cur_line = nlines-1
        lline = len(lines[self._cur_line])
        if lline<self._cur_col:
            self._cur_col = lline
        trunc_lines = lines[:self._cur_line]
        self._tpos = len(string.join(trunc_lines,'\n'))+self._cur_col+cur_line_not_0
        self.redraw()

    def adjust_start(self):
        pass

    def draw_contents(self):
        if self.screen_height()<3: return
        
        t = str(self._curs_text)
        x=1;y=1
        try:
            lines = t.split('\n')
        except:
            lines = "COULD NOT RENDER TEXT IN CONTROL"
        line,col = self.find_cursor_pos(lines)

        startline,startcol = self.find_relative_cpos(line,col,len(lines),len(lines[line]))
        sh = self.screen_height()-2

        #st,en = self._curs_selection
        st,en = self.selection
        st_line,st_col = self.find_lc_pos(lines,st)
        en_line,en_col = self.find_lc_pos(lines,en)
        self.selection_lc = st_line,st_col,en_line,en_col

        for li in range(0,min(sh,len(lines)-startline)):
            #_scr.dbg("start,line:",startline,li,self)
            line = lines[startline+li]
            parts = self.partition_line(line,startline+li,startcol)
            xx = x
            for (txt,attr) in parts:
                self.addstr(xx,y,txt,attr)
                xx += len(txt)
            y+=1

    def partition_line(self,txt,line,startcol):
        st_line,st_col,en_line,en_col = self.selection_lc
        if line<st_line or line>en_line: return ((txt[startcol:],_scr.ATTR_NORMAL),)
        if line>st_line and line<en_line: return ((txt[startcol:],_scr.ATTR_SELECTED),)
        if line == st_line and line == en_line:
            # Case 1: entire selection off left.
            if en_col < startcol:
                return ((txt[startcol:],_scr.ATTR_NORMAL),)
            # Case 2: select start off left, select end in view.
            if st_col < startcol and en_col >= startcol:
                return ((txt[startcol:en_col],_scr.ATTR_SELECTED),
                        (txt[en_col:],_scr.ATTR_NORMAL))
            # Case 3: start and end in view.
            if st_col >= startcol and en_col >= startcol:
                return ((txt[startcol:st_col],_scr.ATTR_NORMAL),
                        (txt[st_col:en_col],_scr.ATTR_SELECTED),
                        (txt[en_col:],_scr.ATTR_NORMAL))
        if line == st_line:
            if st_col<startcol: return ((txt[startcol:],_scr.ATTR_SELECTED),)
            return ((txt[startcol:st_col],_scr.ATTR_NORMAL),
                    (txt[st_col:],_scr.ATTR_SELECTED))
        if line == en_line:
            if en_col<startcol: return ((txt[startcol:],_scr.ATTR_NORMAL),)
            return ((txt[startcol:en_col],_scr.ATTR_SELECTED),
                    (txt[en_col:],_scr.ATTR_NORMAL))


    def find_relative_cpos(self,line,col,nlines,nchars):
        # Take the line,col position of the cursor in self._curs_text
        # and convert it, based on window size, into the window-
        # relative cursor position, which is stored in self._cpos.
        # Then return the line and column of the character that
        # should appear at the top-left corner.
        lh = self.screen_height()-3
        lw = self.screen_width()-3

        tl_line,tl_col,rline,rcol = (self._startline,
                                     self._startcol,
                                     line-self._startline,
                                     col-self._startcol)

        if rline<0: self._startline += rline
        if rline>=lh: self._startline += rline-lh
        if rcol<0: self._startcol += rcol
        if rcol>=lw: self._startcol += rcol-lw

        tl_line,tl_col,rline,rcol = (self._startline,
                                     self._startcol,
                                     line-self._startline,
                                     col-self._startcol)

        self._cur_pos = (rcol, rline)
        return tl_line,tl_col

    def find_lc_pos(self,lines,tp):
        # Find line/col position of absolute text position.
        ll = 0
        tt = 0
        tl = len(lines)
        lastlen = 0
        line = 0
        while tt<=tp and ll<tl:
            lastlen = len(lines[ll])+1
            line = ll
            tt += lastlen
            ll += 1
        col=lastlen-(tt-tp)
        return line,col

    def find_cursor_pos(self,lines):
        # Find line/col position of cursor.
        tp = self._tpos
        line,col = self.find_lc_pos(lines,tp)
        self._cur_line = line
        self._cur_col = col
        return line,col

class TextField(TextMixin):

    def __init__(self,*args,**kws):
        TextMixin.__init__(self,*args,**kws)

    _event_map = {}
    _event_map.update(TextMixin._event_map)
    del _event_map[UP_ARROW] # No line control in TextFields.
    del _event_map[DOWN_ARROW]
    _event_map[ord('\n')] = TextMixin.change_focus

class TextArea(TextMixin):

    def __init__(self,*args,**kws):
        TextMixin.__init__(self,*args,**kws)

class Frame(ParentMixin):

    _gets_focus = 0
    texty = 0
    text = ""

    def __init__(self,*args,**kws):
        ParentMixin.__init__(self,*args,**kws)

class Window(ParentMixin):
    """To move or resize a window, use Esc-W to open
the window menu, then type h,j,k, or l to move, and
H,J,K, or L to resize."""

    _needs_parent = 0
    texty = 0
    _use_text = 0
    menu = {}

    def __init__(self,title="Window",*args,**kws):
        ParentMixin.__init__(self,*args,**kws)
        self.set_title(title)
        #_app.add(self)
        #self.modify(text="")
        ##_scr.dbg("%s:%s"%(self.title,self.geometry))

    def destroy(self):
        if not self._created: return
        #_scr.dbg("Destroyeing %s"%self)
        ParentMixin.destroy(self)
        _app.remove(self)

    def move_to_top(self):
        _app.move_to_top(self)

    def redraw(self):
        if not self._created: return
        ParentMixin.redraw(self)
        self.addstr(2,0,self.title)

    def set_title(self,title):
        self.title = title

    def present_appmenu(self,ev):
        """Open application menu"""
        x,y = self.x,self.y
        w,h = self.width,int(round(3.1/self._vert_scale))
        self._amenu = WinMenuWindow(title="?Window")
        self._amenu._pwin = self
        self._amenu.x=x
        self._amenu.y=y
        self._amenu.width=w
        self._amenu.height=h
        self._amenu._gets_focus=0

    def present_winmenu(self,ev):
        """Open window menu"""
        x,y = self.x,self.y
        w,h = int(round(12.1/self._horiz_scale)),int(round(4.1/self._vert_scale))
        self._omenu = WinMenuWindow(title="?Window")
        self._omenu._pwin = self
        self._omenu.x=x
        self._omenu.y=y
        self._omenu.width=w
        self._omenu.height=h
        self._omenu._gets_focus=0

        x,y = int(round(1.1/self._horiz_scale)),int(round(1.1/self._vert_scale))
        w,h = int(round(10.1/self._horiz_scale)),int(round(1.1/self._vert_scale))
        self._canbtn = MenuButton(parent=self._omenu,geometry=(x,y,w,h),text="Cancel",command=self.cancelclose)
        self._omenu.add(self._canbtn)

        x,y = int(round(1.1/self._horiz_scale)),int(round(2.1/self._vert_scale))
        self._clbtn = MenuButton(parent=self._omenu,geometry=(x,y,w,h),text="Close",command=self.close)
        self._omenu.add(self._clbtn)

        _app.add(self._omenu)
        self._omenu.set_focus_capture(1)
        
    _event_map = {WINMENU_EVENT:present_winmenu,
                  APPMENU_EVENT:present_appmenu}

    def handle_wm_event(self,ch):
        hinc = int(round(1.1/self._horiz_scale))
        vinc = int(round(1.1/self._vert_scale))
        
        if ch == ord('h'):
            self.x -= hinc
            self._omenu.x -= hinc
            return 1
        if ch == ord('l'):
            self.x += hinc
            self._omenu.x += hinc
            return 1
        if ch == ord('j'):
            self.y += vinc
            self._omenu.y += vinc
            return 1
        if ch == ord('k'):
            self.y -= vinc
            self._omenu.y -= vinc
            return 1

        if ch == ord('H'):
            self.width -= hinc
            self.curs_resized(-hinc,0)
            return 1
        if ch == ord('L'):
            self.width += hinc
            self.curs_resized(hinc,0)
            return 1
        if ch == ord('J'):
            self.height += vinc
            self.curs_resized(0,vinc)
            return 1
        if ch == ord('K'):
            self.height -= vinc
            self.curs_resized(0,-vinc)
            return 1
        return 0

    def close(self,*args,**kws):
        ##_scr.dbg("CLOSING %s"%self)
        self._omenu._pwin = None
        self._omenu.destroy()
        self.destroy()

    def cancelclose(self,*args,**kws):
        self._omenu.destroy()
        self.set_focus(1)

    def setMenu(self,menu):
        self.menu=menu

class WinMenuWindow(Window):

    _gets_focus = 0

    def handle_wmove_event(self,ev):
        """Move the window."""
        #_scr.dbg("MOVE",chr(ev))
        return self._pwin.handle_wm_event(ev)

    def handle_wconfig_event(self,ev):
        """Resize the window."""
        #_scr.dbg("RESIZE",chr(ev))
        return self._pwin.handle_wm_event(ev)

    _event_map = {ord('h'):handle_wmove_event,
                  ord('j'):handle_wmove_event,
                  ord('k'):handle_wmove_event,
                  ord('l'):handle_wmove_event,
                  ord('H'):handle_wconfig_event,
                  ord('J'):handle_wconfig_event,
                  ord('K'):handle_wconfig_event,
                  ord('L'):handle_wconfig_event,
                  }

class MenuButton(Button):

    texty = 0

    def __init__(self,*args,**kws):
        Button.__init__(self,*args,**kws)
        self._LLCORNER = ord('<')
        self._LRCORNER = ord('>')
        self._UHLINE = ' '
        self._LHLINE = ' '

class HelpWindow(Window):

    def __init__(self,*args,**kws):
        Window.__init__(self,*args,**kws)
        self._prev_ctrl = _focus_control
        self._prev_focus_capture = _focus_capture_control
        self.title = "INFORMATION (press 'Q' to dismiss)"
        self.x=0
        self.y=0
        self.width=600
        self.height=400
        lb = ListBox(parent=self,geometry=(10,10,580,380))
        self.populate_lb(lb)
        _app.add(self)
        self.set_focus_capture(1)

    def populate_lb(self,lb):
        """Add docstrings for _prev_ctrl event handlers to lb."""
        items = ["---------------------------------------------------------------------",
                 "This is txtgui, the text/curses binding for Manygui.",
                 ""]
        if self._prev_ctrl:
            cls = self._prev_ctrl.__class__.__name__
            items += ["The current control is a "+cls+".",""]
            items += self._prev_ctrl.get_control_help().split('\n')
            items += ["","This " + cls +" responds to the following key bindings:",""]
            items += self._prev_ctrl.get_event_help()
        items += ["You can get this context-sensitive help screen at",
                  "any time by typing ESC-?. You can exit the",
                  "application by typing ESC, followed by the word",
                  "'quit' in lower-case, or by closing all the",
                  "application's windows.",
                  
                  "",
                  
                  "The main difference between the curses binding and",
                  "the text binding is that curses responds to characters",
                  "as soon as they are typed, whereas if the text binding is",
                  "used, you must press the <Return> key in order for",
                  "the application to respond to input. You may type",
                  "ESC-m if you need to send a return character",
                  "to the application.",

                  "",
                  
                  "ESC-f and ESC-b move forward and backward, respectively,",
                  "among the application's controls. Up and down arrow",
                  "move between controls, except in text controls,",
                  "where they move between lines. Z and z can be used",
                  "to zoom the presentation in and out. ESC-arrows",
                  "may be used to scroll the entire screen.",
                  
                  "",

                  "Some terminal emulation programs may not display the",
                  "borders of windows properly when using curses. If",
                  "borders are drawn using strange characters, set",
                  "the environment variable ANYGUI_ALTERNATE_BORDER",
                  "to a non-zero value."
                  
                  ]
        lb.items = items

    def dismiss(self,ev):
        """Exit help and return to the previous window."""
        self.set_focus_capture(0)
        self.destroy()
        if self._prev_focus_capture:
            self._prev_focus_capture.set_focus_capture(1)
        if self._prev_ctrl:
            self._prev_ctrl.set_focus(1)

    #def event_handler(self,ev):
    #    if ev == ord('q'): self.dismiss(ev)

    _event_map = {ord('q'):dismiss,
                  ord('Q'):dismiss,}

# If false, present an initial help window.
_inithelp = 1

# Character escape sequences, and the events we transform them
# into.
_escape_sequence_map = {
    (LEFT_BRACKET,65):UP_ARROW,
    (LEFT_BRACKET,66):DOWN_ARROW,
    (LEFT_BRACKET,67):RIGHT_ARROW,
    (LEFT_BRACKET,68):LEFT_ARROW,

    (LEFT_ARROW,):SCROLL_LEFT,
    (RIGHT_ARROW,):SCROLL_RIGHT,
    (UP_ARROW,):SCROLL_UP,
    (DOWN_ARROW,):SCROLL_DOWN,

    (ord('?'),):HELP_EVENT,

    (ord('q'),ord('u'),ord('i'),ord('t')):QUIT_EVENT,

    (ord('r'),):REFRESH_EVENT,

    (ord('w'),):WINMENU_EVENT,

    (ord('f'),):FOCUS_FORWARD_EVENT,
    (ord('b'),):FOCUS_BACKWARD_EVENT,
    (9,):FOCUS_BACKWARD_EVENT,

    # Convert ESC-m into Return, for textgui's benefit.
    (ord('m'),):ord('\n'),

    (ord('s'),):SELECT_BEGIN_EVENT,
    (ord('e'),):SELECT_END_EVENT,

    }

for seq in list(_escape_sequence_map.keys()):
    for i in range(1,len(seq)):
        _escape_sequence_map[seq[:i]] = None

class Application:
    def __init__(self):
        self._windows = []
        self._quit = 0
        _scr.scr_init()
        set_scale(_scr._xsize,_scr._ysize)
        global _app
        _app = self

    def remove(self,win):
        ##_scr.dbg("WINDOW DELETED")
        try:
            self._windows.remove(win)
        except ValueError:
            pass
        #_scr.dbg("removed %s, now %s"%(win,self._windows))
        if not self._windows:
            self._quit = 1
        else:
            refresh_all()
            self.change_focus()

    def add(self,win):
        #_scr.dbg("adding",win)
        self._windows.append(win)
        #_scr.dbg("\tcreating")
        win.create()
        #_scr.dbg("\trefreshing")
        refresh_all()

    def run(self):
        for w in self._windows:
            #_scr.dbg("creating",w)
            w.create()
        try:
            #_scr.dbg("txt mainloop")
            self.mainloop()
        except:
            # In the event of an error, restore the terminal
            # to a sane state.
            _scr.scr_quit()

            # Pass the exception upwards
            (exc_type, exc_value, exc_traceback) = sys.exc_info()
            if hasattr(exc_value,"value"):
                print("Exception value:",exc_value.value)
            raise exc_type(exc_value).with_traceback(exc_traceback)
        else:
            # In the event of an error, restore the terminal
            # to a sane state.
            _scr.scr_quit()
            
    def mainloop(self):
        # Present the initial help screen, without which the
        # UI remains forever mysterious.
        global _inithelp
        if not _inithelp and not os.getenv('ANYGUI_CURSES_NOHELP', 0):
            HelpWindow()
            _inithelp = 1

        # Establish the initial focus.
        self.change_focus()

        # Redraw the screen.
        refresh_all()
        self.redraw_all()

        # The main event loop:
        while (not self._quit) and self.check_for_events():
            self.redraw_all()

    def appevent_handler(self,ch):
        #_scr.dbg("APPEVENT_HANDLER",ch)
        if ch == HELP_EVENT: # ESC-?
            HelpWindow()
        if ch == QUIT_EVENT: # ESC-quit
            wins = self._windows[:]
            for win in wins:
                win.destroy()
            return 0
        if ch == FOCUS_FORWARD_EVENT or ch == DOWN_ARROW or ch == 9:  # ^F,down,tab
            self.change_focus(1)
        if ch == FOCUS_BACKWARD_EVENT or ch == UP_ARROW:  # ^B,up
            self.change_focus(-1)
        if ch == REFRESH_EVENT:
            refresh_all()
        if ch == SCROLL_LEFT:
            ox,oy = _scr.get_origin()
            ox-=10
            _scr.set_origin(ox,oy)
            refresh_all()
        if ch == SCROLL_RIGHT:
            ox,oy = _scr.get_origin()
            ox+=10
            _scr.set_origin(ox,oy)
            refresh_all()
        if ch == SCROLL_UP:
            ox,oy = _scr.get_origin()
            oy-=10
            _scr.set_origin(ox,oy)
            refresh_all()
        if ch == SCROLL_DOWN:
            ox,oy = _scr.get_origin()
            oy+=10
            _scr.set_origin(ox,oy)
            refresh_all()

        if ch == ord('z'):
            ComponentMixin._horiz_scale /= 2.0
            ComponentMixin._vert_scale /= 2.0
            refresh_all()
        
        if ch == ord('Z'):
            ComponentMixin._horiz_scale *= 2.0
            ComponentMixin._vert_scale *= 2.0
            refresh_all()
        
        return 1

    def translate_escape(self,ch):
        if ch != ESCAPE:
            return ch
        done=0
        chtuple=()
        while not done:
            ch = self.translate_escape(_scr.get_char())
            try:
                chtuple = chtuple + (ch,)
                result = _escape_sequence_map[chtuple]
                if type(result) == type(0):
                    return result
            except:
                # Invalid escape sequence.
                return ch

    def check_for_events(self):
        #_scr.dbg("Checking for events...")
        ch = _scr.get_char()
        ch = self.translate_escape(ch)
        #_scr.dbg("GOT:",ch)
        handled = 0
        if _focus_control is not None:
            handled = _focus_control.handle_event(ch)
        if not handled:
            return self.appevent_handler(ch)
        return 1

    def redraw_all(self):
        global refresh_all_flag
        if refresh_all_flag:
            _scr.erase_all()
            for win in self._windows:
                win.redraw()
            refresh_all_flag = 0
        ##_scr.dbg("redraw_all: %s"%self._windows)
        try:
            self._windows[-1].redraw()
        except IndexError:
            pass
        self.ensure_focus()
        _scr.refresh()

    def change_focus(self,dir=1):
        #_scr.dbg("**** CHANGING FOCUS",dir)
        global _focus_dir
        _focus_dir = dir
        
        # If no focus, establish focus.
        if not _focus_control:
            for win in _all_components:
                win.set_focus(1)
                if _focus_control:
                    self.raise_focus_window()
                    return
            #_scr.dbg("NOFOCUS: FOCUS NOW ON",_focus_control,"\n")
            return
        
        # Move focus to the next control that can accept it.
        aclen = len(_all_components)
        #_scr.dbg("aclen:",aclen)
        tried = 0

        fc = _focus_control
        ii = _all_components.index(fc)
        discard_focus()

        while not _focus_control and tried <= aclen:
            tried += 1
            ii += dir
            if ii>=aclen: ii = 0
            if ii<0: ii = aclen-1
            _all_components[ii].set_focus(1)

        #_scr.dbg("FOCUS NOW ON",_focus_control,"\n")
        self.raise_focus_window()

    #def window_lost_focus(self,win):
    #    try:
    #        ii = self._windows.index(win)
    #        ii += 1
    #        if ii >= len(self._windows):
    #            ii = 0
    #    except ValueError:
    #        ii = 0
    #    try:
    #        self._windows[ii].set_focus(1)
    #    except IndexError:
    #        self._quit = 1

    def ensure_focus(self):
        for win in self._windows:
            win.ensure_focus()

    def raise_focus_window(self):
        if not _focus_control: return
        for win in self._windows:
            if contains(win,_focus_control):
                self.move_to_top(win)

    def move_to_top(self,win):
        if self._windows[-1] == win: return
        self._windows.remove(win)
        self._windows.append(win)
        refresh_all()

def hi(ctl):
    l.set_text("Pushed!")

def hi2(ctl,val):
    if ctl.on:
        l.set_text("%d Checked!"%val)
    else:
        l.set_text("%d UnChecked!"%val)

def hi3(ctl,value):
    w2.set_title("Radio choics %s"%ctl.value)

def sel(ctl,idx,item): l.set_text("%d %s"%(idx,item))

def showHide(*args,**kws):
    if fr.visible:
        fr.visible = 0
    else:
        fr.visible = 1

def showHide2(*args,**kws):
    if fr2.visible:
        fr2.visible = 0
    else:
        fr2.visible = 1

def showHide3(*args,**kws):
    if fr3.visible:
        fr3.visible = 0
    else:
        fr3.visible = 1


if __name__ == "__main__":
    from . import scr_curses
    global _scr
    _scr = scr_curses
    app = Application()
    win = Window(geometry=(0,0,450,300))
    app.add(win)
    num = 3
    bns = [Button(geometry=((10+i*90),10,80,25), text='Frame %s' % i ) for i in range(num)]
    for btn in bns:
        win.add(btn)
    fms = [Frame(geometry=(10,45,420,230), visible=0) for i in range(num)]
    n = 0
    for frm, i in zip(fms,list(range(num))):
        lbl = Label(text='This is Frame number %s.' % i, geometry=(30, 30, 200, 30))
        btn = Button(text = 'A button',geometry=(230,30,100,40))
    
        frm1 = Frame(geometry = (20,60,150,150))
        
        lbl1 = Label(text="Subframe %d"%n,geometry = (30, 30, 100, 30))
        n += 1
        
        btn1 = Button(text="A button %d"%n,geometry=(30,70,100,40))
        frm1.add(lbl1)
        frm1.add(btn1)
    
        frm2 = Frame(geometry = (250,60,150,150))
        lbl2 = Label(text="Subframe %d"%n,geometry = (10, 10, 100, 30))
        n += 1
        btn2 = Button(text="A button %d"%n,geometry=(30,70,100,40))
        frm2.add(lbl2)
        frm2.add(btn2)
    
        frm.add(lbl)
        frm.add(btn)
        frm.add(frm1)
        frm.add(frm2)
        win.add(frm)
    callbacks = []
    for i in range(num):
        def callback(event,i=i,*args,**kws): # Store the index
            for j in range(num):
                if j!=i:
                    fms[j].visible = 0
                    log('Frame %s hidden' % j)
                else:
                    fms[j].visible = 1
                    log('Frame %s shown' % j)
        callbacks.append(callback)
    for i in range(num):
        bns[i].command =  callbacks[i]
    app.run()

#if __name__ == "__main__":
#
#    import scr_curses as sc
#    global scr_,fr
#    _scr = sc
#
#    # Create an Application.
#    global _app
#    Application()
#    w = Window(geometry=(10,10,500,400))
#    global l
#    l = Label(parent=w,geometry=(100,40,300,60),text="Hello, world!",border=1)
#    b = Button(parent=w,geometry=(100,100,300,60),text="Push me",command=hi)
#    lb = ListBox(parent=w,geometry=(100,160,300,60),items=[1,2,3,4,5],command=sel)
#    cb = CheckBox(parent=w,geometry=(100,220,300,60),value=0,command=hi2)
#    global w2
#    w2 = Window(geometry=(50,50,500,480))
#    fr = Frame(parent=w2,geometry=(40,60,300,130))
#
#    fr2 = Frame(parent=w2,geometry=(40,60,300,130),text="Frame 2")
#    fr22 = Frame(parent=fr2,geometry=(10,40,100,80),text="Frame 22")
#    fr22lbl = Label(parent=fr22,text="Sub-frame",geometry=(10,10,70,60))
#
#    fr3 = Frame(parent=w2,geometry=(40,60,300,130),text="Frame 2")
#    fr33 = Frame(parent=fr3,geometry=(10,40,100,80),text="Frame 3")
#    fr33lbl = Label(parent=fr33,text="Sub-frame",geometry=(10,10,70,60))
#
#    shbtn = Button(parent=w2,geometry=(360,60,100,60),text="Hide",command=showHide)
#    shbtn2 = Button(parent=w2,geometry=(360,130,100,60),text="Hide2",command=showHide2)
#    shbtn2 = Button(parent=w2,geometry=(360,200,100,60),text="Hide2",command=showHide3)
#
#    rb1 = RadioButton(parent=fr,geometry=(40,30,200,40),text="Choice 1",command=hi3,value=1)
#    rb2 = RadioButton(parent=fr,geometry=(40,70,200,40),text="Choice 2",command=hi3,value=2)
#    te = TextField(parent=w2,geometry=(40,180,300,80),text="Edit me")
#    ta = TextArea(parent=w2,geometry=(40,250,300,220),text="Edit me")
#    _app.add(w)
#    _app.add(w2)
#    _app.run()
