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
  FrameWrapper
  RadioButtonWrapper
  CheckBoxWrapper
'''.split()

from anygui.Utils import log
from anygui.Applications import AbstractApplication
from anygui.Wrappers import AbstractWrapper
from anygui.Events import *
from anygui import application

################################################################
from dynwin import windll, structob, gencb
user32 = windll.module('user32')
gdi32 = windll.module('gdi32')
kernel32 = windll.module('kernel32')

ANSI_VAR_FONT=12
BM_GETSTATE=0xf2
BM_SETCHECK=0xf1
BN_CLICKED=0
BS_AUTOCHECKBOX=3
BS_AUTORADIOBUTTON=9
BS_PUSHBUTTON=0
BST_CHECKED=1
BST_UNCHECKED=0
COLOR_BTNFACE=15
EM_GETSEL=176
EM_SETREADONLY=207
EM_SETSEL=177
EN_KILLFOCUS=512
ES_AUTOHSCROLL=128
ES_AUTOVSCROLL=64
ES_MULTILINE=4
ES_NOHIDESEL=256
ES_WANTRETURN=4096
FORMAT_MESSAGE_FROM_SYSTEM=0x00001000
FORMAT_MESSAGE_IGNORE_INSERTS=0x00000200
IDC_ARROW=0x7f00
IDI_APPLICATION=0x7f00
IMAGE_BITMAP=0
LB_ADDSTRING=0x180
LB_GETCURSEL=0x188
LB_RESETCONTENT=0x184
LB_SETCURSEL=0x186
LBN_SELCHANGE=0x1
LBS_NOINTEGRALHEIGHT=0x0100
LBS_NOTIFY=0x1
LR_DEFAULTSIZE=64
LR_LOADFROMFILE=16
PBS_SMOOTH=1
SM_CXFRAME=32
SM_CYCAPTION=4
SM_CYFRAME=33
SS_LEFT=0
SW_HIDE=0
SW_SHOWNORMAL=1
SWP_NOACTIVATE=16
SWP_NOZORDER=4
WM_CLOSE=16
WM_COMMAND=273
WM_DESTROY=2
WM_PAINT=15
WM_SETFONT=48
WM_SIZE=5
WM_USER=1024
WS_BORDER=0x800000
WS_CHILD=0x40000000
WS_CLIPCHILDREN=0x2000000
WS_EX_CLIENTEDGE=0x200
WS_GROUP=0x20000
WS_OVERLAPPEDWINDOW=0xcf0000
WS_VISIBLE=0x10000000
WS_VSCROLL=0x200000

PBM_SETPOS=WM_USER+2
PBM_SETRANGE=WM_USER+1

GetLastError = kernel32.GetLastError
_verbose=0
if _verbose:
    from anygui.Utils import log, setLogFile
    setLogFile('/tmp/dbg.txt')

def _lastErrorMessage(n=None):
    msg = windll.cstring('',512)
    kernel32.FormatMessageA(
            FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
            0,
            n is None and GetLastError() or n,
            0,
            msg.address(),
            len(msg)-1,
            0
            )
    return repr(msg)[1:-1]

class t_rect(structob.struct_object):
    oracle = structob.Oracle (
        'tuple rect',
        'N4l',
        ('rect',)
        )

class t_point(structob.struct_object):
    oracle = structob.Oracle (
        'tuple point',
        'N2l',
        ('point',)
        )

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
    _hfont = gdi32.GetStockObject(ANSI_VAR_FONT)

    def __init__(self,*args,**kws):
        self._width = 0
        self._height = 0
        AbstractWrapper.__init__(self,*args,**kws)
        self.setConstraints('container','x','y','width','height',
                            'text','selection','geometry','visible')

    def widgetFactory(self,*args,**kws):
        app = application()
        if hasattr(self.proxy.container,'wrapper'):
            parent = self.proxy.container.wrapper.widget
        else:
            parent = 0
        t = self._wndclass
        if t is None:
            self._i_wndclass = 0
        elif type(t) is type(''):
            self._i_wndclass = windll.cstring(t)
        elif type(t) is type(0):
            self._i_wndclass = t
        widget = user32.CreateWindowEx(self._win_style_ex,
                                         self._i_wndclass,
                                         0,
                                         self._win_style,
                                         0,
                                         0,
                                         10,
                                         10,
                                         parent,
                                         0, # hMenu
                                         0, # hInstance
                                         0)
        app.widget_map[widget] = self
        return widget

    def widgetSetUp(self):
        if _verbose: log('widgetSetup',str(self))
        self.proxy.container.wrapper.widget_map[self.widget] = self
        self.proxy.push(blocked=['container'])
        user32.SendMessage(self.widget,
                             WM_SETFONT,
                             self._hfont,
                             0)
        self.setVisible(1)

    def getGeometry(self):
        r = t_rect()
        user32.GetWindowRect(self.widget,r)
        l,t,r,b = r.rect
        w = r-l
        h = b-t

        if _verbose: log(str(self),'getGeometry',l,t,w,h)
        try:
            p = t_point()
            p.point = l,t
            user32.ScreenToClient(self.proxy.container.wrapper.widget,p)
            l,t = p.point
            if _verbose: log('   -->', l,t,w,h)
        except AttributeError:
            pass
        except:
            import traceback
            traceback.print_exc(1)
        return l,t,w,h

    def setX(self,x):
        if not self.widget: return
        ox,y,w,h = self.getGeometry()
        self.setGeometry(x,y,w,h)

    def setY(self,y):
        if not self.widget: return
        x,oy,w,h = self.getGeometry()
        self.setGeometry(x,y,w,h)

    def setWidth(self,width):
        if not self.widget: return
        x,y,ow,h = self.getGeometry()
        self.setGeometry(x,y,width,h)

    def setHeight(self,height):
        if not self.widget: return
        x,y,w,oh = self.getGeometry()
        self.setGeometry(x,y,w,height)

    def setSize(self,width,height):
        if not self.widget: return
        x,y,w,h = self.getGeometry()
        self.setGeometry(x,y,width,height)

    def setPosition(self,x,y):
        if not self.widget: return
        ox,oy,w,h = self.getGeometry()
        self.setGeometry(x,y,w,h)

    def setGeometry(self,x,y,width,height):
        if self.widget:
            if _verbose: log(str(self),'setGeometry', x,y,width,height)
            user32.SetWindowPos(self.widget, 0, x, y, width, height, SWP_NOACTIVATE | SWP_NOZORDER)
            user32.UpdateWindow(self.widget)

    def setVisible(self,visible):
        if self.widget:
            if _verbose: log(str(self),'setVisible', visible, self.widget)
            user32.ShowWindow(self.widget, visible and SW_SHOWNORMAL or SW_HIDE)

    def setEnabled(self,enabled):
        if self.widget:
            user32.EnableWindow(self.widget, enabled and 1 or 0)

    def destroy(self):
        if self.proxy.container:
            try:
                del self.proxy.container.wrapper.widget_map[self.widget]
            except:
                pass
        if self.widget:
            try:
                user32.DestroyWindow(self.widget)
            except:
                pass
            self.widget = None

    def setText(self,text):
        if not self.widget: return
        if _verbose: log("%s.SetWindowText('%s'(%s)) hwnd=%s(%s) self=%s" % (self.__class__.__name__,text,type(text),self.widget,type(self.widget),self))
        self._i_text = windll.cstring(text)
        user32.SetWindowTextA(self.widget,self._i_text)

    def getText(self):
        if not self.widget: return
        n = user32.GetWindowTextLength(self.widget)
        if _verbose: log('GetWindowText n=',n)
        t = windll.cstring('',n+1)
        r = user32.GetWindowText(self.widget,t.address(),n+1)
        if _verbose: log('GetWindowText n=%d r=%d s=%s'%(n,r,t.trunc()))
        return t.trunc()

    def setContainer(self, container):
        if container is None:
            try:
                self.destroy()
            except:
                pass
            return
        parent = container.wrapper.widget
        if parent:
            self.destroy()
            self.create(parent)
            self.proxy.push(blocked=['container'])

    def enterMainLoop(self):
        self.proxy.push()

    def _WM_PAINT(self, hwnd, msg, wParam, lParam):
        return user32.DefWindowProc(hwnd, msg, wParam, lParam)

##################################################################
class LabelWrapper(ComponentWrapper):
    _wndclass = "STATIC"
    _win_style = SS_LEFT | WS_CHILD

##################################################################
class ProgressBarWrapper(ComponentWrapper):
    _wndclass = "msctls_progress32"
    _win_style = WS_VISIBLE | WS_CHILD | PBS_SMOOTH

    def setPos(self,pos):
        if not self.widget: return
        user32.SendMessage(self.widget, PBM_SETRANGE, 0, 0xffff0000)
        return user32.SendMessage(self.widget, PBM_SETPOS, int(pos*0xffff), 0)

##################################################################
class ButtonWrapper(ComponentWrapper):
    _wndclass = "BUTTON"
    _win_style = BS_PUSHBUTTON | WS_CHILD

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        #log("Button._WM_COMMAND called, looking for %s==%s"%(wParam>>16,BN_CLICKED))
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        if (wParam >> 16) == BN_CLICKED:
            #self.do_action()
            send(self.proxy, 'click')

##################################################################
class ListBoxWrapper(ComponentWrapper):
    _wndclass = "LISTBOX"
    _win_style = WS_CHILD | WS_VSCROLL | WS_BORDER | LBS_NOTIFY | LBS_NOINTEGRALHEIGHT
    _win_style_ex = WS_EX_CLIENTEDGE

    def getSelection(self):
        if not self.widget: return
        return user32.SendMessage(self.widget,
                                    LB_GETCURSEL,
                                    0,
                                    0)

    def setItems(self,items):
        if not self.widget: return
        user32.SendMessage(self.widget,
                             LB_RESETCONTENT, 0, 0)
        for item in map(str, list(items)):
            # FIXME: This doesn't work! Items get jumbled...
            user32.SendMessage(self.widget,
                                 LB_ADDSTRING,
                                 0,
                                 windll.cstring(item))


    def setSelection(self,selection):
        if not self.widget: return
        user32.SendMessage(self.widget,
                             LB_SETCURSEL,
                             selection, 0)

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        if wParam >> 16 == LBN_SELCHANGE:
            #self.do_action()
            send(self.proxy, 'select')

##################################################################
class ToggleButtonWrapper(ComponentWrapper):

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        if (wParam >> 16) == BN_CLICKED:
            #self.do_action()
            send(self.proxy, 'click')

    def setOn(self,on):
        if not self.widget:
            return
        if on:
            val = BST_CHECKED
        else:
            val = BST_UNCHECKED
        user32.SendMessage(self.widget, BM_SETCHECK, val, 0)
        self._on = on

    def getOn(self):
        val = user32.SendMessage(self.widget, BM_GETSTATE, 0, 0)
        val = val & BST_CHECKED
        if val: return 1
        return 0

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        if (wParam >> 16) != BN_CLICKED:
            return
        send(self.proxy, 'click')

class CheckBoxWrapper(ToggleButtonWrapper):
    _wndclass = "BUTTON"
    _win_style = BS_AUTOCHECKBOX | WS_CHILD

class RadioButtonWrapper(ToggleButtonWrapper):
    _wndclass = "BUTTON"
    _win_style = BS_AUTORADIOBUTTON | WS_CHILD

    def __init__(self,*args,**kws):
        self._value = -2
        ToggleButtonWrapper.__init__(self,*args,**kws)

    def widgetFactory(self,*args,**kws):
        # The first radiobutton in a group must have the wxRB_GROUP style
        if self.proxy.group and self.proxy.group._items.index(self.proxy) == 0:
            self._win_style |= WS_GROUP
        return ToggleButtonWrapper.widgetFactory(self,*args,**kws)

    def setGroup(self,group):
        if group == None:
            return
        if self.proxy not in group._items:
            group._items.append(self.proxy)

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        if (wParam >> 16) != BN_CLICKED:
            return
        send(self.proxy, 'click')

##################################################################

### IMPORTANT NOTE: Until the 'copy-paste' structure has been
### fixed (e.g. with a common superclass), fixes in one of these
### text classes should probably also be done in the other.

##################################################################

# END COMMENT - search for JKJKJK

class TextFieldWrapper(ComponentWrapper):
    _wndclass = "EDIT"
    _win_style = ES_NOHIDESEL | ES_AUTOHSCROLL | \
                 WS_CHILD | WS_BORDER
    _win_style_ex = WS_EX_CLIENTEDGE

    def _to_native(self, text):
        return text.replace('\n', '\r\n')

    def _from_native(self, text):
        return text.replace('\r\n', '\n')

    def getText(self):
        if not self.widget: return
        return self._from_native(ComponentWrapper.getText(self))

    def setText(self, text):
        if not self.widget: return
        if text==self.getText(): return
        ComponentWrapper.setText(self, self._to_native(text))

    def getSelection(self):
        #log("TextField._backend_selection")
        if not self.widget: return
        result = user32.SendMessage(self.widget,
                                      EM_GETSEL,
                                      0, 0)
        start, end = result & 0xFFFF, result >> 16
        #log("    start,end=%s,%s"%(start,end))
        # under windows, the natice widget contains
        # CRLF line separators
        text = self.getText()
        start -= text[:start].count('\n')
        end -= text[:end].count('\n')
        return start, end

    def setSelection(self,selection):
        #log("TextField._ensure_selection")
        if not self.widget: return
        start, end = selection
        text = self.getText()
        start += text[:start].count('\n')
        end += text[:end].count('\n')
        #log("    start,end=%s,%s"%(start,end))
        user32.SendMessage(self.widget,
                             EM_SETSEL,
                             start, end)

    def setEditable(self,editable):
        if self.widget:
            user32.SendMessage(self.widget, EM_SETREADONLY, not editable and 1 or 0, 0)

##    def _ensure_events(self):
##        if self.widget:
##            EVT_TEXT_ENTER(self.widget, self._msw_id, self._msw_enterkey)

##    def _msw_enterkey(self, event):
##        self.do_action()

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        pass

# FIXME: Inheriting TextField overrides TextArea defaults.
#        This is a temporary fix. (mlh20011222)
class TextAreaWrapper(TextFieldWrapper):
    _win_style = TextFieldWrapper._win_style | ES_MULTILINE | \
                 ES_AUTOVSCROLL | ES_WANTRETURN


class ContainerMixin:
    def __init__(self,*args,**kws):
        self.widget_map = {} # maps child window handles to instances

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

class FrameWrapper(ComponentWrapper,ContainerMixin):
    _win_style = WS_CHILD
    _wndclass = None

    def __init__(self,*args,**kws):
        ContainerMixin.__init__(self)
        ComponentWrapper.__init__(self,*args,**kws)


    def setContainer(self, *args, **kws):
        """
        OK, this probably needs to be pulled into a mixin heritable by
        various backends.

        Ensure all contents are properly created. This looks like it could
        be handled at the Proxy level, but it probably *shouldn't* be -
        it's handling a Tk-specific requirement about the order in which
        widgets must be created. (I did it the Proxy way too. This way
        is definitely "the simplest thing that could possibly work.") - jak
        """
        ComponentWrapper.setContainer(self, *args, **kws)
        for component in self.proxy.contents:
            component.container = self.proxy

    def _WM_SIZE(self, hwnd, msg, wParam, lParam):
        # Proxy handles resizing.
        pass

##################################################################
class ImageWrapper(ComponentWrapper):
    _win_style = WS_CHILD | WS_VISIBLE
    _wndclass = "dw.anygui.PythonWindow"

    def _WM_PAINT(self, hwnd, msg, wParam, lParam):
        if not self.widget: return
        if _verbose: log('in dwImage _WM_PAINT')
        r = ComponentWrapper._WM_PAINT(self, hwnd, msg, wParam, lParam)
        self.draw()
        return r

    def setVisible(self,visible):
        if not self.widget: return
        self.draw()
        ComponentWrapper.setVisible(self,visible)

    def draw(self,*arg,**kw):
        if not self.widget: return
        dc = user32.GetDC(self.widget)
        name = windll.cstring('/python/rlextra/distro/demo/RLImage.bmp')
        if _verbose: log('in draw widget=%s dc=%s dim=%sx%s' % (hex(self.widget),hex(dc),self.proxy.width,self.proxy.height))
        try:
            bmp=user32.LoadImage(0,name,IMAGE_BITMAP,0,0,LR_DEFAULTSIZE|LR_LOADFROMFILE)
        except:
            import traceback
            traceback.print_exc()
            from anygui.backends.dwgui import _lastErrorMessage 
            log(_lastErrorMessage())
        memdc = gdi32.CreateCompatibleDC(dc)
        old = gdi32.SelectObject(memdc,bmp)
        gdi32.BitBlt(dc,0,0,self.proxy.width,self.proxy.height,memdc,0,0,0x00CC0020)
        gdi32.SelectObject(memdc,old)
        gdi32.DeleteDC(memdc)
        gdi32.DeleteObject(bmp)

class WindowWrapper(ContainerMixin,ComponentWrapper):
    _win_style = WS_OVERLAPPEDWINDOW | WS_CLIPCHILDREN
    _extraWidth = 2*user32.GetSystemMetrics(SM_CXFRAME)
    _extraHeight = user32.GetSystemMetrics(SM_CYCAPTION) + 2*user32.GetSystemMetrics(SM_CYFRAME)

    def __init__(self,*args,**kws):
        ComponentWrapper.__init__(self,*args,**kws)
        self.widget_map = {}

    def getGeometry(self):
        r = t_rect()
        user32.GetWindowRect(self.widget,r)
        l,t,r,b = r.rect
        w = r-l-self._extraWidth
        h = b-t-self._extraHeight
        if _verbose: log(str(self),'getGeometry WindowWrapper:', l,t,w,h)
        return l,t,w,h

    def setGeometry(self,x,y,width,height):
        if not self.widget: return
        if _verbose: log('WindowWrapper: setGeometry',x,y,width,height)
        # take account for title bar and borders
        user32.SetWindowPos(self.widget,
                              0,
                              x, y,
                              width + self._extraWidth,
                              height + self._extraHeight,
                              SWP_NOACTIVATE | SWP_NOZORDER)
        user32.UpdateWindow(self.widget)

    def setContainer(self,container):
        if not application().isRunning(): return
        if container is None: return
        if not self.widget:
            self.create()
        user32.ShowWindow(self.widget, SW_HIDE)
        user32.UpdateWindow(self.widget)
        self.proxy.push(blocked=['container'])
        # Ensure contents are properly created.
        for comp in self.proxy.contents:
            comp.container = self.proxy

    def setTitle(self,title):
        if not self.widget: return
        if title:
            self._i_text = windll.cstring(title)
            user32.SetWindowTextA(self.widget, self._i_text)

    def getTitle(self):
        return ComponentWrapper.getText(self)

    def widgetSetUp(self):
        Application.widget_map[self.widget] = self
        user32.SendMessage(self.widget,
                             WM_SETFONT,
                             self._hfont,
                             0)
    def _WM_SIZE(self, hwnd, msg, wParam, lParam):
        w, h = lParam & 0xFFFF, lParam >> 16
        if _verbose: log('WindowWrapper: _WM_SIZE _width,_height,w,h=',self._width,self._height,w,h,)
        if self._width==0 and self._height==0:
            # This will be the case when the widget is first
            # created. We need to ensure the contents get
            # reasonable geometries before we start sliding
            # them around, so ignore the initial resize.
            dw=0
            dh=0
        else:
            dw = w - self._width
            dh = h - self._height
        if _verbose: log('dw,dh=',dw,dh)

        self._width = w
        self._height = h
        if (dw,dh) == (0,0): return
        self.proxy.resized(dw,dh)

    def _WM_CLOSE(self, hwnd, msg, wParam, lParam):
        self.destroy()
        application().remove(self.proxy)
        return 1

################################################################
class Application(AbstractApplication):
    widget_map = {} # maps top level window handles to window instances
    _wndclass = None

    def __init__(self):
        AbstractApplication.__init__(self)
        if not self._wndclass: self._register_class()
        WindowWrapper._wndclass = self._wndclass
        FrameWrapper._wndclass = self._wndclass
        global _app
        _app = self

    def _register_class(self):
        class WNDCLASS(structob.struct_object):
            oracle = structob.Oracle (
                'window class information',
                'Nllllllllll',
                ('style',
                 'lpfnWndProc',
                 'cls_extra',
                 'wnd_extra',
                 'hInst',
                 'hIcon',
                 'hCursor',
                 'hbrBackground',
                 'menu_name',
                 'lpzClassName',
                 )
                )
        self._class_name = windll.cstring("dw.anygui.PythonWindow")
        self.__wndproc = gencb.generated_callback('llll',self._wndproc)
        # register a window class for toplevel windows.
        wc = WNDCLASS()
        wc.hbrBackground = COLOR_BTNFACE + 1
        wc.hCursor = user32.LoadCursor(0, IDC_ARROW)
        wc.hIcon = user32.LoadIcon(0, IDI_APPLICATION)
        wc.lpzClassName = self._class_name.address()
        wc.lpfnWndProc = self.__wndproc.address
        wc.hInst = kernel32.GetModuleHandle(0)
        self._wc = wc
        user32.UnregisterClass(wc.lpzClassName,0)
        self.__class__._wndclass = user32.RegisterClass(wc)
        assert self.__class__._wndclass, "RegisterClass --> %d=%s ie\n%s" % (GetLastError(), hex(GetLastError()), _lastErrorMessage())

    def _wndproc(self, hwnd, msg, wParam, lParam):
        if _verbose: log("%s._wndproc called with %s,%s,%s,%s"%(self.__class__.__name__,hex(hwnd),hex(msg),hex(wParam),hex(lParam)))
        try:
            window = self.widget_map[hwnd]
        except:
            if _verbose: log("\tNO WINDOW TO DISPATCH???")
            return user32.DefWindowProc(hwnd, msg, wParam, lParam)
        # there should probably be a better way to dispatch messages
        if msg == WM_DESTROY:
            app = application()
            app.remove(window)
            app.internalRemove()
        if msg == WM_CLOSE:
            if _verbose: log("\t_WM_COMMAND to %s %s" % (window.__class__.__name__,window))
            return window._WM_CLOSE(hwnd, msg, wParam, lParam)
        if msg == WM_SIZE:
            if _verbose: log("\t_WM_SIZE to %s %s" % (window.__class__.__name__,window))
            return window._WM_SIZE(hwnd, msg, wParam, lParam)
        if msg == WM_COMMAND:
            if _verbose: log("\t_WM_COMMAND to %s %s" % (window.__class__.__name__,window))
            return window._WM_COMMAND(hwnd, msg, wParam, lParam)
        if msg == WM_PAINT:
            if _verbose: log("\t_WM_PAINT to %s %s" % (window.__class__.__name__,window))
            return window._WM_PAINT(hwnd, msg, wParam, lParam)
        if _verbose: log("\tDefaultProc() %s %s" % (window.__class__.__name__,window))
        return user32.DefWindowProc(hwnd, msg, wParam, lParam)

    def internalRun(self):
        class MSG (structob.struct_object):
            oracle = structob.Oracle (
                'windows message',
                'Nlllllll',
                ('hwnd',
                 'message',
                 'wParam',
                 'lParam',
                 'time',
                 'x',
                 'y')
                )
        msg = MSG()
        while self._windows and user32.GetMessage(msg, 0, 0, 0):
            user32.TranslateMessage(msg)
            user32.DispatchMessage(msg)

    def internalRemove(self):
        if not self._windows:
            if _verbose: log('PostQuitMessage(0)')
            user32.PostQuitMessage(0)

################################################################
if __name__ == '__main__':
    from anygui import *
    app = Application()
    win = Window(title = "A Standard Window",
                 width = 300, height = 200)
    win.show()
    application().run()
