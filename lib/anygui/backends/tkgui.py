from anygui.backends import *

__all__ = '''

  Application
  ButtonWrapper
  WindowWrapper
  LabelWrapper
  TextFieldWrapper

'''.split()

################################################################

import Tkinter, re
from anygui.Applications import AbstractApplication
from anygui.Wrappers import AbstractWrapper, DummyWidget, isDummy
from anygui.Events import *
from anygui import application

class Application(AbstractApplication):

    def __init__(self):
        AbstractApplication.__init__(self)
        self._root = Tkinter.Tk()
        self._root.withdraw()
    
    def internalRun(self):
        self._root.mainloop()

    def internalRemove(self):
        if not self._windows:
            self._root.destroy()

class Wrapper(AbstractWrapper):
    
    def __init__(self, *args, **kwds):
        AbstractWrapper.__init__(self, *args, **kwds)
        self.addConstraint('geometry', 'visible')
        # FIXME: Is this the right place to put it? Make sure
        # 'geometry' implies 'x', 'y', etc. too (see Wrappers.py)
        # Also, this scheme will cause flashing... (place before
        # place_forget)

    def enterMainLoop(self): # ...
        if not isDummy(self.widget):
            self.widget.destroy()
        self.proxy.sync() # FIXME: Why is this needed when sync is called in internalProd (by prod)?
        
    def internalDestroy(self):
        self.widget.destroy()

# FIXME: It seems that layout stuff (e.g. hstretch and vmove) is set
# directly as state variables/attributes... Why is that? (There is a
# layout_data attribute too... Hm.)
class ComponentWrapper(Wrapper):

    def setX(self, x):
        self.widget.place(x=x)

    def setY(self, y):
        self.widget.place(y=y)

    def setWidth(self, width):
        self.widget.place(width=width)

    def setHeight(self, height):
        self.widget.place(height=height)

    def setPosition(self, x, y):
        self.widget.place(x=x, y=y)

    def setSize(self, width, height):
        self.widget.place(width=width, height=height)

    def setGeometry(self, x, y, width, height):
        self.widget.place(x=x, y=y, width=width, height=height)

    def setVisible(self, visible):
        if not visible: self.widget.place_forget()
        # Other case handled by geometric setters

    def setContainer(self, container):
        if container is None:
            try:
                self.destroy()
            except:
                pass
            return
        parent = container.wrapper.widget
        try: assert parent.isDummy()
        except (AttributeError, AssertionError):
            self.destroy()
            self.create(parent)
            self.proxy.sync(blocked=['container'])

    def setEnabled(self, enabled):
        if enabled: newstate = Tkinter.NORMAL
        else: newstate = Tkinter.DISABLED
        try: self.widget.config(state=newstate)
        except Tkinter.TclError:
            # Widget doesn't support -state
            pass

class ButtonWrapper(ComponentWrapper):

    def clickHandler(self): 
        send(self.proxy, 'click')

    def setUp(self):
        self.widget.configure(command=self.clickHandler)

    def widgetFactory(self, *args, **kwds):
        return Tkinter.Button(*args, **kwds)

    def setText(self, text):
        self.widget.configure(text=text)

class LabelWrapper(ComponentWrapper):

    def widgetFactory(self,*args,**kws):
        return Tkinter.Label(*args,**kws)

    def setText(self, text):
        self.widget.configure(text=text)

class TkTextMixin:
    """ Mixin that abstracts out all behavior needed to get
    selectable-but-not-editable behavior out of Tk text widgets.
    We bind all keystrokes, passing them through to the underlying
    control when _editable is true, and ignoring all but select
    and copy keystrokes when _editable is false. The mixed-in
    class must provide an updateModel() method, called as a
    Tk event handler when focus leaves the control; and a
    setEditable() method, called from update(), that manages
    the self.editable property. """

    def install_bindings(self,widget):
        self.ctl = 0
        self.alt = 0
        self.shift = 0
        self.editable = 1
        widget.bind("<Key>", self.keybinding)
        widget.bind("<KeyRelease>",self.updateProxy)
        widget.bind("<KeyPress-Control_L>", self.ctldown)
        widget.bind("<KeyRelease-Control_L>", self.ctlup)
        widget.bind("<KeyPress-Alt_L>", self.altdown)
        widget.bind("<KeyRelease-Alt_L>", self.altup)
        widget.bind("<KeyPress-Shift_L>", self.shiftdown)
        widget.bind("<KeyRelease-Shift_L>", self.shiftup)
        widget.bind("<Key-Insert>", self.insertbinding)
        widget.bind("<Key-Up>", self.arrowbinding)
        widget.bind("<Key-Down>", self.arrowbinding)
        widget.bind("<Key-Left>", self.arrowbinding)
        widget.bind("<Key-Right>", self.arrowbinding)
        widget.bind("<ButtonRelease>", self.insertbinding)

        # Easy place to put this - not _editable-related, but common
        # to all text widgets.
        widget.bind("<Leave>", self.updateProxy)

    # Track modifier key state.
    def ctldown(self, ev):
        self.ctl = 1
    def ctlup(self, ev):
        self.ctl = 0
    def altdown(self, ev):
        self.alt = 1
    def altup(self, ev):
        self.alt = 0
    def shiftdown(self, ev):
        self.shift = 1
    def shiftup(self, ev):
        self.shift = 0

    def keybinding(self, ev):
        """ This method binds all keys, and causes them to be
        ignored when _editable is not set. """
        if self.editable:
            self.updateProxy()
            return None
        else:
            # This is truly horrid. Please add appropriate
            # code for Mac platform, someone.
            if (ev.char == "\x03") or (ev.char == "c" and self.alt):
                # DON'T ignore this key: it's a copy operation.
                return None
            return "break"

    def insertbinding(self,ev):
        # Overrides _keybinding for the Insert key.
        if self.editable:
            return None
        if self.ctl:
            # Allow copy.
            return None
        return "break"

    def arrowbinding(self,ev):
        # This method's sole reason for existence is to allow arrows
        # to work even when self.editable is false.
        return None

class TextFieldWrapper(ComponentWrapper,TkTextMixin):

    def widgetFactory(self,*args,**kws):
        theWidge=Tkinter.Entry(*args,**kws)
        self.install_bindings(theWidge)
        return theWidge

    def updateProxy(self,*args,**kws):
        # Inform proxy of text change by the user.
        self.proxy.rawModify(text=self.widget.get())
        if self.widget.select_present():
            start = self.widget.index('sel.first')
            end = self.widget.index('sel.last')
        else:
            start = end = self.widget.index('insert')
        self.proxy.rawModify(selection=(start,end))

    def setText(self,text):
        disabled=0
        if self.widget.cget('state') != Tkinter.NORMAL:
            self.widget.configure(state=Tkinter.NORMAL)
            disabled=1
        self.widget.delete(0,Tkinter.END)
        self.widget.insert(0,text)
        if disabled:
            self.widget.configure(state=Tkinter.DISABLED)

    def setEditable(self,editable):
        self.editable=editable

    def setSelection(self,selection):
        self.widget.selection_range(*selection)

class FrameWrapper(ComponentWrapper):

    def widgetFactory(self,*args,**kws):
        kws['relief'] = 'sunken'
        kws['borderwidth'] = 2
        theWidge=Tkinter.Frame(*args,**kws)
        return theWidge

    def setContainer(self,*args,**kws):
        """
        Ensure all contents are properly created. This looks like it could
        be handled at the Proxy level, but it probably *shouldn't* be -
        it's handling a Tk-specific requirement about the order in which
        widgets must be created. (I did it the Proxy way too. This way
        is definitely "the simplest thing that could possibly work.") - jak
        """
        ComponentWrapper.setContainer(self,*args,**kws)
        for component in self.proxy.contents:
            component.container = self.proxy

class WindowWrapper(ComponentWrapper):

    def __init__(self,proxy):
        ComponentWrapper.__init__(self,proxy)

    def internalProd(self):
        # Should check for None, but not properly implemented yet...
        try: self.proxy.container
        except AttributeError: return
        self.create()
        self.proxy.sync()

    def closeHandler(self):
        self.destroy()
        application().remove(self.proxy)

    def resizeHandler(self, event):
        # FIXME: Shouldn't this simply set geometry, and have
        # setGeometry that call resized() or something? - mlh
        # No, we've already got new geometry, no need to
        # set it. - jak
        x,y,w,h = self.getGeometry()
        dw = w - self.proxy.width
        dh = h - self.proxy.height

        # Weird: why doesn't self.proxy.geometry give us the same values???
        oldGeo = self.proxy.x,self.proxy.y,self.proxy.width,self.proxy.height
        if (x,y,w,h) == oldGeo:
            # Do nothing unless we've actually changed size or position.
            # (Configure events happen for all kinds of wacky reasons,
            # most of which are already dealt with by Proxy code.) - jak
            return
        
        self.proxy.rawModify(width=w)
        self.proxy.rawModify(height=h)
        self.proxy.rawModify(x=x)
        self.proxy.rawModify(y=y)
        self.proxy.resized(dw, dh) # @@@ Implement this...

    def setUp(self):
        self.widget.protocol('WM_DELETE_WINDOW', self.closeHandler)
        self.widget.bind('<Configure>', self.resizeHandler)

    #def getGeometry(self):
    #    geo = self.widget.geometry()
    #    if not geo:
    #        return 100,100,10,10
    #    geo = geo.split('+')
    #    geo[0:1] = geo[0].split('x')
    #    w,h,x,y = map(int,geo)
    #    return x,y,w,h

    def getGeometry(self):
        g = self.widget.geometry()
        m = re.match('^(\d+)x(\d+)\+(\d+)\+(\d+)', g) # Hm...
        w = int(m.group(1))
        h = int(m.group(2))
        x = int(m.group(3))
        y = int(m.group(4))
        return x,y,w,h
    
    def setX(self, x):
        ox,y,w,h = self.getGeometry()
        self.setGeometry(x,y,w,h)

    def setY(self, y):
        x,oy,w,h = self.getGeometry()
        self.setGeometry(x,y,w,h)

    def setWidth(self, width):
        x,y,ow,h = self.getGeometry()
        self.setGeometry(x,y,width,h)

    def setHeight(self, height):
        x,y,w,oh = self.getGeometry()
        self.setGeometry(x,y,w,height)

    def setPosition(self, x, y):
        ox,oy,w,h = self.getGeometry()
        geometry = "%dx%d+%d+%d" % (w,h,x, y)
        self.widget.geometry(geometry)

    def setSize(self, width, height):
        x,y,ow,oh = self.getGeometry()
        geometry = "%dx%d+%d+%d" % (width, height,x,y)
        self.widget.geometry(geometry)        
    
    def setGeometry(self, x, y, width, height):
        geometry = "%dx%d+%d+%d" % (width, height, x, y)
        self.widget.geometry(geometry)
        self.widget.update()
    
    def setTitle(self, title):
        self.widget.title(title)

    def setContainer(self, container):
        pass

    def setVisible(self, visible):
        if visible: self.widget.deiconify()
        else: self.widget.withdraw()

    def widgetFactory(self, *args, **kwds):
        return Tkinter.Toplevel(*args, **kwds)
