from anygui.backends import *

__all__ = '''

  Application
  ButtonWrapper
  WindowWrapper

'''.split()

################################################################

import Tkinter
from anygui.Applications import AbstractApplication
from anygui.Wrappers import AbstractWrapper
from anygui.Events import *
from anygui import application

wrappers = []

class Application(AbstractApplication):

    def __init__(self):
        AbstractApplication.__init__(self)
        self._root = Tkinter.Tk()
        self._root.withdraw()

    def _window_deleted(self):
        if not self._windows:
            self._root.destroy()
    
    def _mainloop(self):
        #@ Move this to AbstractApplication?
        for wrapper in wrappers:
            wrapper.prod()
        self._root.mainloop()

class DummyWidget:
    """
    A dummy object used when a wrapper currently has no native widget
    instantiated.
    """
    def isDummy(self): return 1
    
    def dummyMethod(self, *args, **kwds): pass

    def __getattr__(self, name): return self.dummyMethod

    def __setattr__(self, name): pass

    def __str__(self): return '<DummyWidget>'

class Wrapper(AbstractWrapper):

    widget = DummyWidget()
    
    def __init__(self, *args, **kwds):
        AbstractWrapper.__init__(self, *args, **kwds)
        if not self in wrappers: wrappers.append(self) # Hm...
        self.addConstraint('geometry', 'visible')
        # FIXME: Is this the right place to put it? Make sure
        # 'geometry' implies 'x', 'y', etc. too (see Wrappers.py)
        # Also, this scheme will cause flashing... (place before
        # place_forget)

    def enterMainLoop(self): # ...
        try: assert self.widget.isDummy()
        except (AttributeError, AssertionError): pass
        else:
            self.widget.destroy()
            self.internalProd()
        self.proxy.sync()
        
    def destroy(self):
        if self in wrappers: wrappers.remove(self) # ...
        self.widget.destroy() #@ ?

# TODO: Encapsulate dummy-testing a bit...

# Hm... It seems that layout stuff (e.g. hstretch and vmove) is set
# directly as state variables/attributes... Why is that? (There is a
# layout_data attribute too... Hm.)

# Create an idempotent setupEvents method (perhaps in AbstractWrapper, even?)
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

    def clickHandler(self):
        send(self.proxy, 'click')

    # Hm. This method is perhaps a bit hackish? :-)
    # Clean up the parent/dummy code?
    # (Hm. Creation is put here, but descruction directly in remove...?)
    def setContainer(self, container):
        parent = container.wrapper.widget
        try: assert parent.isDummy()
        except (AttributeError, AssertionError):
            self.widget = self.widgetFactory(parent)
            self.widget.configure(command=self.clickHandler) # Move elsewhere...
            self.proxy.sync(blocked=['container'])

class ButtonWrapper(ComponentWrapper):

    def widgetFactory(self, *args, **kwds):
        return Tkinter.Button(*args, **kwds)

    def setText(self, text):
        self.widget.configure(text=text)

class WindowWrapper(ComponentWrapper):

    # Creation/event setup should be placed more consistently...
    def internalProd(self):
        try: self.proxy.container # Should check for None, but not properly implemented yet...
        except AttributeError: return
        if application().isRunning():
            try:
                assert self.widget.isDummy()
            except (AttributeError, AssertionError): pass
            else:
                self.widget = self.widgetFactory()
                self.widget.protocol('WM_DELETE_WINDOW', self.closeHandler)
                self.proxy.sync()

    def closeHandler(self):
        self.destroy()
        application().remove(self.proxy)
        application()._window_deleted() # @@@ Should be invoced by remove...

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
        self.prod()

    def setVisible(self, visible):
        if visible: self.widget.deiconify()
        else: self.widget.withdraw()

    def widgetFactory(self, *args, **kwds):
        return Tkinter.Toplevel(*args, **kwds)

"""

class Button(ComponentMixin, AbstractButton):
    _tk_class = Button

    def _ensure_events(self):
        if self._tk_comp:
            self._tk_comp.config(command=self._tk_clicked)

    def _tk_clicked(self):
        send(self, 'click')

    def _ensure_text(self):
        if self._tk_comp:
            self._tk_comp.configure(text=self._text)
"""

"""

class Window(ComponentMixin, AbstractWindow):
    _tk_class = Toplevel
    _tk_style = 0

    def _ensure_created(self):
        result = ComponentMixin._ensure_created(self)
        #if result:
        #    self._tk_comp.SetAutoLayout(1)
        return result

    def _ensure_visibility(self):
        if self._tk_comp:
            if self._visible:
                self._tk_comp.deiconify()
            else:
                self._tk_comp.withdraw()

    def _ensure_geometry(self):
        geometry = "%dx%d+%d+%d" % (self._width, self._height,self._x, self._y)
        if self._tk_comp:
            self._tk_comp.geometry(geometry)
    
    def _ensure_events(self):
        self._tk_comp.bind('<Configure>', self._tk_size_handler)
        self._tk_comp.protocol('WM_DELETE_WINDOW', self._tk_close_handler)

    def _ensure_title(self):
        if self._tk_comp:
            self._tk_comp.title(self._title)

    def _tk_close_handler(self):
        self._tk_comp.destroy()
        self.destroy()
        #_app._window_deleted()
        application()._window_deleted() #?

    def _tk_size_handler(self, dummy):
        g = self._tk_comp.geometry()
        m = re.match('^(\d+)x(\d+)', g)
        w = int(m.group(1))
        h = int(m.group(2))
        dw = w - self._width
        dh = h - self._height
        self._width = w
        self._height = h
        self.resized(dw, dh)

    def _get_tk_text(self):
        return self._title
"""

"""
class ComponentMixin:
    # mixin class, implementing the backend methods

    _tk_comp = None
    _tk_id = None
    _tk_style = 0
    _tk_opts = {}
    
    def _is_created(self):
        return self._tk_comp is not None

    def _ensure_created(self):
        if self._is_created(): return 0

        if self._container is None: parent = None
        else: parent = self._container._tk_comp

        component = self._tk_class(parent, **self._tk_opts)

        # FIXME: Should be handled by _ensure_title and _ensure_text
        if self._tk_class is Toplevel: #?
            component.title(self._get_tk_text())
        else:
            try:
                component.config(text=self._get_tk_text())
            except: # not all widgets have a 'text' property
                pass
            if self._tk_class is Tkinter.Label:
                component.config(justify=self._tk_style, anchor=W)

        try:
            component.configure(exportselection=EXPORTSELECTION)
        except:
            pass            

        self._tk_comp = component

        return 1

    def _ensure_events(self):
        pass

    def _show(self):
        self._tk_comp.place(x=self._x, y=self._y,
                            width=self._width, height=self._height)

    def _hide(self):
        self._tk_comp.place_forget()

    def _ensure_geometry(self):
        if self._tk_comp and self._visible: self._show()

    def _ensure_visibility(self):
        if self._tk_comp:
            if self._visible: self._show()
            else: self._hide()

    def _ensure_enabled_state(self):
        if self._tk_comp:
            if self._enabled: newstate = NORMAL
            else: newstate = DISABLED
            try: self._tk_comp.config(state=newstate)
            except TclError: pass # Widget doesn't support -state

    def _ensure_destroyed(self):
        if self._tk_comp:
            self._tk_comp.destroy()
            self._tk_comp = None

    def _get_tk_text(self):
        # helper function for creation: return text needed for creation
        # (normally _text, maybe _title or other depending on the class)
        return self._text

    def _ensure_text(self):
        pass
"""
