import sys
#from curses import *

from anygui.backends import *
from anygui.Exceptions import Error

# Map of character codes to names.
_charnames = {ord(' '):'space',
              258:'down arrow',
              259:'up arrow',
              260:'left arrow',
              261:'right arrow',
              27:'ESC',
              127:'backspace',
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
_scr = None

_refresh_all_flag = 0
def _refresh_all():
    global _refresh_all_flag
    _refresh_all_flag = 1

_all_components = [] # List of all controls. Used for focus management.
_focus_control = None
_focus_capture_control = None
_focus_dir = 1
def _discard_focus():
    global _focus_control
    _focus_control = None

def _add_to_focus_list(comp):
    """ Add comp to _all_components in the proper focus-visit position. """
    prev_comp = None
    if comp._container:
        # Find last control in the container in _all_components
        # that is not comp.
        c = comp._container
        prev_comp = c # Insert after container by default.
        rcs = c._contents[:]
        rcs.reverse()
        for cc in rcs:
            if cc is not comp:
                prev_comp = cc
                break
    if prev_comp and prev_comp in _all_components:
        ii = _all_components.index(prev_comp)
        _all_components.insert(ii+1,comp)
        return
    _all_components.append(comp)

def _remove_from_focus_list(comp):
    if _focus_control is comp:
        _app._change_focus()
    if _focus_control is comp:
        _discard_focus()
    try:
        _all_components.remove(comp)
    except ValueError:
        pass

def _in_focus_purview(comp):
    if _focus_capture_control is None:
        return 1
    return _contains(_focus_capture_control,comp)

def _contains(cont,comp):
    while comp:
        if comp == cont: return 1
        try:
            comp = comp._container
        except AttributeError:
            return 0
    return 0

def _set_scale(x,y):
    ComponentMixin._horiz_scale = float(x)/640.0
    ComponentMixin._vert_scale = float(y)/480.0

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
    _title = "txtgui"
    _gets_focus = 1
    _text = "txtgui"
    _use_text = 1
    _textx = 1
    _texty = 1
    _tiny_LLCORNER = ord('<')
    _tiny_LRCORNER = ord('>')

    # Event-handler maps.
    _event_map = {}
    _event_range_map = {}

    def _get_event_help(self):
        items = []
        evmap = self._event_map
        kk = evmap.keys()
        kk.sort()
        for ch in kk:
            f = evmap[ch]
            if f == ComponentMixin._ignore_event:
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
                items.append(item)
                items.append(' ')
        try:
            if self._container:
                items += self._container._get_event_help()
        except:
            a,b,c = sys.exc_info()
            items.append("*** Exception gathering help data!"+str(b))
        return items

    def __init__(self,*args,**kws):
        ##_scr.dbg("Creating %s"%self)
        self._curses_created = 0
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

    def _is_visible(self):
        if self._visible: return self._container._is_visible()

    def _set_focus(self,val):
        #self._ensure_enabled_state()
        global _focus_control
        if val:
            _focus_control = self
            #_scr.dbg("_set_focus:",self._gets_focus,self._is_visible(),self._curses_created,_in_focus_purview(self),self)
            if self._gets_focus and self._is_visible() and self._curses_created \
               and _in_focus_purview(self):
                return
            else:
                _app._change_focus(_focus_dir)
        else:
            if _focus_control is self:
                _discard_focus()

    def _set_focus_capture(self,val):
        global _focus_capture_control
        if val:
            _focus_capture_control = self
            _app._change_focus()
        else:
            if _focus_capture_control is self:
                _focus_capture_control = None

    def _scale_xy(self,x,y):
        return (int(x*self._horiz_scale),int(y*self._vert_scale))
    def _scale_yx(self,y,x):
        nx,ny = self._scale_xy(x,y)
        return ny,nx

    def _screen_height(self):
        w,h = self._scale_xy(self.width,self.height)
        return h

    def _screen_width(self):
        w,h = self._scale_xy(self.width,self.height)
        return w

    def _effective_texty(self):
        return min(self._texty,self._screen_height()-1)

    def _get_screen_coords(self):
        if not self._curses_created: return 0,0
        #if self._needs_container and not self._container: return 0,0
        x,y = self._scale_xy(self.x,self.y)
        ##_scr.dbg("_gsc: %s,%s: %s"%(x,y,self._text))
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
        ##_scr.dbg("_container_intersect (%s,%s) %s,%s,%s,%s: %s"%(x,y,ix,iy,iw,ih,self))
        return ix,iy,iw,ih

    def _addstr(self,x,y,str,attr=0):
        if attr == 0:
            attr = self._attr
        sx,sy,w,h = self._get_bounding_rect()
        if y>=h: return
        x += sx
        y += sy
        _scr.addstr(x,y,str,sx+w-x,attr)

    def _get_bounding_rect(self):
        # Get the screen x,y,w,h of the visible portion of the component.
        # If the control is invisible or completely clipped, w and h
        # are both 0.
        if not self._visible or not self._curses_created:
            return 0,0,0,0
        x,y = self._get_screen_coords()
        ##_scr.dbg("%s,%s: %s"%(x,y,self))
        w,h = self._scale_xy(self.width,self.height)
        x,y,w,h = self._container_intersect(x,y,w,h)
        return x,y,w,h

    def _redraw(self):
        ##_scr.dbg("Redrawing (%d) %s"%(self.refresh,self))
        if not self._curses_created: return
        ##_scr.dbg("Visible: %s"%self)
        x,y = self._get_screen_coords()
        if self._visible:
            self._erase()
            self._draw_border()
            self._draw_contents()
            ety = self._effective_texty()
            #_scr.dbg("ety ",ety,self,self._height*self._vert_scale)
            if self._use_text:
                self._addstr(self._textx,ety,self._text)

    def _erase(self):
        if not self._curses_created: return
        x,y,w,h = self._get_bounding_rect()
        ##_scr.dbg("Erasing %s"%self)
        _scr.erase(x,y,w,h)

    def _draw_border(self):
        if not self._curses_created: return
        if not self._border: return
        x,y = self._get_screen_coords()
        w,h = self._scale_xy(self.width,self.height)
        ##_scr.dbg("Screen coords %s for %s"%((x,y,w,h),self))
        x,y,w,h = self._container_intersect(x,y,w,h)
        if w == 0 or h == 0: return
        ##_scr.dbg("Container intersect %s for %s"%((x,y,w,h),self))

        llcorner = self._LLCORNER
        lrcorner = self._LRCORNER
        if self._screen_height() < 2:
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

    def _draw_contents(self):
        if not self._curses_created: return
        pass

    def _ensure_focus(self):
        if not self._curses_created: return
        x,y = self._get_screen_coords()
        ##_scr.dbg("Ensuring focus %s,%s on %s"%(x,y,self))
        if _focus_control is self:
            ##_scr.dbg("Ensuring focus on ",self)
            ##_scr.dbg("   HAS FOCUS!")
            ety = self._effective_texty()
            #_scr.dbg("focus ety ",ety,self,self._height*self._vert_scale)
            _scr.move_cursor(x+self._textx,y+ety)

    def _handle_event(self,ev):
        handled = self._event_handler(ev)
        if handled: return 1
        if self._container:
            # Propagate unhandled events to container.
            return self._container._handle_event(ev)
        return 0

    def _event_handler(self,ev):
        try:
            handled = self._event_map[ev](self,ev)
            return handled
        except KeyError:
            for (lo,hi) in self._event_range_map.keys():
                if ev>=lo and ev<=hi:
                    handled = self._event_range_map[(lo,hi)](self,ev)
                    return handled
        return 0

    def _ignore_event(self,ev):
        return 0

    # backend api

    def _is_created(self):
        return self._curses_created

    def _ensure_created(self):
        ##_scr.dbg("_ensure_created(): %s"%self)
        if self._curses_created:
            return 0
        if self._needs_container and not self._container:
            return 0
        self._curses_created = 1
        _add_to_focus_list(self)
        return 1

    def _ensure_geometry(self):
        ##_scr.dbg("Ensuring geometry",self.geometry,self)
        _refresh_all()
        self._redraw()

    def _ensure_visibility(self):
        self._redraw()

    def _ensure_enabled_state(self):
        #_scr.dbg("ENSURING ENABLED",self)
        # UNTESTED!
        if not self._enabled:
            #_scr.dbg("   NOT ENABLED")
            self._gets_focus = 0
            if _focus_control is self:
                _app._change_focus()
        else:
            #_scr.dbg("   ENABLED")
            self._gets_focus = self.__class__._gets_focus

    def _ensure_destroyed(self):
        ##_scr.dbg("Ensuring destroyed: %s"%self)
        self.focus_capture = 0
        _remove_from_focus_list(self)
        self._erase()
        self._curses_created = 0

    def _ensure_events(self):
        pass

    def _ensure_editable(self):
        pass

    def _ensure_text(self):
        self._ensure_editable()
        self._redraw()

class ContainerMixin(ComponentMixin):
    """ Special handling for containers. These are mostly the
    same, presentation-wise, as regular components, but they
    manage their focus differently. """

    def __init__(self,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)

    def _is_visible(self):
        if self._container:
            return ComponentMixin._is_visible(self)
        if self._visible: return 1
        return 0

    def _redraw(self):
        if not self._curses_created: return
        ComponentMixin._redraw(self)
        for comp in self._contents:
            comp._redraw()

    def _ensure_destroyed(self):
        ##_scr.dbg("Ensuring destroyed ",self)
        self.focus_capture = 0
        _remove_from_focus_list(self)
        for comp in self._contents:
            comp._ensure_destroyed()
        ##_scr.dbg("Focus on ",_focus_control,"after dtoy",self)
        self._erase()
        self._curses_created = 0

    def _ensure_focus(self):
        ##_scr.dbg("Ensuring focus in %s"%self)
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
            if _focus_control is self:
                _app._change_focus()

            comp._ensure_destroyed()
            self._contents.remove(comp)
            comp._set_container(None)

            ##_scr.dbg("Refreshing %s"%self)
            self._redraw()
        except ValueError:
            pass

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

    _use_text = 0

    def __init__(self,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        AbstractListBox.__init__(self,*args,**kws)
    
    def _ensure_items(self):
        pass

    def _ensure_selection(self):
        pass

    def _backend_selection(self):
        return self._selection

    def _draw_contents(self):
        lh = self._screen_height()-2
        start = 0
        if lh<len(self._items):
            start = self._selection - lh + 1
            if start<0: start = 0

        x=2;y=1
        for ii in range(start,len(self._items)):
            item = str(self._items[ii])
            if self._selection == ii:
                self._addstr(x-1,y,'>')
            self._addstr(x,y,item)
            y+=1
            if y>lh: return

    def _select_down(self,ev):
        """Move listbox selection down."""
        self._selection += 1
        if self._selection >= len(self._items):
            self._selection = 0
        self._redraw()

    def _select_up(self,ev):
        """Move listbox selection up."""
        self._selection -= 1
        if self._selection < 0:
            self._selection = len(self._items)-1
        self._redraw()

    def _do_click(self,ev):
        """Click on selected item."""
        send(self,'select')

    _event_map = { ord('j'):_select_down,
                   ord('k'):_select_up,
                   ord(' '):_do_click }

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
        self._attr = _scr.ATTR_UNDERLINE

    def __str__(self): return "Button "+self._text

    def _do_click(self,ev):
        """Click on button."""
        send(self,'click')

    _event_map = { ord(' '):_do_click }

class ToggleButtonMixin(ComponentMixin):

    _textx = 2
    _on_ind = '+'
    _off_ind = '-'

    def __init__(self,value=0,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        self._value = value

    def _curs_clicked(self):
        """Click on button."""
        self.on = not self.on # FIXME: ??
        self._redraw()
        send(self, 'click')

    _event_map = { ord(' '):_curs_clicked }

    def _ensure_state(self):
        self._redraw()

    def _draw_contents(self):
        ind = self._off_ind
        if self.on:
            ind = self._on_ind
        ety = self._effective_texty()
        self._addstr(self._textx-1,ety,ind)

class CheckBox(ToggleButtonMixin, AbstractCheckBox):

    _border = 0

    def __init__(self,*args,**kws):
        ToggleButtonMixin.__init__(self,*args,**kws)
        AbstractCheckBox.__init__(self,*args,**kws)
    
class RadioButton(ToggleButtonMixin, AbstractRadioButton):

    _on_ind = '*'
    _off_ind = '.'
    _border = 0

    def __init__(self,*args,**kws):
        ToggleButtonMixin.__init__(self,*args,**kws)
        AbstractRadioButton.__init__(self,*args,**kws)

    def _curs_clicked(self):
        if self.group is not None:
            self.group.value = self.value
        self._redraw()
        send(self, 'click')

class DisabledTextBindings: pass

import string
class TextMixin(ComponentMixin):

    _use_text = 0 # Prevent naive text presentation.

    def __init__(self,*args,**kws):
        ComponentMixin.__init__(self,*args,**kws)
        self._tpos=0
        self._cur_pos=(1,1)
        self._cur_line = 0
        self._cur_col = 0

    def _ensure_editable(self):
        #_scr.dbg("ENSURING EDITABLE",self)
        # UNTESTED!
        if not self._editable:
            #_scr.dbg("   NOT EDITABLE")
            self._gets_focus = 0
            if _focus_control is self:
                _app._change_focus()
        else:
            #_scr.dbg("   EDITABLE")
            self._gets_focus = self.__class__._gets_focus

    def _ensure_focus(self):
        if not self._curses_created: return
        x,y = self._get_screen_coords()
        ##_scr.dbg("Ensuring focus %s,%s on %s"%(x,y,self))
        if _focus_control is self:
            ##_scr.dbg("Ensuring focus on ",self)
            ##_scr.dbg("   HAS FOCUS!")
            ety = self._effective_texty()
            #_scr.dbg("focus ety ",ety,self,self._height*self._vert_scale)
            tx,ty = self._cur_pos
            _scr.move_cursor(x+tx,y+ty)

    ### Event handlers ###
    def _backspace(self,ev):
        """Erase character before cursor."""
        if self._tpos < 1: return 1
        self._text = self._text[:self._tpos-1] + self._text[self._tpos:]
        self._tpos -= 1
        self._redraw()
        return 1

    def _insert(self,ev):
        """Insert character before cursor."""
        if not chr(ev) in string.printable:
            return 0
        self._text = self._text[:self._tpos] + chr(ev) + self._text[self._tpos:]
        self._tpos += 1
        self._redraw() # FIXME: only really need to redraw current line.
        return 1

    def _back(self,ev):
        """Move cursor back one character."""
        self._tpos -= 1
        if self._tpos<0: self._tpos=0
        self._redraw()
        return 1

    def _fwd(self,ev):
        """Move cursor forward one character."""
        self._tpos += 1
        if self._tpos>len(self._text): self._tpos=len(self._text)
        self._redraw()
        return 1

    def _change_focus(self,ev):
        """Focus on the next control."""
        _app._change_focus()

    def _down_line(self,ev):
        """Move cursor up one line."""
        self._move_line(1)
        
    def _up_line(self,ev):
        """Move cursor down one line."""
        self._move_line(-1)

    _event_map = {127:_backspace,
                  258:_down_line,
                  259:_up_line,
                  27:_change_focus,
                  260:_back,
                  261:_fwd,
                  15:ComponentMixin._ignore_event
                  }
    _event_range_map = {(8,255):_insert}

    ### Event handler end ###

    def _move_line(self,n):
        lines = self._text.split('\n')
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
        self._redraw()

    def _draw_contents(self):
        if self._screen_height()<2: return
        
        t = self._text
        x=1;y=1
        lines = self._text.split('\n')
        line,col = self._find_cursor_pos(lines)
        self._cur_line_len = len(lines[line])

        startline,startcol = self._find_relative_cpos(line,col,len(lines),len(lines[line]))
        sh = self._screen_height()

        for li in range(0,min(sh,len(lines)-startline)):
            #_scr.dbg("start,line:",startline,li,self)
            line = lines[startline+li]
            self._addstr(x,y,line[startcol:])
            y+=1

    def _find_relative_cpos(self,line,col,nlines,nchars):
        # Take the line,col position of the cursor in self._text
        # and convert it, based on window size, into the window-
        # relative cursor position, which is stored in self._cpos.
        # Then return the line and column of the character that
        # should appear at the top-left corner.
        lh = self._screen_height()-2
        startline = 0
        if lh<nlines:
            startline = line - lh
            if startline<0: startline = 0
            
        lw = self._screen_width()-2
        startcol = 0
        if lw<nchars:
            startcol = col - lw
            if startcol<0: startcol = 0

        self._cur_pos = (col-startcol+1, line-startline+1)
        #_scr.dbg("cur_pos:",self._cur_pos,self)

        return startline,startcol

    def _find_cursor_pos(self,lines):
        tp = self._tpos
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
        self._cur_line = line
        self._cur_col = col
        return line,col

    def _ensure_editable(self):
        pass

    def _ensure_selection(self):
        pass

    def _backend_text(self):
        return self._text

    def _backend_selection(self):
        return 0,0

class TextField(TextMixin, AbstractTextField):

    def __init__(self,*args,**kws):
        TextMixin.__init__(self,*args,**kws)
        AbstractTextField.__init__(self,*args,**kws)

    _event_map = TextMixin._event_map
    del _event_map[258] # No line control in TextFields.
    del _event_map[259]
    _event_map[ord('\n')] = TextMixin._change_focus

class TextArea(TextMixin, AbstractTextArea):

    def __init__(self,*args,**kws):
        TextMixin.__init__(self,*args,**kws)
        AbstractTextArea.__init__(self,*args,**kws)

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
        ##_scr.dbg("%s:%s"%(self._title,self.geometry))

    def _ensure_destroyed(self):
        ContainerMixin._ensure_destroyed(self)
        self.focus_capture = 0
        _remove_from_focus_list(self)
        _app.remove(self)
        _app._window_deleted()

    def _move_to_top(self):
        _app._move_to_top(self)

    def _redraw(self):
        if not self._curses_created: return
        ContainerMixin._redraw(self)
        self._addstr(2,0,self._title)

    def _ensure_title(self): self._redraw()

    def _present_winmenu(self,ev):
        """Open window menu"""
        x,y = self._x,self._y
        w,h = int(round(12.1/self._horiz_scale)),int(round(4.1/self._vert_scale))
        self._omenu = WinMenuWindow(title="?Window")
        self._omenu._pwin = self
        self._omenu.geometry=(x,y,w,h)
        x,y = int(round(1.1/self._horiz_scale)),int(round(1.1/self._vert_scale))
        w,h = int(round(10.1/self._horiz_scale)),int(round(1.1/self._vert_scale))
        self._clbtn = MenuButton(geometry=(x,y,w,h),text="Close")
        self._omenu.add(self._clbtn)
        self._omenu._gets_focus=0
        link(self._clbtn,self._close)

        x,y = int(round(1.1/self._horiz_scale)),int(round(2.1/self._vert_scale))
        self._canbtn = MenuButton(geometry=(x,y,w,h),text="Cancel")
        self._omenu.add(self._canbtn)
        link(self._canbtn,self._cancel_close)

        _app.add(self._omenu)
        self._omenu.focus_capture = 1
        
        self._redraw()
        self._omenu._redraw()

    _event_map = {15:_present_winmenu}

    def _curs_resized(self,dw,dh):
        self.resized(dw,dh)

    def _handle_wm_event(self,ch):
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
            self._curs_resized(-hinc,0)
            return 1
        if ch == ord('L'):
            self.width += hinc
            self._curs_resized(hinc,0)
            return 1
        if ch == ord('J'):
            self.height += vinc
            self._curs_resized(0,vinc)
            return 1
        if ch == ord('K'):
            self.height -= vinc
            self._curs_resized(0,-vinc)
            return 1
        return 0

    def _close(self,*args,**kws):
        ##_scr.dbg("CLOSING %s"%self)
        self._omenu.destroy()
        self.destroy()

    def _cancel_close(self,*args,**kws):
        self._omenu.destroy()
        self.focus = 1

class WinMenuWindow(Window):

    _gets_focus = 0

    def _handle_wmove_event(self,ev):
        """Move the window."""
        _scr.dbg("MOVE",chr(ev))
        return self._pwin._handle_wm_event(ev)

    def _handle_wconfig_event(self,ev):
        """Resize the window."""
        _scr.dbg("RESIZE",chr(ev))
        return self._pwin._handle_wm_event(ev)

    _event_map = {ord('h'):_handle_wmove_event,
                  ord('j'):_handle_wmove_event,
                  ord('k'):_handle_wmove_event,
                  ord('l'):_handle_wmove_event,
                  ord('H'):_handle_wconfig_event,
                  ord('J'):_handle_wconfig_event,
                  ord('K'):_handle_wconfig_event,
                  ord('L'):_handle_wconfig_event,
                  }
    
class MenuButton(Button):

    _texty = 0

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
        self._title = "INFORMATION (press 'q' to dismiss)"
        self._x = 0
        self._y = 0
        self._width = 600
        self._height = 400
        lb = ListBox(geometry=(10,10,580,380))
        self.add(lb)
        self._populate_lb(lb)
        _app.add(self)
        self.focus_capture = 1

    def _populate_lb(self,lb):
        """Add docstrings for _prev_ctrl event handlers to lb."""
        items = ["This is txtgui, the text/curses binding for Anygui.",
                 "You can get this help screen at any time by typing ^G.",
                 "",
                 "^F and ^B move between controls.",
                 "Under curses, up and down arrow move between controls,",
                 "except in text controls, where they move between lines.",
                 "z and Z can be used to zoom the presentation in and out.",
                 "",
                 "The current control is a "+self._prev_ctrl.__class__.__name__+";",
                 "it supports the following key bindings:",""]
        items += self._prev_ctrl._get_event_help()
        lb.items = items

    def _dismiss(self,ev):
        """Exit help and return to the previous window."""
        self.focus_capture = 0
        self.destroy()
        if self._prev_focus_capture:
            self._prev_focus_capture.focus_capture = 1
        self._prev_ctrl.focus = 1

    #def _event_handler(self,ev):
    #    if ev == ord('q'): self._dismiss(ev)

    _event_map = {ord('q'):_dismiss}

class Application(AbstractApplication):
    def __init__(self):
        AbstractApplication.__init__(self)
        self._quit = 0
        _scr.scr_init()
        _set_scale(_scr._xsize,_scr._ysize)
        global _app
        _app = self

    def _window_deleted(self):
        ##_scr.dbg("WINDOW DELETED")
        if not self._windows:
            self._quit = 1
        else:
            _refresh_all()
            self._change_focus()

    def run(self):
        try:
            AbstractApplication.run(self)
        except:
            # In the event of an error, restore the terminal
            # to a sane state.
            _scr.scr_quit()

            # Pass the exception upwards
            (exc_type, exc_value, exc_traceback) = sys.exc_info()
            if hasattr(exc_value,"value"):
                print "Exception value:",exc_value.value
            raise exc_type, exc_value, exc_traceback
        else:
            # In the event of an error, restore the terminal
            # to a sane state.
            _scr.scr_quit()

    def _mainloop(self):
        # Establish the initial focus.
        self._change_focus()

        # Redraw the screen.
        _refresh_all()
        self._redraw_all()

        # The main event loop:
        while (not self._quit) and self._check_for_events():
            self._redraw_all()

    def _app_event_handler(self,ch):
        #_scr.dbg("APP_EVENT_HANDLER",ch)
        if ch == 7: # ^G
            HelpWindow()
        if ch == 17: # ^Q
            return 0
        if ch == 6 or ch == 258:  # ^F,down
            self._change_focus(1)
        if ch == 2 or ch == 259:  # ^B,up
            self._change_focus(-1)
        if ch == 12:
            _refresh_all()

        if ch == ord('z'):
            ComponentMixin._horiz_scale *= 2.0
            ComponentMixin._vert_scale *= 2.0
            _refresh_all()
        
        if ch == ord('Z'):
            ComponentMixin._horiz_scale /= 2.0
            ComponentMixin._vert_scale /= 2.0
            _refresh_all()
        
        return 1

    def _check_for_events(self):
        ch = _scr.get_char()
        handled = 0
        if _focus_control is not None:
            handled = _focus_control._handle_event(ch)
        if not handled:
            return self._app_event_handler(ch)
        return 1

    def _redraw_all(self):
        global _refresh_all_flag
        if _refresh_all_flag:
            _scr.erase_all()
            for win in self._windows:
                win._redraw()
            _refresh_all_flag = 0
        ##_scr.dbg("redraw_all: %s"%self._windows)
        self._ensure_focus()
        _scr.refresh()

    def _change_focus(self,dir=1):
        #_scr.dbg("**** CHANGING FOCUS",dir)
        global _focus_dir
        _focus_dir = dir
        
        # If no focus, establish focus.
        if not _focus_control:
            for win in _all_components:
                win.focus = 1
                if _focus_control:
                    self._raise_focus_window()
                    return
            #_scr.dbg("NOFOCUS: FOCUS NOW ON",_focus_control,"\n")
            return
        
        # Move focus to the next control that can accept it.
        aclen = len(_all_components)
        #_scr.dbg("aclen:",aclen)
        tried = 0

        fc = _focus_control
        ii = _all_components.index(fc)
        _discard_focus()

        while not _focus_control and tried <= aclen:
            tried += 1
            ii += dir
            if ii>=aclen: ii = 0
            if ii<0: ii = aclen-1
            _all_components[ii].focus = 1

        #_scr.dbg("FOCUS NOW ON",_focus_control,"\n")
        self._raise_focus_window()

    #def _window_lost_focus(self,win):
    #    try:
    #        ii = self._windows.index(win)
    #        ii += 1
    #        if ii >= len(self._windows):
    #            ii = 0
    #    except ValueError:
    #        ii = 0
    #    try:
    #        self._windows[ii].focus = 1
    #    except IndexError:
    #        self._quit = 1

    def _ensure_focus(self):
        for win in self._windows:
            win._ensure_focus()

    def _raise_focus_window(self):
        if not _focus_control: return
        for win in self._windows:
            if _contains(win,_focus_control):
                self._move_to_top(win)

    def _move_to_top(self,win):
        self._windows.remove(win)
        self._windows.append(win)
        _refresh_all()
