#A win32 backend based on Thomas Heller's ctypes module.
from anygui.backends import *

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
  ProgressBarWrapper
  ImageWrapper
  Resource
  inlineResource
'''.split()

from anygui.Applications import AbstractApplication
from anygui.Wrappers import AbstractWrapper
from anygui.Events import *
from anygui import application
from anygui.Utils import log, setLogFile, logTraceback

################################################################
from ctypes import CDLL, _DLLS, _DynFunction, CFunction, c_string, Structure, WinError, byref

_apiMode = 'A'
def _to_native(text):
    return text.replace('\n', '\r\n')

def _from_native(text):
    return text.replace('\r\n', '\n')

class WinDLL(CDLL):
    
    def __getattr__(self, name):
        try:
            func = _DynFunction(name, self)
        except:
            func = _DynFunction(name+_apiMode, self)
        setattr(self, name, func)
        return func
windll = _DLLS(WinDLL)
user32 = windll.user32
gdi32 = windll.gdi32
kernel32 = windll.kernel32

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

_verbose=0
if _verbose:
    setLogFile('/tmp/dbg.txt')

class t_rect(Structure):
    _fields_=(('left','i'),('top','i'),('right','i'),('bottom','i'))

class t_point(Structure):
    _fields_=(('x','i'),('y','i'))

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
        if self.proxy.container and hasattr(self.proxy.container,'wrapper'):
            parent = self.proxy.container.wrapper.widget
        else:
            parent = 0
        t = self._wndclass
        if t is None:
            self._i_wndclass = 0
        elif type(t) is type(''):
            self._i_wndclass = c_string(t)
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
        user32.SendMessage(self.widget,
                             WM_SETFONT,
                             self._hfont,
                             0)
        self.setVisible(1)

    def internalProd(self):
        if _verbose: log('internalProd',str(self))
        self.proxy.push(blocked=['container'])

    def getGeometry(self):
        if not self.widget: return 0,0,0,0
        r = t_rect()
        user32.GetWindowRect(self.widget,byref(r))
        l,t,r,b = r.left, r.top, r.right, r.bottom
        w = r-l
        h = b-t

        if _verbose: log(str(self),'getGeometry',l,t,w,h)
        try:
            p = t_point()
            p.x, p.y = l,t
            user32.ScreenToClient(self.proxy.container.wrapper.widget,byref(p))
            l,t = p.x, p.y
            if _verbose: log('   -->', l,t,w,h)
        except AttributeError:
            pass
        except:
            logTraceback(None)
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
        if getattr(self.proxy,'container',None):
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
        if _verbose: log("%s.SetWindowText('%s'(%s)) hwnd=%s(%s) self=%s" % (self.__class__.__name__,text,type(text),self.widget,type(self.widget),str(self)))
        user32.SetWindowText(self.widget,c_string(_to_native(text)))

    def _getText(self):
        'return native text'
        n = user32.GetWindowTextLength(self.widget)
        t = c_string('\000'*(n+1))
        user32.GetWindowText(self.widget,t,n+1)
        return t.value

    def getText(self):
        if self.widget: return _from_native(self._getText())

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
        return (wParam >> 16)!=BN_CLICKED and -1 or send(self.proxy, 'click')

##################################################################
class ListBoxWrapper(ComponentWrapper):
    _wndclass = "LISTBOX"
    _win_style = WS_CHILD | WS_VSCROLL | WS_BORDER | LBS_NOTIFY | LBS_NOINTEGRALHEIGHT
    _win_style_ex = WS_EX_CLIENTEDGE

    def getSelection(self):
        if self.widget: return user32.SendMessage(self.widget, LB_GETCURSEL, 0, 0)

    def setItems(self,items):
        if not self.widget: return
        user32.SendMessage(self.widget, LB_RESETCONTENT, 0, 0)
        for item in map(str, list(items)):
            # FIXME: This doesn't work! Items get jumbled...
            user32.SendMessage(self.widget, LB_ADDSTRING, 0, c_string(item))


    def setSelection(self,selection):
        if not self.widget: return
        user32.SendMessage(self.widget,
                             LB_SETCURSEL,
                             selection, 0)

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        return  (wParam>>16)!=LBN_SELCHANGE and -1 or send(self.proxy, 'select')

##################################################################
class ToggleButtonWrapper(ButtonWrapper):

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

##################################################################

### IMPORTANT NOTE: Until the 'copy-paste' structure has been
### fixed (e.g. with a common superclass), fixes in one of these
### text classes should probably also be done in the other.

##################################################################

# END COMMENT - search for JKJKJK

class TextFieldWrapper(ComponentWrapper):
    _wndclass = "EDIT"
    _win_style = ES_NOHIDESEL | ES_AUTOHSCROLL | WS_CHILD | WS_BORDER
    _win_style_ex = WS_EX_CLIENTEDGE

    def setText(self, text):
        if self.widget and text!=self.getText():
            ComponentWrapper.setText(self,text)

    def getSelection(self):
        #log("TextField._backend_selection")
        if not self.widget: return
        result = user32.SendMessage(self.widget, EM_GETSEL, 0, 0)
        start, end = result & 0xFFFF, result >> 16
        #log("TextField.getSelection: start,end=%s,%s"%(start,end))
        # under windows, the native widget contains
        # CRLF line separators
        text = self._getText()
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

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        return 0

# FIXME: Inheriting TextField overrides TextArea defaults.
#        This is a temporary fix. (mlh20011222)
class TextAreaWrapper(TextFieldWrapper):
    _win_style = TextFieldWrapper._win_style | ES_MULTILINE | \
                 ES_AUTOVSCROLL | ES_WANTRETURN


class ContainerMixin:
    def __init__(self,*args,**kws):
        self.widget_map = {} # maps child window handles to instances

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        if _verbose: log("ContainerMixin _WM_COMMAND called for %s"%self)
        # lParam: handle of control (or NULL, if not from a control)
        # HIWORD(wParam): notification code
        # LOWORD(wParam): id of menu item, control, or accelerator
        try:
            app = application()
            child_window = self.widget_map[lParam]
        except KeyError:
            if _verbose: log("NO SUCH CHILD WINDOW %s"%lParam)
            # we receive (when running test_textfield.py)
            # EN_CHANGE (0x300) and EN_UPDATE (0x400) notifications
            # here even before the call to CreateWindow returns.
            return -1
        except:
            logTraceback(None)
            return -1
        if _verbose: log("Dispatching to child %s"%child_window)
        return child_window._WM_COMMAND(hwnd, msg, wParam, lParam)

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
        return 0


class Resource:
    inline = None
    def __init__(self,text=None,suffix='.bmp',kind='bitmap'):
        self.text = text
        self.suffix = suffix
        self.kind = kind
        self._handle = None

    def _fn2handle(self,fn):
        if self.kind=='bitmap':
            try:
                self._handle = user32.LoadImage(0,c_string(fn),
                    IMAGE_BITMAP,0,0,LR_DEFAULTSIZE|LR_LOADFROMFILE)
            except:
                logTraceback(None)
                log(WinError())

    def handle(self):
        if not self._handle:
            if self.inline:
                import zlib, base64, tempfile, os
                fn = tempfile.mktemp(self.suffix)
                if _verbose: log('resource:','fn',fn,'kind',self.kind)
                open(fn,'wb').write(zlib.decompress(base64.decodestring(self.text)))
                try:
                    self._fn2handle(fn)
                finally:
                    os.remove(fn)
            else:
                self._fn2handle(self.text)
        if _verbose: log('resource:','-->',self._handle)
        return self._handle

    def __del__(self):
        if self._handle:
            if self.kind=='bitmap':
                gdi32.DeleteObject(self._handle)

class inlineResource(Resource):
    inline = 1

##################################################################
class ImageWrapper(ComponentWrapper):
    _win_style = WS_CHILD | WS_VISIBLE
    _wndclass = "dw.anygui.PythonWindow"

    def _WM_PAINT(self, hwnd, msg, wParam, lParam):
        if not self.widget: return -1
        if _verbose: log('Image _WM_PAINT self.__dict__',self.__dict__)
        r = ComponentWrapper._WM_PAINT(self, hwnd, msg, wParam, lParam)
        self.draw()
        return r

    def draw(self,*arg,**kw):
        if _verbose: log('Image.draw',self.widget,self._image)
        if not self.widget or not self._image: return
        dc = user32.GetDC(self.widget)
        memdc = gdi32.CreateCompatibleDC(dc)
        if _verbose: log('Image.draw dc, memdc',dc,memdc)
        old = gdi32.SelectObject(memdc,self._image.handle())
        gdi32.BitBlt(dc,0,0,self.proxy.width,self.proxy.height,memdc,0,0,0x00CC0020)
        gdi32.SelectObject(memdc,old)
        gdi32.DeleteDC(memdc)

    def setImage(self,image):
        self._image = image

    def getImage(self):
        return self._image

    def _WM_SIZE(self, hwnd, msg, wParam, lParam):
        w, h = lParam & 0xFFFF, lParam >> 16

class WindowWrapper(ContainerMixin,ComponentWrapper):
    _win_style = WS_OVERLAPPEDWINDOW | WS_CLIPCHILDREN
    _extraWidth = 2*user32.GetSystemMetrics(SM_CXFRAME)
    _extraHeight = user32.GetSystemMetrics(SM_CYCAPTION) + 2*user32.GetSystemMetrics(SM_CYFRAME)

    def __init__(self,*args,**kws):
        ContainerMixin.__init__(self)
        ComponentWrapper.__init__(self,*args,**kws)
        self.widget_map = {}

    def getGeometry(self):
        if not self.widget: return 0,0,0,0
        r = t_rect()
        user32.GetWindowRect(self.widget,byref(r))
        l,t,r,b = r.left, r.top, r.right, r.bottom
        w = r-l-self._extraWidth
        h = b-t-self._extraHeight
        if _verbose: log(str(self),'getGeometry WindowWrapper:', l,t,w,h)
        return l,t,w,h

    def setGeometry(self,x,y,width,height):
        if not self.widget: return
        if _verbose: log('WindowWrapper: setGeometry',str(self),self.widget,x,y,width,height,self._extraWidth,self._extraHeight)
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
        if self.widget and title:
            user32.SetWindowText(self.widget, c_string(title))

    def getTitle(self):
        if not self.widget: return
        return ComponentWrapper.getText(self)

    def widgetSetUp(self):
        if _verbose: log('Windowwrapper widgetSetup',str(self),'application()',application(),'isRunning()',application().isRunning(),'widget',getattr(self,'widget',None))
        application().widget_map[self.widget] = self
        user32.SendMessage(self.widget, WM_SETFONT, self._hfont, 0)

    def internalProd(self):
        if _verbose: log('internalProd',str(self))
        self.proxy.push(blocked=['container'])

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
        if (dw,dh)!=(0,0): self.proxy.resized(dw,dh)
        return 0

    def _WM_CLOSE(self, hwnd, msg, wParam, lParam):
        self.destroy()
        application().remove(self.proxy)
        return 0

    def _WM_COMMAND(self, hwnd, msg, wParam, lParam):
        if _verbose: log('WindowWrapper: _WM_COMMAND',str(self),hwnd,msg,wParam,lParam)
        return ContainerMixin._WM_COMMAND(self, hwnd, msg, wParam, lParam)

################################################################
def _dispatch_WM_DESTROY(window,hwnd,msg,wParam,lParam):
    app = application()
    app.remove(window)
    app.internalRemove()
    return 0

def _dispatch_WM_CLOSE(window,hwnd,msg,wParam,lParam):
    return window._WM_CLOSE(hwnd, msg, wParam, lParam)

def _dispatch_WM_SIZE(window,hwnd,msg,wParam,lParam):
    return window._WM_SIZE(hwnd, msg, wParam, lParam)

def _dispatch_WM_COMMAND(window,hwnd,msg,wParam,lParam):
    return window._WM_COMMAND(hwnd, msg, wParam, lParam)

def _dispatch_WM_PAINT(window,hwnd,msg,wParam,lParam):
    return window._WM_PAINT(hwnd, msg, wParam, lParam)

def _dispatch_DEFAULT(window,hwnd,msg,wParam,lParam):
    return user32.DefWindowProc(hwnd, msg, wParam, lParam)

_app=None
class Application(AbstractApplication):
    widget_map = {} # maps top level window handles to window instances
    _wndclass = None
    _dispatch = {
                WM_DESTROY: _dispatch_WM_DESTROY,
                WM_CLOSE: _dispatch_WM_CLOSE,
                WM_SIZE: _dispatch_WM_SIZE,
                WM_COMMAND: _dispatch_WM_COMMAND,
                WM_PAINT: _dispatch_WM_PAINT,
                }

    def __init__(self):
        if not self:
            if _verbose: log('Application.__init__:start',str(self))
            AbstractApplication.__init__(self)
            if not self._wndclass: self._register_class()
            WindowWrapper._wndclass = self._wndclass
            FrameWrapper._wndclass = self._wndclass
            global _app
            _app = self
            if _verbose: log('Application.__init__:end',str(self))

    def __str__(self):
        return '<%s.Application 0x%s>' % (__file__,id(self))

    def __nonzero__(self):
        return _app is not None

    def _register_class(self):
        if _verbose: log('Application._register_class:start',str(self))
        class WINDOWPROC(CFunction):
            _types_ = "iiii"
            _stdcall_ = 1
        class WNDCLASS(Structure):
            _fields_= (
                ('style','i'),
                ('lpfnWndProc',WINDOWPROC),
                ('cls_extra','i'),
                ('wnd_extra','i'),
                ('hInst','i'),
                ('hIcon','i'),
                ('hCursor','i'),
                ('hbrBackground','i'),
                ('menu_name','z'),
                ('lpzClassName','z'),
                )

        # register a window class for our windows.
        wc = WNDCLASS()
        wc.hbrBackground = COLOR_BTNFACE + 1
        wc.hCursor = user32.LoadCursor(0, IDC_ARROW)
        wc.hIcon = user32.LoadIcon(0, IDI_APPLICATION)
        wc.lpzClassName = "dw.anygui.PythonWindow"
        wc.lpfnWndProc = WINDOWPROC(self._wndproc)
        wc.hInst = kernel32.GetModuleHandle(None)
        self._wc = wc
        user32.UnregisterClass(wc.lpzClassName,0)
        self.__class__._wndclass = user32.RegisterClass(byref(wc)) & 0xFFFF
        assert self.__class__._wndclass, "RegisterClass --> %s" % WinError()
        if _verbose: log('Application._register_class:end',str(self))

    def _wndproc(self, hwnd, msg, wParam, lParam):
        if _verbose: log("%s._wndproc called with %s,%s,%s,%s"%(self.__class__.__name__,hex(hwnd),hex(msg),hex(wParam),hex(lParam)))
        try:
            window = self.widget_map[hwnd]
        except:
            if _verbose: log("\tNO WINDOW TO DISPATCH???")
            return user32.DefWindowProc(hwnd, msg, wParam, lParam)
        try:
            _dispatch = self._dispatch.get(msg,_dispatch_DEFAULT)
            x = _dispatch(window,hwnd,msg,wParam,lParam)
        except:
            if _verbose: logTraceback(None,'_wndproc.1')
            x = -1
        if _verbose: log("\tdispatch %s to %s %s\n" % (_dispatch.__name__[9:],window.__class__.__name__,window),"\t ==>",x)
        return x


    def internalRun(self):
        if _verbose: log('internalRun:Begin',str(self))
        class MSG(Structure):
            _fields_ = (
                ('hwnd','i'),
                ('message','i'),
                ('wParam','i'),
                ('lParam','i'),
                ('time','i'),
                ('x','i'),
                ('y','i'),
                )

        msg = MSG()
        while user32.GetMessage(byref(msg), 0, 0, 0):
            try:
                if _verbose: log('internalRun: loopstart',msg)
                user32.TranslateMessage(byref(msg))
                user32.DispatchMessage(byref(msg))
                if _verbose: log('internalRun: loopend')
            except:
                logTraceback(None)
        if _verbose: log('internalRun: finish')

    def internalRemove(self):
        if not self._windows:
            if _verbose: log('PostQuitMessage(0)')
            user32.PostQuitMessage(0)
            global _app
            _app = None

if  1 and _verbose:
    n = 0
    from inspect import isclass, ismethod, getmembers
    def makeTBWrap(C,methodname):
        import new
        global n
        oldmethodname = '_%d_tbWrap_%s' % (n,methodname)
        oldmethod = getattr(C,methodname)
        S = []
        s = S.append
        s('def %s(self,*A,**K):' % methodname)
        s('\ttry:')
        s('\t\treturn self.%s(*A,**K)' % oldmethodname)
        s('\texcept:')
        s('\t\tfrom anygui.Utils import logTraceback')
        s('\t\tlogTraceback(None,\'[%s.%s]\')' % (C.__name__,methodname))
        s('\t\traise')
        s('setattr(C,oldmethodname,oldmethod)')
        s('setattr(C,methodname,new.instancemethod(%s,None,C))' % methodname)
        exec '\n'.join(S) + '\n' in locals()
        n += 1

    for a in __all__:
        C = globals()[a]
        if isclass(C):
            M = []
            m = M.append
            for methodname,method in getmembers(C):
                if ismethod(method): m(methodname)
            for methodname in M: makeTBWrap(C,methodname)

################################################################
if __name__ == '__main__':
    from anygui import *
    app = Application()
    win = Window(title = "A Standard Window",
                 width = 300, height = 200)
    win.show()
    application().run()
