from anygui.backends import *
from anygui.Exceptions import Error
__all__ = anygui.__all__

import sys
import curses
from curses import *

_f = open("curses.txt","w")
_debug_messages = 1

def dbg(msg):
    if not _debug_messages: return
    _f.write(msg+"\n")
    _f.flush()

class CursesGUIException(Error):

    def __init__(self,**kws):
        self.__dict__.update(kws)

# Curses magic...
_scr = None
_refresh_all = 0
_focus_control = None
def _addstr(x,y,ch,n=0,attr=curses.A_NORMAL):
    #dbg("adding at %s,%s: <%s>"%(x,y,ch))
    try:
        if n != 0:
            _scr.addnstr(y,x,ch,n,attr)
        else:
            _scr.addstr(y,x,ch,attr)
    except:
        raise CursesGUIException(value="addstr/addnstr error: %d,%d <- \"%s\""%(x,y,ch))
def _erase(x,y,w,h):
    #dbg("Erasing %s,%s,%s,%s"%(x,y,w,h))
    for xx in range(x,x+w):
        for yy in range(y,y+h):
            _addstr(xx,yy,' ')        

# Global list of all created components. Used for
# focus management.
_all_components = []
def _discard_focus():
    for comp in _all_components:
        comp._focus = 0

class ComponentMixin:
    """ Mixin class for components.
    We're really only using curses as a screen-addressing
    library, since its implementation of "windows" isn't
    really very much like a GUI window. """

    # We'll map coordinates according to these scaling factors.
    # This lets normal anygui programs run under curses without
    # having to scroll the screen. This might not be such a
    # good idea, but it's worth a try.
    _horiz_scale = 80.0/800.0
    _vert_scale = 24.0/600.0
    #_horiz_scale = 1.0
    #_vert_scale = 1.0
    _attr = curses.A_NORMAL

    # If true for a particular class or component, we'll draw
    # a border around the component when it's displayed.
    _border = 1 # For debugging.
    _visible = 1
    _needs_container = 0
    _title = "curses"
    _gets_focus = 1
    _text = "curses"
    _textx = 1
    _texty = 1

    # Border characters:
    def __init__(self,*args,**kws):
        #dbg("Creating %s"%self)
        self._curses_created = 0
        self._focus = 0
        self._focus_capture = 0
        self._cpos = 1,1 # Cursor position when in focus.
        self._LVLINE = curses.ACS_VLINE
        self._RVLINE = curses.ACS_VLINE
        self._UHLINE = curses.ACS_HLINE
        self._LHLINE = curses.ACS_HLINE
        self._ULCORNER = curses.ACS_ULCORNER
        self._URCORNER = curses.ACS_URCORNER
        self._LLCORNER = curses.ACS_LLCORNER
        self._LRCORNER = curses.ACS_LRCORNER

    def _set_focus(self,val):
        if val:
            # Remove focus from all other components.
            _discard_focus()
            # Give focus to self and container heirarchy.
            self._focus = 1
            if self._container:
                self._container._acquire_focus()

    def _set_focus_capture(self,val):
        if val:
            _discard_focus()
            self._change_focus()

    def _scale_xy(self,x,y):
        return (int(x*self._horiz_scale),int(y*self._vert_scale))
    def _scale_yx(self,y,x):
        nx,ny = self._scale_xy(x,y)
        return ny,nx

    def _get_screen_coords(self):
        if not self._curses_created: return 0,0
        #if self._needs_container and not self._container: return 0,0
        x,y = self._scale_xy(self.x,self.y)
        #dbg("_gsc: %s,%s: %s"%(x,y,self._text))
        if not self._container:
            return x,y
        cx,cy = self._container._get_screen_coords()
        return x+cx, y+cy

    def _container_intersect(self,x,y,w,h):
        # Get the screen rectangle representing the intersection of
        # the component and its container.
        if not self._curses_created: return 0,0,0,0
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
        #dbg("_container_intersect (%s,%s) %s,%s,%s,%s: %s"%(x,y,ix,iy,iw,ih,self))
        return ix,iy,iw,ih

    def _addstr(self,x,y,str,attr=0):
        if attr == 0:
            attr = self._attr
        sx,sy,w,h = self._get_bounding_rect()
        if y>=h: return
        x += sx
        y += sy
        _addstr(x,y,str,sx+w-x,attr)

    def _get_bounding_rect(self):
        # Get the screen x,y,w,h of the visible portion of the component.
        # If the control is invisible or completely clipped, w and h
        # are both 0.
        if not self._visible or not self._curses_created:
            return 0,0,0,0
        x,y = self._get_screen_coords()
        #dbg("%s,%s: %s"%(x,y,self))
        w,h = self._scale_xy(self.width,self.height)
        x,y,w,h = self._container_intersect(x,y,w,h)
        return x,y,w,h

    def _redraw(self):
        #dbg("Redrawing (%d) %s"%(self.refresh,self))
        if not self._curses_created: return
        #dbg("Visible: %s"%self)
        if self._visible:
            self._erase()
            self._draw_border()
            self._draw_contents()
            self._addstr(self._textx,self._texty,self._text)

    def _erase(self):
        if not self._curses_created: return
        x,y,w,h = self._get_bounding_rect()
        #dbg("Erasing %s"%self)
        _erase(x,y,w,h)

    def _draw_border(self):
        if not self._curses_created: return
        if not self._border: return
        x,y = self._get_screen_coords()
        w,h = self._scale_xy(self.width,self.height)
        #dbg("Screen coords %s for %s"%((x,y,w,h),self))
        x,y,w,h = self._container_intersect(x,y,w,h)
        if w == 0 or h == 0: return
        #dbg("Container intersect %s for %s"%((x,y,w,h),self))
        _scr.addch(y,x,self._ULCORNER)
        _scr.addch(y,x+w-1,self._URCORNER)
        _scr.addch(y+h-1,x,self._LLCORNER)
        _scr.addch(y+h-1,x+w-1,self._LRCORNER)
        for xx in range(x+1,x+w-1):
            _scr.addch(y,xx,self._UHLINE)
            _scr.addch(y+h-1,xx,self._LHLINE)
        for yy in range(y+1,y+h-1):
            _scr.addch(yy,x,self._LVLINE)
            _scr.addch(yy,x+w-1,self._RVLINE)

    def _draw_contents(self):
        if not self._curses_created: return
        pass

    def _change_focus(self):
        dbg("Changing focus on %s"%self)
        x,y,w,h = self._get_bounding_rect()
        if w == 0 or h == 0:
            self._focus = 0
            return
        if not self._gets_focus:
            return
        if not self._focus:
            dbg("   gained focus!")
            self.focus = 1
        else:
            if self._focus_capture: return
            #dbg("   lost focus!")
            self._focus = 0

    def _ensure_focus(self):
        if not self._curses_created: return
        x,y = self._get_screen_coords()
        #dbg("Ensuring focus %s,%s on %s"%(x,y,self))
        if self._focus:
            #dbg("   HAS FOCUS!")
            _scr.move(y+self._texty,x+self._textx)
            global _focus_control
            _focus_control = self

    def _handle_event(self,ev):
        handled = self._event_handler(ev)
        if handled: return 1
        if self._container:
            # Propagate unhandled events to container.
            return self._container._handle_event(ev)
        return 0

    def _event_handler(self,ev):
        return 0

    # backend api

    def _is_created(self):
        return self._curses_created

    def _ensure_created(self):
        #dbg("_ensure_created(): %s"%self)
        if self._curses_created:
            return 0
        if self._needs_container and not self._container:
            return 0
        self._curses_created = 1
        global _all_components
        _all_components.append(self)
        return 1

    def _ensure_geometry(self):
        self._redraw()

    def _ensure_visibility(self):
        self._redraw()

    def _ensure_enabled_state(self):
        self._redraw()

    def _ensure_destroyed(self):
        #dbg("Ensuring destroyed: %s"%self)
        self._erase()
        self._curses_created = 0
        global _all_components
        _all_components.remove(self)

    def _ensure_events(self):
        pass

    def _ensure_text(self):
        self._redraw()

class Label(ComponentMixin, AbstractLabel):

    _gets_focus = 0
    _texty = 0

    def __init__(self,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        AbstractLabel.__init__(self,*args,**kws)
        self._LVLINE = ord(' ')
        self._RVLINE = ord(' ')
        self._UHLINE = ord(' ')
        self._LHLINE = ord(' ')
        self._ULCORNER = ord(' ')
        self._URCORNER = ord(' ')
        self._LLCORNER = ord(' ')
        self._LRCORNER = ord(' ')

class ListBox(ComponentMixin, AbstractListBox):
    pass

class Button(ComponentMixin, AbstractButton):

    _texty = 0
    _attr = curses.A_UNDERLINE

    def __init__(self,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        AbstractButton.__init__(self,*args,**kws)
        self._LVLINE = ord('<')
        self._RVLINE = ord('>')
        self._UHLINE = ord(' ')
        self._LHLINE = ord(' ')
        self._ULCORNER = ord('<')
        self._URCORNER = ord('>')
        self._LLCORNER = ord('<')
        self._LRCORNER = ord('>')


    def __str__(self): return "Button "+self._text

    def _event_handler(self,ev):
        if ev == ' ':
            send(self, 'click')
            return 1
        return 0

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

class ContainerMixin(ComponentMixin):

    def __init__(self,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)

    def _redraw(self):
        if not self._curses_created: return
        ComponentMixin._redraw(self)
        for comp in self._contents:
            comp._redraw()

    def _ensure_destroyed(self):
        for comp in self._contents:
            comp._ensure_destroyed()
        self._erase()
        self._curses_created = 0

    def _change_focus(self):
        #dbg("Changing CONTAINER focus on %s"%self)
        if not self._contents:
            #dbg("   empty...")
            return
        if not self._focus:
            #dbg("   new focus...")
            self._focus = 1
        self._contents[self._focus-1]._change_focus()
        #dbg("   moving focus...")
        done = 0
        while not done:
            if not self._contents[self._focus-1]._focus:
                self._focus += 1
                if self._focus-1 >= len(self._contents):
                    #dbg("   focus lost...")
                    if self._focus_capture:
                        self._contents[0]._change_focus()
                        return
                    else:
                        self._focus = 0
                        return
                else:
                    #dbg("   focus moved...")
                    self._contents[self._focus-1]._change_focus()
            else:
                done = 1

    def _acquire_focus(self):
        for nn in range(len(self._contents)):
            if self._contents[nn]._focus:
                self._focus = nn+1
                break
        else:
            self._focus = 0
        if self._container:
            self._container._acquire_focus()

    def _ensure_focus(self):
        #dbg("Ensuring focus in %s"%self)
        if not self._contents:
            ComponentMixin._ensure_focus(self)
        for win in self._contents:
            win._ensure_focus()

    def _remove(self, comp):
        # Curses components MUST have a valid container
        # in order to destroy themselves. Since the
        # comp.destroy() call in Frame._remove() dissociates
        # the component from the container, we must
        # override Frame._remove().
        try:
            self._contents.remove(comp)

            # Fix the focus.
            if comp._focus:
                if self._contents:
                    _discard_focus()
                    self._contents[0]._change_focus()
                else:
                    self._acquire_focus()

            comp._ensure_destroyed()
            comp._set_container(None)

            #dbg("Refreshing %s"%self)
            self._redraw()
        except ValueError:
            pass

class Frame(ContainerMixin, AbstractFrame):

    def __init__(self,*args,**kws):
        ContainerMixin.__init__(self,*args,**kws)
        AbstractFrame.__init__(self,*args,**kws)
        self._text = ""

class Window(ContainerMixin, AbstractWindow):

    _needs_container = 0

    def __init__(self,*args,**kws):
        ContainerMixin.__init__(self,*args,**kws)
        AbstractWindow.__init__(self,*args,**kws)
        self._text = ""
        #dbg("%s:%s"%(self._title,self.geometry))

    def _redraw(self):
        if not self._curses_created: return
        ContainerMixin._redraw(self)
        self._addstr(2,0,self._title)

    def _ensure_title(self): self._redraw()

    def _present_winmenu(self):
        x,y = 0,int(round(1.0/self._vert_scale))
        w,h = int(10.0/self._horiz_scale),int(4.0/self._vert_scale)
        self._omenu = Frame(geometry=(x,y,w,h))
        self.add(self._omenu)
        x,y = int(1.0/self._horiz_scale),int(1.0/self._vert_scale)
        w,h = int(8.0/self._horiz_scale),int(4.0/self._vert_scale)
        self._clbtn = Button(geometry=(x,y,w,h),text="Close")
        self._omenu.add(self._clbtn)
        link(self._clbtn,self._close)

        x,y = int(1.0/self._horiz_scale),int(2.0/self._vert_scale)
        self._canbtn = Button(geometry=(x,y,w,h),text="Cancel")
        self._omenu.add(self._canbtn)

        self._omenu.focus_capture = 1
        
        link(self._canbtn,self._cancel_close)

        self._redraw()
        self._omenu._redraw()


    def _event_handler(self,ch):
        # Handle the ^Option command by popping up a
        # window menu.
        if ord(ch) == 15:
            self._present_winmenu()
            return 1

    def _close(self,*args,**kws):
        dbg("CLOSING %s"%self)
        self.destroy()

    def _cancel_close(self,*args,**kws):
        self.remove(self._omenu)

def _curses_quit():
    _scr.keypad(1)
    echo()
    nocbreak()
    noraw()
    endwin()

class Application(AbstractApplication):
    def __init__(self):
        AbstractApplication.__init__(self)
        #sys.excepthook = _curses_excepthook
        global _scr
        _scr = initscr()
        noecho()
        cbreak()
        raw()
        _app = self

    def _window_deleted(self):
        if not self._windows:
            _curses_quit()
            sys.exit()
        else:
            if self._windows:
                self._windows[0]._change_focus()

    def run(self):
        try:
            AbstractApplication.run(self)
        except:
            # In the event of an error, restore the terminal
            # to a sane state.
            _curses_quit()

            # Pass the exception upwards
            (exc_type, exc_value, exc_traceback) = sys.exc_info()
            if hasattr(exc_value,"value"):
                print "Exception value:",exc_value.value
            raise exc_type, exc_value, exc_traceback
        else:
            # In the event of an error, restore the terminal
            # to a sane state.
            _curses_quit()

    def _mainloop(self):
        if self._windows:
            self._windows[0]._change_focus()
        self._redraw_all()
        while self._check_for_events():
            self._redraw_all()

    def _app_event_handler(self,ch):
        if ch == 17: # ^Q
            return 0
        if ch == 6:  # ^F
            self._change_focus()
        return 1

    def _check_for_events(self):
        ch = _scr.getch()
        handled = 0
        if _focus_control is not None:
            handled = _focus_control._handle_event(chr(ch))
        if not handled:
            return self._app_event_handler(ch)
        return 1

    def _redraw_all(self):
        global _refresh_all
        if _refresh_all:
            _scr.erase()
            for win in self._windows:
                win._redraw()
            _refresh_all = 0
        #dbg("redraw_all: %s"%self._windows)
        _scr.refresh()
        self._ensure_focus()

    def _change_focus(self):
        # Find the window with focus:
        #dbg("focus changing...")
        for ii in range(len(self._windows)):
            if self._windows[ii]._focus:
                #dbg("Window %s has focus"%ii)
                self._windows[ii]._change_focus()
                if not self._windows[ii]._focus:
                    jj = ii+1
                    if jj >= len(self._windows):
                        jj = 0
                    self._windows[jj]._change_focus()
                return
        #dbg("No focus! Giving to window 0")
        if self._windows:
            self._windows[0]._change_focus()

    def _ensure_focus(self):
        for win in self._windows:
            win._ensure_focus()
