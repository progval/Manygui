import sys
#from curses import *

from anygui.backends import *
from anygui.Exceptions import Error

# Screen-management package.
_support = None

class CursesGUIException(Error):

    def __init__(self,**kws):
        self.__dict__.update(kws)

_refresh_all_flag = 0
def _refresh_all():
    global _refresh_all_flag
    _refresh_all_flag = 1
_focus_control = None

def _discard_focus():
    global _focus_control
    _focus_control = None

def _set_scale(x,y):
    ComponentMixin._horiz_scale = float(x)/640.0
    ComponentMixin._vert_scale = float(y)/480.0

def _contains(cont,comp):
    while comp:
        if comp == cont: return 1
        try:
            comp = comp._container
        except AttributeError:
            return 0
    return 0

class ComponentMixin:
    """ Mixin class for components.
    We're really only using curses as a screen-addressing
    library, since its implementation of "windows" isn't
    really very much like a GUI window. """

    # We'll map coordinates according to these scaling factors.
    # This lets normal anygui programs run under curses without
    # having to scroll the screen. This might not be such a
    # good idea, but it's worth a try.
    _horiz_scale = 80.0/640.0
    _vert_scale = 24.0/480.0
    #_horiz_scale = 1.0
    #_vert_scale = 1.0

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
        #_support.dbg("Creating %s"%self)
        self._curses_created = 0
        self._focus = 0
        self._focus_capture = 0
        self._cpos = 1,1 # Cursor position when in focus.
        self._LVLINE = _support.SCR_LVLINE
        self._RVLINE = _support.SCR_RVLINE
        self._UHLINE = _support.SCR_UHLINE
        self._LHLINE = _support.SCR_LHLINE
        self._ULCORNER = _support.SCR_ULCORNER
        self._URCORNER = _support.SCR_URCORNER
        self._LLCORNER = _support.SCR_LLCORNER
        self._LRCORNER = _support.SCR_LRCORNER
        self._attr = _support.ATTR_NORMAL

    def _set_focus(self,val):
        _support.dbg("Focus->",val,self)
        global _focus_control
        # Remove focus from all other components.
        _discard_focus()
        if val:

            if not self._gets_focus:

                # Figure out who to give focus to next.
                self._move_focus()
                return

            # Give focus to self.
            _focus_control = self
        else:
            if self._focus_capture:
                _support.dbg("Capturing focus: ",self)
                self.focus = 1
                _support.dbg("After capture, focus on:",_focus_control)
                return
            self._relinquish_focus()

    def _move_focus(self):
        # For non-containers, this is just a relinquish.
        self._relinquish_focus()

    def _relinquish_focus(self):
        self._container._component_lost_focus(self)

    def _set_focus_capture(self,val):
        if val:
            _discard_focus()
            self._focus_capture = 1
            self.focus = 1
        else:
            self._focus_capture = 0

    def _scale_xy(self,x,y):
        return (int(x*self._horiz_scale),int(y*self._vert_scale))
    def _scale_yx(self,y,x):
        nx,ny = self._scale_xy(x,y)
        return ny,nx

    def _get_screen_coords(self):
        if not self._curses_created: return 0,0
        #if self._needs_container and not self._container: return 0,0
        x,y = self._scale_xy(self.x,self.y)
        #_support.dbg("_gsc: %s,%s: %s"%(x,y,self._text))
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
        #_support.dbg("_container_intersect (%s,%s) %s,%s,%s,%s: %s"%(x,y,ix,iy,iw,ih,self))
        return ix,iy,iw,ih

    def _addstr(self,x,y,str,attr=0):
        if attr == 0:
            attr = self._attr
        sx,sy,w,h = self._get_bounding_rect()
        if y>=h: return
        x += sx
        y += sy
        _support.addstr(x,y,str,sx+w-x,attr)

    def _get_bounding_rect(self):
        # Get the screen x,y,w,h of the visible portion of the component.
        # If the control is invisible or completely clipped, w and h
        # are both 0.
        if not self._visible or not self._curses_created:
            return 0,0,0,0
        x,y = self._get_screen_coords()
        #_support.dbg("%s,%s: %s"%(x,y,self))
        w,h = self._scale_xy(self.width,self.height)
        x,y,w,h = self._container_intersect(x,y,w,h)
        return x,y,w,h

    def _redraw(self):
        #_support.dbg("Redrawing (%d) %s"%(self.refresh,self))
        if not self._curses_created: return
        #_support.dbg("Visible: %s"%self)
        if self._visible:
            self._erase()
            self._draw_border()
            self._draw_contents()
            self._addstr(self._textx,self._texty,self._text)

    def _erase(self):
        if not self._curses_created: return
        x,y,w,h = self._get_bounding_rect()
        #_support.dbg("Erasing %s"%self)
        _support.erase(x,y,w,h)

    def _draw_border(self):
        if not self._curses_created: return
        if not self._border: return
        x,y = self._get_screen_coords()
        w,h = self._scale_xy(self.width,self.height)
        #_support.dbg("Screen coords %s for %s"%((x,y,w,h),self))
        x,y,w,h = self._container_intersect(x,y,w,h)
        if w == 0 or h == 0: return
        #_support.dbg("Container intersect %s for %s"%((x,y,w,h),self))
        _support.addch(y,x,self._ULCORNER)
        _support.addch(y,x+w-1,self._URCORNER)
        _support.addch(y+h-1,x,self._LLCORNER)
        _support.addch(y+h-1,x+w-1,self._LRCORNER)
        for xx in range(x+1,x+w-1):
            _support.addch(y,xx,self._UHLINE)
            _support.addch(y+h-1,xx,self._LHLINE)
        for yy in range(y+1,y+h-1):
            _support.addch(yy,x,self._LVLINE)
            _support.addch(yy,x+w-1,self._RVLINE)

    def _draw_contents(self):
        if not self._curses_created: return
        pass

    def _ensure_focus(self):
        if not self._curses_created: return
        x,y = self._get_screen_coords()
        _support.dbg("Ensuring focus %s,%s on %s"%(x,y,self))
        if _focus_control is self:
            #_support.dbg("Ensuring focus on ",self)
            #_support.dbg("   HAS FOCUS!")
            _support.move_cursor(x+self._textx,y+self._texty)

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
        #_support.dbg("_ensure_created(): %s"%self)
        if self._curses_created:
            return 0
        if self._needs_container and not self._container:
            return 0
        self._curses_created = 1
        return 1

    def _ensure_geometry(self):
        #_support.dbg("Ensuring geometry",self.geometry,self)
        _refresh_all()
        self._redraw()

    def _ensure_visibility(self):
        self._redraw()

    def _ensure_enabled_state(self):
        self._redraw()

    def _ensure_destroyed(self):
        #_support.dbg("Ensuring destroyed: %s"%self)
        self._erase()
        self._curses_created = 0
        self._focus_capture = 0

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

    def __init__(self,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        AbstractButton.__init__(self,*args,**kws)
        #self._LVLINE = ord('<')
        #self._RVLINE = ord('>')
        #self._UHLINE = ord(' ')
        #self._LHLINE = ord(' ')
        #self._ULCORNER = ord('<')
        #self._URCORNER = ord('>')
        #self._LLCORNER = ord('<')
        #self._LRCORNER = ord('>')
        #self._attr = _support.ATTR_UNDERLINE

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

    def _move_focus(self):
        if _focus_control is not None:
            return
        # We are being given focus, but cannot accept. Try
        # to hand it to a sub-control; otherwise, relinquish.
        for comp in self._contents:
            if not comp._curses_created:
                continue
            comp.focus = 1
            if _focus_control is not None:
                return
        self._container._component_lost_focus(self)

    def _component_lost_focus(self,comp):
        # Give focus to the next component in self._contents,
        # or relinquish to self._container else.
        if not comp in self._contents:
            _support.dbg("BAD! Focus lost from non-content!")
            return
        ii = self._contents.index(comp)
        ii += 1
        if ii >= len(self.contents):
            # Tabbed off of last control. Can't call
            # _relinquish_focus() here, since it's overridden
            # to do something different.
            if self._focus_capture:
                _support.dbg("2 Capturing focus: ",self)
                self.focus = 1
                _support.dbg("2 After capture, focus on:",_focus_control)
                return
            self._container._component_lost_focus(self)
            return
        self._contents[ii].focus = 1

    def _relinquish_focus(self):
        # A container relinquishes focus by giving the
        # focus to its contents, if possible.
        self._move_focus()

    def _redraw(self):
        if not self._curses_created: return
        ComponentMixin._redraw(self)
        for comp in self._contents:
            comp._redraw()

    def _ensure_destroyed(self):
        _support.dbg("Ensuring destroyed ",self)
        self._focus_capture = 0
        for comp in self._contents:
            comp._ensure_destroyed()
        _support.dbg("Focus on ",_focus_control,"after dtoy",self)
        self._erase()
        self._curses_created = 0

    def _ensure_focus(self):
        _support.dbg("Ensuring focus in %s"%self)
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
            # Fix the focus.
            global _focus_control
            had_focus = 0
            if _contains(comp,_focus_control):
                had_focus = 1
                _discard_focus()

            comp._ensure_destroyed()
            self._contents.remove(comp)
            comp._set_container(None)

            #_support.dbg("Refreshing %s"%self)
            if had_focus:
                self.focus = 1
            self._redraw()
        except ValueError:
            pass

class Frame(ContainerMixin, AbstractFrame):

    _gets_focus = 0

    def __init__(self,*args,**kws):
        ContainerMixin.__init__(self,*args,**kws)
        AbstractFrame.__init__(self,*args,**kws)
        self._text = ""

class Window(ContainerMixin, AbstractWindow):

    _needs_container = 0
    _texty = 0

    def __init__(self,*args,**kws):
        ContainerMixin.__init__(self,*args,**kws)
        AbstractWindow.__init__(self,*args,**kws)
        self._text = ""
        #_support.dbg("%s:%s"%(self._title,self.geometry))

    def _ensure_destroyed(self):
        ContainerMixin._ensure_destroyed(self)
        _app._remove_window(self)
        _app._window_deleted()

    def _move_to_top(self):
        _app._move_to_top(self)

    def _set_focus(self,val):
        ContainerMixin._set_focus(self,val)
        if val:
            self._move_to_top()

    def _move_focus(self):
        if _focus_control is not None:
            return
        # We are being given focus, but cannot accept. Try
        # to hand it to a sub-control; otherwise, relinquish.
        for comp in self._contents:
            if not comp._curses_created:
                continue
            comp.focus = 1
            if _focus_control is not None:
                return
        _app._window_lost_focus(self)

    def _component_lost_focus(self,comp):
        # Give focus to the next component in self._contents,
        # or relinquish to the next window else.
        if not comp in self._contents:
            _support.dbg("BAD! Focus lost from non-content!")
            return
        ii = self._contents.index(comp)
        ii += 1
        if ii >= len(self.contents):
            # Tabbed off of last control. Can't call
            # _relinquish_focus() here, since it's overridden
            # to do something different.
            if self._focus_capture:
                _support.dbg("3 Capturing focus: ",self)
                self.focus = 1
                _support.dbg("3 After capture, focus on:",_focus_control)
                return
            _app._window_lost_focus(self)
            return
        self._contents[ii].focus = 1

    #def _relinquish_focus(self):
    #    if self._contents:
    #        self._move_focus()
    #    else:
    #        _app._window_lost_focus(self)

    def _redraw(self):
        if not self._curses_created: return
        ContainerMixin._redraw(self)
        self._addstr(2,0,self._title)

    def _ensure_title(self): self._redraw()

    def _present_winmenu(self):
        x,y = self._x,self._y
        w,h = int(round(12.0/self._horiz_scale)),int(round(8.0/self._vert_scale))
        self._omenu = Window(title="?Window")
        self._omenu.geometry=(x,y,w,h)
        sx,sy,sw,sh = self._omenu._get_bounding_rect()
        _support.dbg("omenu geo",(x,y,w,h))
        _support.dbg("omenu scr geo",(sx,sy,sw,sh))
        x,y = int(round(1.0/self._horiz_scale)),int(round(1.0/self._vert_scale))
        w,h = int(round(10.0/self._horiz_scale)),int(round(3.0/self._vert_scale))
        self._clbtn = Button(geometry=(x,y,w,h),text="Close")
        self._omenu.add(self._clbtn)
        self._omenu._gets_focus=0
        link(self._clbtn,self._close)

        x,y = int(round(1.0/self._horiz_scale)),int(round(4.0/self._vert_scale))
        self._canbtn = Button(geometry=(x,y,w,h),text="Cancel")
        self._omenu.add(self._canbtn)
        link(self._canbtn,self._cancel_close)

        self._omenu.open()
        self._omenu.focus_capture = 1
        
        self._redraw()
        self._omenu._redraw()

    def _event_handler(self,ch):
        # Handle the ^Option command by popping up a
        # window menu.
        if ord(ch) == 15:
            self._present_winmenu()
            return 1

    def _close(self,*args,**kws):
        _support.dbg("CLOSING %s"%self)
        self._omenu.destroy()
        self.destroy()

    def _cancel_close(self,*args,**kws):
        self._omenu.destroy()

class Application(AbstractApplication):
    def __init__(self):
        AbstractApplication.__init__(self)
        self._quit = 0
        _support.scr_init()
        global _app
        _app = self

    def _window_deleted(self):
        _support.dbg("WINDOW DELETED")
        if not self._windows:
            self._quit = 1
        else:
            _refresh_all()
            self._windows[0].focus = 1

    def run(self):
        try:
            AbstractApplication.run(self)
        except:
            # In the event of an error, restore the terminal
            # to a sane state.
            _support.scr_quit()

            # Pass the exception upwards
            (exc_type, exc_value, exc_traceback) = sys.exc_info()
            if hasattr(exc_value,"value"):
                print "Exception value:",exc_value.value
            raise exc_type, exc_value, exc_traceback
        else:
            # In the event of an error, restore the terminal
            # to a sane state.
            _support.scr_quit()

    def _mainloop(self):
        if self._windows:
            self._windows[0].focus = 1
        self._redraw_all()
        while (not self._quit) and self._check_for_events():
            self._redraw_all()

    def _app_event_handler(self,ch):
        _support.dbg("APP_EVENT_HANDLER",ch)
        if ch == 17: # ^Q
            return 0
        if ch == 6:  # ^F
            self._change_focus()
        return 1

    def _check_for_events(self):
        ch = _support.get_char()
        handled = 0
        if _focus_control is not None:
            handled = _focus_control._handle_event(chr(ch))
        if not handled:
            return self._app_event_handler(ch)
        return 1

    def _redraw_all(self):
        global _refresh_all_flag
        if _refresh_all_flag:
            _support.erase_all()
            for win in self._windows:
                win._redraw()
            _refresh_all_flag = 0
        #_support.dbg("redraw_all: %s"%self._windows)
        _support.refresh()
        self._ensure_focus()

    def _change_focus(self):
        if not _focus_control:
            _support.dbg("    No focus; giving to...")
            if self._windows:
                _support.dbg(self._windows[0])
                self._windows[0].focus = 1
            else:
                pass
                _support.dbg("    NOTHING: no windows!")
        else:
            #_support.dbg("    Changing focus from",_focus_control)
            _focus_control.focus = 0
        self._ensure_focus()

    def _window_lost_focus(self,win):
        try:
            ii = self._windows.index(win)
            ii += 1
            if ii >= len(self._windows):
                ii = 0
        except ValueError:
            ii = 0
        try:
            self._windows[ii].focus = 1
        except IndexError:
            self._quit = 1

    def _ensure_focus(self):
        for win in self._windows:
            win._ensure_focus()

    def _move_to_top(self,win):
        self._windows.remove(win)
        self._windows.append(win)
        _refresh_all()
