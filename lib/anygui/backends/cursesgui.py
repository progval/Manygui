from anygui.backends import *
__all__ = anygui.__all__

from curses import *

_f = open("curses.txt","w")
_debug_messages = 0

def dbg(msg):
    if not _debug_messages: return
    _f.write(msg+"\n")
    _f.flush()

_scr = None
_refresh_all = 0
def _add(x,y,ch):
    _scr.addch(y,x,ch)
def _erase(x,y,w,h):
    for xx in range(x,x+w):
        for yy in range(y,y+h):
            _add(xx,yy,' ')        

class ComponentMixin:
    """ Mixin class for components.
    We're really only using curses as a screen-addressing
    library, since its implementation of "windows" isn't
    really very much like a GUI window. """

    # We'll map coordinates according to these scaling factors.
    # This lets normal anygui programs run under curses without
    # having to scroll the screen. This might not be such a
    # good idea, but it's worth a try.
    #_horiz_scale = 80.0/640.0
    #_vert_scale = 24.0/480.0
    _horiz_scale = 1.0
    _vert_scale = 1.0

    # If true for a particular class or component, we'll draw
    # a border around the component when it's displayed.
    _border = 1 # For debugging.
    _visible = 1
    _needs_container = 0

    def __init__(self,*args,**kws):
        dbg("Creating %s"%self)
        self._created = 0

    def _scale_xy(self,x,y):
        return (int(x*self._horiz_scale),int(y*self._vert_scale))
    def _scale_yx(self,y,x):
        nx,ny = self._scale_xy(x,y)
        return ny,nx

    def _get_screen_coords(self):
        if not self._created: return 0,0
        #if self._needs_container and not self._container: return 0,0
        x,y = self._scale_xy(self.x,self.y)
        if not self._container:
            return x,y
        cx,cy = self._container._get_screen_coords()
        return x+cx, y+cy

    def _container_intersect(self,x,y,w,h):
        # Get the screen rectangle representing the intersection of
        # the component and its container.
        if not self._created: return 0,0,0,0
        #if self._needs_container and not self._container: return 0,0,0,0
        if not self._container:
            return x,y,w,h
        cx,cy,cw,ch = self._container._get_bounding_rect()
        ix = max(x,cx)
        iy = max(y,cy)
        ix2 = min(x+w,cx+cw)
        iy2 = min(y+h,cy+ch)
        iw = ix2-ix
        ih = iy2-iy
        if iw<0: iw=0
        if ih<0: ih=0
        return ix,iy,iw,ih

    def _get_bounding_rect(self):
        # Get the screen x,y,w,h of the visible portion of the component.
        # If the control is invisible or completely clipped, w and h
        # are both 0.
        if not self._visible or not self._created:
            return 0,0,0,0
        x,y = self._get_screen_coords()
        w,h = self._scale_xy(self.width,self.height)
        x,y,w,h = self._container_intersect(x,y,w,h)
        return x,y,w,h

    def _redraw(self):
        dbg("Redrawing %s"%self)
        if not self._created: return
        dbg("Visible: %s"%self)
        if self.visible:
            self._erase()
            self._draw_border()
            self._draw_contents()

    def _erase(self):
        if not self._created: return
        x,y,w,h = self._get_bounding_rect()
        _erase(x,y,w,h)

    def _draw_border(self):
        if not self._created: return
        if not self._border: return
        x,y = self._get_screen_coords()
        w,h = self._scale_xy(self.width,self.height)
        dbg("Screen coords %s for %s"%((x,y,w,h),self))
        x,y,w,h = self._container_intersect(x,y,w,h)
        dbg("Container intersect %s for %s"%((x,y,w,h),self))
        _add(x,y,'+')
        _add(x+w-1,y,'+')
        _add(x,y+h-1,'+')
        _add(x+w-1,y+h-1,'+')
        for xx in range(x+1,x+w-1):
            _add(xx,y,'-')
            _add(xx,y+h-1,'-')
        for yy in range(y+1,y+h-1):
            _add(x,yy,'|')
            _add(x+w-1,yy,'|')

    def _draw_contents(self):
        if not self._created: return
        pass

    # backend api

    def _is_created(self):
        return self._created

    def _ensure_created(self):
        dbg("_ensure_created(): %s"%self)
        if self._needs_container and not self._container:
            return 0
        self._created = 1
        return 1

    def _ensure_geometry(self):
        self._redraw()

    def _ensure_visibility(self):
        self._redraw()

    def _ensure_enabled_state(self):
        pass

    def _ensure_destroyed(self):
        self._erase()
        self._created = 0

    def _ensure_events(self):
        pass

class Label(ComponentMixin, AbstractLabel):
    pass

class ListBox(ComponentMixin, AbstractListBox):
    pass

class Button(ComponentMixin, AbstractButton):
    pass

#class CheckBox(ToggleButtonMixin, AbstractCheckBox):
#    pass
#
#class RadioButton(ToggleButtonMixin, AbstractRadioButton):
#    pass

class CheckBox:
    pass

class RadioButton:
    pass

class DisabledTextBindings: pass

class TextField(ComponentMixin, AbstractTextField, DisabledTextBindings):
    pass

class TextArea(ComponentMixin, AbstractTextArea, DisabledTextBindings):
    pass

class Frame(ComponentMixin, AbstractFrame):

    def __init__(self,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        AbstractFrame.__init__(self,*args,**kws)

    def _redraw(self):
        ComponentMixin._redraw(self)
        for comp in self._contents:
            comp._redraw()

    def _ensure_destroyed(self):
        for comp in self._contents:
            comp._ensure_destroyed()
        self._erase()
        self._created = 0

class Window(ComponentMixin, AbstractWindow):

    _needs_container = 0

    def __init__(self,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        AbstractWindow.__init__(self,*args,**kws)

    def _redraw(self):
        ComponentMixin._redraw(self)
        for comp in self._contents:
            comp._redraw()

    def _ensure_destroyed(self):
        for comp in self._contents:
            comp._ensure_destroyed()
        self._erase()
        self._created = 0

class Application(AbstractApplication):
    def __init__(self):
        AbstractApplication.__init__(self)
        global _scr
        _scr = initscr()
        noecho()
        cbreak()
        _app = self

    def _window_deleted(self):
        if not self._windows:
            echo()
            nocbreak()
            nodelay(0)
            endwin()
    
    def _mainloop(self):
        self._redraw_all()
        while self._check_for_events():
            self._redraw_all()
        echo()
        nocbreak()
        endwin()

    def _check_for_events(self):
        ch = _scr.getch()
        if ch == ord('q'):
            return 0
        return 1

    def _redraw_all(self):
        global _refresh_all
        if _refresh_all:
            _refresh_all = 0
            _scr.erase()
        dbg("redraw_all: %s"%self._windows)
        for win in self._windows:
            win._redraw()
        _scr.refresh()
