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

class TextFieldWrapper(ComponentWrapper):

    def widgetFactory(self,*args,**kws):
        theWidge=Tkinter.Entry(*args,**kws)
        theWidge.bind("<Return>",self.handle_return)
        return theWidge

    def handle_return(self,*args,**kws):
        # Inform proxy of text change by the user.
        self.proxy.rawModify(text=self.widget.get())

    def setText(self,text):
        disabled=0
        if self.widget.cget('state') != Tkinter.NORMAL:
            self.widget.configure(state=Tkinter.NORMAL)
        self.widget.delete(0,Tkinter.END)
        self.widget.insert(0,text)
        if disabled:
            self.widget.configure(state=Tkinter.DISABLED)

class WindowWrapper(ComponentWrapper):

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
        # setGeometry that call resized() or something?
        g = self.widget.geometry()
        m = re.match('^(\d+)x(\d+)', g) # Hm...
        w = int(m.group(1))
        h = int(m.group(2))
        dw = w - self.proxy.width
        dh = h - self.proxy.height
        self.proxy.rawModify(width=w)
        self.proxy.rawModify(height=h)
        #self.proxy.resized(dw, dh) # @@@ Implement this...

    def setUp(self):
        self.widget.protocol('WM_DELETE_WINDOW', self.closeHandler)
        self.widget.bind('<Configure>', self.resizeHandler)

    # This works, but separate x, y, width, and height setters are
    # still needed...

    def setPosition(self, x, y):
        geometry = "%d+%d" % (x, y)
        self.widget.geometry(geometry)

    def setSize(self, width, height):
        geometry = "%dx%d" % (width, height)
        self.widget.geometry(geometry)        
    
    def setGeometry(self, x, y, width, height):
        geometry = "%dx%d+%d+%d" % (width, height, x, y)
        self.widget.geometry(geometry)
    
    def setTitle(self, title):
        self.widget.title(title)

    def setContainer(self, container):
        pass

    def setVisible(self, visible):
        if visible: self.widget.deiconify()
        else: self.widget.withdraw()

    def widgetFactory(self, *args, **kwds):
        return Tkinter.Toplevel(*args, **kwds)
