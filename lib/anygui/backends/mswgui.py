from anygui.backends import *
#__all__ = anygui.__all__

__all__ = '''

  Application
  ButtonWrapper
  WindowWrapper
  LabelWrapper
  TextFieldWrapper
  TextAreaWrapper
  ListBoxWrapper
  RadioButtonWrapper
  CheckBoxWrapper

'''.split()

from anygui.Utils import log
from anygui.Applications import AbstractApplication
from anygui.Wrappers import AbstractWrapper, DummyWidget, isDummy
from anygui.Events import *
from anygui import application

#ButtonWrapper = 1
TextFieldWrapper = 1
TextAreaWrapper = 3
ListBoxWrapper = 4
RadioButtonWrapper = 5
CheckBoxWrapper = 6

################################################################
import win32gui, win32con

# BUGS:
#
#    When I start test_listbox there is no way to control it
#    with the keyboard, even tabbing into the listbox.
#    Actually, it seems that the arrow keys don't work here
#    at all.

class ComponentWrapper(AbstractWrapper):
    # mixin class, implementing the backend methods
    #_height = -1 # -1 means default size in wxPython
    #_width = -1
    #_x = -1
    #_y = -1

    _win_style_ex = 0

    _hfont = win32gui.GetStockObject(win32con.ANSI_VAR_FONT)

    def __init__(self,*args,**kws):
        AbstractWrapper.__init__(self,*args,**kws)
        self.setConstraints('container','x','y','width','height',
                            'text','selection','geometry','visible')

    def noWidget(self):
        try:
            assert(self.widget.isDummy())
            return 1
        except (AttributeError,AssertionError):
            return 0
    
    def widgetFactory(self,*args,**kws):
        app = application()
        if hasattr(self.proxy.container,'wrapper'):
            parent = self.proxy.container.wrapper.widget
        else:
            parent = 0
        widget = win32gui.CreateWindowEx(self._win_style_ex,
                                         self._wndclass,
                                         "NO SUCH TEXT",
                                         self._win_style,
                                         0,
                                         0,
                                         10,
                                         10,
                                         parent,
                                         0, # hMenu
                                         0, # hInstance
                                         None)
        app.widget_map[widget] = self
        return widget

    def widgetSetUp(self):
        if self.proxy.container:
            self.proxy.container.wrapper.widget_map[self.widget] = self
        win32gui.SendMessage(self.widget,
                             win32con.WM_SETFONT,
                             self._hfont,
                             0)
        self.setVisible(1)

    def getGeometry(self):
        l,t,r,b = win32gui.GetWindowRect(self.widget)
        w = r-l
        h = b-t
        return l,t,w,h

    def setX(self,x):
        if self.noWidget(): return
        ox,y,w,h = self.getGeometry()
        self.setGeometry(x,y,w,h)

    def setY(self,y):
        if self.noWidget(): return
        x,oy,w,h = self.getGeometry()
        self.setGeometry(x,y,w,h)

    def setWidth(self,width):
        if self.noWidget(): return
        x,y,ow,h = self.getGeometry()
        self.setGeometry(x,y,width,h)

    def setHeight(self,height):
        if self.noWidget(): return
        x,y,w,oh = self.getGeometry()
        self.setGeometry(x,y,w,height)

    def setSize(self,width,height):
        if self.noWidget(): return
        x,y,w,h = self.getGeometry()
        self.setGeometry(x,y,width,height)

    def setPosition(self,x,y):
        if self.noWidget(): return
        ox,oy,w,h = self.getGeometry()
        self.setGeometry(x,y,w,h)

    def setGeometry(self,x,y,width,height):
        if self.noWidget(): return
        win32gui.SetWindowPos(self.widget,
                              0,
                              x, y,
                              width, height,
                              win32con.SWP_NOACTIVATE | win32con.SWP_NOZORDER)

    def setVisible(self,visible):
        if self.noWidget(): return
        if visible:
            win32gui.ShowWindow(self.widget, win32con.SW_SHOWNORMAL)
        else:
            win32gui.ShowWindow(self.widget, win32con.SW_HIDE)

    def setEnabled(self,enabled):
        if self.noWidget(): return
        if enabled:
            win32gui.EnableWindow(self.widget, 1)
        else:
            win32gui.EnableWindow(self.widget, 0)

    def destroy(self):
        if self.proxy.container:
            try:
                del self.proxy.container.wrapper.widget_map[self.widget]
            except:
                pass
        if not self.noWidget():
            win32gui.DestroyWindow(self.widget)
            del self.widget

    def setText(self,text):
        if self.noWidget(): return
        win32gui.SetWindowText(self.widget, str(text))

    def getText(self):
        return win32gui.GetWindowText(self.widget)

    def setContainer(self, container):
        if container is None:
            try:
                self.destroy()
            except:
                pass
            return
        parent = container.wrapper.widget
        try:
            assert parent.isDummy()
        except (AttributeError, AssertionError):
            self.destroy()
            self.create(parent)
            self.proxy.push(blocked=['container'])

    def enterMainLoop(self):
        self.proxy.push()


##################################################################

class LabelWrapper(ComponentWrapper):
    #_width = 100 # auto ?
    #_height = 32 # auto ?
    _wndclass = "STATIC"
    #_text = "mswLabel"
    _win_style = win32con.SS_LEFT | win32con.WS_CHILD

##################################################################

class ButtonWrapper(ComponentWrapper):
    _wndclass = "BUTTON"
    _win_style = win32con.BS_PUSHBUTTON | win32con.WS_CHILD
    #_text = "mswButton"

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        #log("Button._WM_COMMAND called, looking for %s==%s"%(wParam>>16,win32con.BN_CLICKED))
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        if (wParam >> 16) == win32con.BN_CLICKED:
            #self.do_action()
            print "SENDING"
            send(self.proxy, 'click')

##################################################################

class ListBoxWrapper(ComponentWrapper):
    _wndclass = "LISTBOX"
    _win_style = win32con.WS_CHILD | win32con.WS_VSCROLL | win32con.WS_BORDER | win32con.LBS_NOTIFY
    _win_style_ex = win32con.WS_EX_CLIENTEDGE

    def getSelection(self):
        if self.noWidget(): return
        return win32gui.SendMessage(self.widget,
                                    win32con.LB_GETCURSEL,
                                    0,
                                    0)

    def setItems(self,items):
        if self.noWidget(): return
        win32gui.SendMessage(self.widget,
                             win32con.LB_RESETCONTENT, 0, 0)
        for item in map(str, list(items)):
            # FIXME: This doesn't work! Items get jumbled...
            win32gui.SendMessage(self.widget,
                                 win32con.LB_ADDSTRING,
                                 0,
                                 item)
                

    def setSelection(self,selection):
        if self.noWidget(): return
        win32gui.SendMessage(self.widget,
                             win32con.LB_SETCURSEL,
                             selection, 0)

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        if wParam >> 16 == win32con.LBN_SELCHANGE:
            #self.do_action()
            send(self.proxy, 'select')

##################################################################

'''
class ToggleButtonMixin(ComponentMixin):

    def _get_msw_text(self):
        # return the text required for creation
        return str(self._text)

    def _ensure_text(self):
        if self.widget:
            win32gui.SetWindowText(self.widget, str(self._text))

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        if (wParam >> 16) == win32con.BN_CLICKED:
            #self.do_action()
            send(self, 'click')

    def _ensure_state(self):
        if not self.widget:
            return
        if self.on:
            val = win32con.BST_CHECKED
        else:
            val = win32con.BST_UNCHECKED
        win32gui.SendMessage(self.widget, win32con.BM_SETCHECK, val, 0)

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        if (wParam >> 16) != win32con.BN_CLICKED:
            return
        val = win32gui.SendMessage(self.widget, win32con.BM_GETSTATE, 0, 0)
        val = val & win32con.BST_CHECKED
        if val == self.on:
            return
        self.modify(on=val)
        #self.do_action()
        send(self, 'click')


class CheckBox(ToggleButtonMixin, AbstractCheckBox):
    _wndclass = "BUTTON"
    #_text = "mswCheckBox"
    _win_style = win32con.BS_AUTOCHECKBOX | win32con.WS_CHILD


class RadioButton(ToggleButtonMixin, AbstractRadioButton):
    _wndclass = "BUTTON"
    #_text = "mswCheckBox"
    _win_style = win32con.BS_AUTORADIOBUTTON | win32con.WS_CHILD
    
    def _ensure_created(self):
        # The first radiobutton in a group must have the wxRB_GROUP style
        if self._group and 0 == self._group._items.index(self):
            self._win_style |= win32con.WS_GROUP
        return ToggleButtonMixin._ensure_created(self)

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        if (wParam >> 16) != win32con.BN_CLICKED:
            return
        #val = win32gui.SendMessage(self.widget, win32con.BM_GETSTATE, 0, 0)
        #val = val & win32con.BST_CHECKED
        #if val == self.on:
        #    return
        #self.modify(on=val)
        #self.do_action()
        if self.group is not None:
            self.group.modify(value=self.value)
        send(self, 'click')

##################################################################

### IMPORTANT NOTE: Until the 'copy-paste' structure has been
### fixed (e.g. with a common superclass), fixes in one of these
### text classes should probably also be done in the other.

class TextField(ComponentMixin, AbstractTextField):
    _wndclass = "EDIT"
    #_text = "mswTextField"
    _win_style = win32con.ES_NOHIDESEL | win32con.ES_AUTOHSCROLL | \
                 win32con.WS_CHILD | win32con.WS_BORDER
    _win_style_ex = win32con.WS_EX_CLIENTEDGE

    def _to_native(self, text):
        return text.replace('\n', '\r\n')

    def _from_native(self, text):
        return text.replace('\r\n', '\n')

    def _backend_text(self):
        if self.widget:
            return self._from_native(win32gui.GetWindowText(self.widget))

    #def _set_text(self, text):
    #    if self.widget:
    #        win32gui.SetWindowText(self.widget, self._to_native(text))

    def _backend_selection(self):
        #log("TextField._backend_selection")
        if self.widget:
            result = win32gui.SendMessage(self.widget,
                                          win32con.EM_GETSEL,
                                          0, 0)
            start, end = result & 0xFFFF, result >> 16
            #log("    start,end=%s,%s"%(start,end))
            # under windows, the natice widget contains
            # CRLF line separators
            text = self.text
            start -= text[:start].count('\n')
            end -= text[:end].count('\n')
            return start, end
            
    def _ensure_text(self):
        if self.widget:
            # avoid recursive updates
            if str(self._text) != self._backend_text():
                win32gui.SetWindowText(self.widget, self._to_native(str(self._text)))
        
    def _ensure_selection(self):
        #log("TextField._ensure_selection")
        if self.widget:
            start, end = self._selection
            text = self.text
            start += text[:start].count('\n')
            end += text[:end].count('\n')
            #log("    start,end=%s,%s"%(start,end))
            win32gui.SendMessage(self.widget,
                                 win32con.EM_SETSEL,
                                 start, end)

    def _ensure_editable(self):
        if self.widget:
            if self._editable:
                win32gui.SendMessage(self.widget,
                                     win32con.EM_SETREADONLY,
                                     0, 0)
            else:
                win32gui.SendMessage(self.widget,
                                     win32con.EM_SETREADONLY,
                                     1, 0)

##    def _ensure_events(self):
##        if self.widget:
##            EVT_TEXT_ENTER(self.widget, self._msw_id, self._msw_enterkey)

##    def _msw_enterkey(self, event):
##        self.do_action()

    def _get_msw_text(self):
        # return the text required for creation
        return self._to_native(str(self._text))

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        # HIWORD(wParam): notification code
        if (wParam >> 16) == win32con.EN_KILLFOCUS:
            self.modify(selection=self._backend_selection())
            self.modify(text=self._backend_text())


# FIXME: Inheriting TextField overrides TextArea defaults.
#        This is a temporary fix. (mlh20011222)
import anygui.Defaults # Deleted at the end of the module [xyzzy42]
class TextArea(anygui.Defaults.TextArea, TextField, AbstractTextArea):
    _win_style = TextField._win_style | win32con.ES_MULTILINE | \
                 win32con.ES_AUTOVSCROLL | win32con.ES_WANTRETURN

##################################################################

class ContainerMixin(ComponentMixin):
    def __init__(self):
        self.widget_map = {} # maps child window handles to instances
    
    def _finish_creation(self):
        #log("ContainerMixin._finish_creation %s"%self)
        for comp in self._contents:
            #log("  Adding %s"%comp)
            self.widget_map[comp.widget] = comp

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        #log("ContainerMixin _WM_COMMAND called for %s"%self)
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        app = application()
        try:
            child_window = self.widget_map[lParam]
        except KeyError:
            #log("NO SUCH CHILD WINDOW %s"%lParam)
            # we receive (when running test_textfield.py)
            # EN_CHANGE (0x300) and EN_UPDATE (0x400) notifications
            # here even before the call to CreateWindow returns.
            return
        #log("Dispatching to child %s"%child_window)
        child_window._WM_COMMAND(hwnd, msg, wParam, lParam)

    def _WM_SIZE(self, hwnd, msg, wParam, lParam):
        w, h = lParam & 0xFFFF, lParam >> 16
        dw = w - self._width
        dh = h - self._height
        self.modify(width=w)
        self.modify(height=h)
        self.resized(dw, dh)


class Frame(ContainerMixin, AbstractFrame):
    _win_style = win32con.WS_CHILD
    _win_style_ex = 0

    def __init__(self, *args, **kw):
        ContainerMixin.__init__(self)
        AbstractFrame.__init__(self, *args, **kw)

    def _get_msw_text(self):
        return ""

    def _finish_creation(self):
        ContainerMixin._finish_creation(self)
        AbstractFrame._finish_creation(self)
'''
# END COMMENT - search for JKJKJK


class WindowWrapper(ComponentWrapper):

    _win_style = win32con.WS_OVERLAPPEDWINDOW | win32con.WS_CLIPCHILDREN
    _win_style_ex = 0

    def __init__(self,*args,**kws):
        ComponentWrapper.__init__(self,*args,**kws)
        self.widget_map = {}

    def setGeometry(self,x,y,width,height):
        if self.noWidget(): return
        # take account for title bar and borders
        import win32api
        win32gui.SetWindowPos(self.widget,
                              0,
                              x, y,
                              width \
                              + 2*win32api.GetSystemMetrics(win32con.SM_CXFRAME),
                              height \
                              + win32api.GetSystemMetrics(win32con.SM_CYCAPTION) \
                              + 2*win32api.GetSystemMetrics(win32con.SM_CYFRAME),
                              win32con.SWP_NOACTIVATE | win32con.SWP_NOZORDER)

    #def _ensure_events(self):
    #    pass

    def setContainer(self,container):
        if not application().isRunning(): return
        if container is None: return
        if self.noWidget():
            self.create()
        self.proxy.push(blocked=['container'])
        # Ensure contents are properly created.
        for comp in self.proxy.contents:
            comp.container = self.proxy
        win32gui.ShowWindow(self.widget, win32con.SW_HIDE)
        win32gui.UpdateWindow(self.widget)


    def setTitle(self,title):
        if self.noWidget(): return
        win32gui.SetWindowText(self.widget, title)

    def getTitle(self):
        win32gui.GetWindowText(self.widget, title)

    def widgetSetUp(self):
        Application.widget_map[self.widget] = self
        win32gui.SendMessage(self.widget,
                             win32con.WM_SETFONT,
                             self._hfont,
                             0)
    def _WM_CLOSE(self, hwnd, msg, wParam, lParam):
        self.destroy()
        application().remove(self.proxy)
        return 1

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        #log("ContainerMixin _WM_COMMAND called for %s"%self)
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        app = application()
        try:
            child_window = self.widget_map[lParam]
        except KeyError:
            #log("NO SUCH CHILD WINDOW %s"%lParam)
            # we receive (when running test_textfield.py)
            # EN_CHANGE (0x300) and EN_UPDATE (0x400) notifications
            # here even before the call to CreateWindow returns.
            return
        #log("Dispatching to child %s"%child_window)
        child_window._WM_COMMAND(hwnd, msg, wParam, lParam)

    def _WM_SIZE(self, hwnd, msg, wParam, lParam):
        w, h = lParam & 0xFFFF, lParam >> 16
        #dw = w - self._width
        #dh = h - self._height
        #self.setWidth(width=w)
        #self.setHeight(height=h)
        #self.resized(dw, dh)

################################################################

class Frame: pass

class Application(AbstractApplication):
    widget_map = {} # maps top level window handles to window instances
    _wndclass = None

    def __init__(self):
        AbstractApplication.__init__(self)
        if not self._wndclass:
            self._register_class()
        WindowWrapper._wndclass = self._wndclass
        Frame._wndclass = self._wndclass
        global _app
        _app = self

    def _register_class(self):
        # register a window class for toplevel windows.
        wndclass = win32gui.WNDCLASS()
        wndclass.hbrBackground = win32con.COLOR_BTNFACE + 1
        wndclass.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wndclass.hIcon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        wndclass.lpszClassName = "msw.anygui.PythonWindow"
        wndclass.lpfnWndProc = self._wndproc
        self.__class__._wndclass = win32gui.RegisterClass(wndclass)

    def _wndproc(self, hwnd, msg, wParam, lParam):
        #log("_wndproc called with %s,%s,%s,%s"%(hwnd,msg,wParam,lParam))
        try:
            window = self.widget_map[hwnd]
        except:
            #log("NO WINDOW TO DISPATCH???")
            return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)
        # there should probably be a better way to dispatch messages
        if msg == win32con.WM_DESTROY:
            app = application()
            app.remove(window)
            if not app._windows:
                win32gui.PostQuitMessage(0)
        if msg == win32con.WM_CLOSE:
            return window._WM_CLOSE(hwnd, msg, wParam, lParam)
        if msg == win32con.WM_SIZE:
            return window._WM_SIZE(hwnd, msg, wParam, lParam)
        if msg == win32con.WM_COMMAND:
            #log("Dispatching command to %s"%window)
            return window._WM_COMMAND(hwnd, msg, wParam, lParam)
        return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)
        
    def internalRun(self):
        win32gui.PumpMessages()

    def internalRemove(self):
        if not self._windows:
            win32gui.PostQuitMessage(0)

################################################################

# FIXME: Part of temporary fix earlier in file. (Search for xyzzy42)
#del anygui.Defaults # Imported earlier

if __name__ == '__main__':
    from anygui import *

    app = Application()
    win = Window(title = "A Standard Window",
                 width = 300, height = 200)
    win.show()
    application().run()
