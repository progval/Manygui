'''
Experimental backend using the new 0.2 backend API.

Magnus Lie Hetland, 2002-02-09

'''

__version__ = '$Revision$'[11:-2]

import pyui

wrappers = []

class Application:
    
    def run(self):
        done = 1

        pyui.init(800, 600, fullscreen=1)
        
        for wrapper in wrappers:
            wrapper.prod()
        
        while done:
            pyui.draw()
            done = pyui.update()

        pyui.quit()


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


class Wrapper:

    widget = DummyWidget()
    
    def __init__(self, proxy):
        if not self in wrappers: wrappers.append(self)
        self.proxy = proxy

    def prod(self):
        self.widget.destroy()
        self._prod()
        self.proxy.refresh()

    def destroy(self):
        if self in wrappers: wrappers.remove(self)
        self.widget.destroy()

    def set(self, **kwds):
        # Should be more "intelligent":
        for key, val in kwds.iteritems():
            setter = getattr(self, 'set'+key.capitalize(), None)
            if setter: setter(val)

class ComponentWrapper(Wrapper):

    _x, _y, _width, _height = 0, 0, 0, 0

    def setX(self, x):
        self._x = x
        # FIXME: Won't survive pack()
        self.widget.moveto(x, self._y)

    def setY(self, y):
        self._y = y
        # FIXME: Won't survive pack()
        self.widget.moveto(self._x, y)

    def setWidth(self, width):
        self._width = width
        self.widget.resize(width, self._height)

    def setHeight(self, height):
        self._height = height
        self.widget.resize(self._width, height)

    def setVisible(self, visible):
        self.widget.setShow(visible)

    def setEnabled(self, enabled):
        pass # What is PyUI equivalent?

    def setParent(self, parent):
        widget = getattr(parent, 'widget', None)
        if widget is not None:
            try: assert self.widget.isDummy()
            except:
                widget.addChild(self.widget, (self._x, self._y)) # ...


class ButtonWrapper(ComponentWrapper):

    def _handler(self, evt):
        # TODO: Add call to send()
        pass

    def _prod(self):
        self.widget = pyui.widgets.Button('Button', self._handler)        

    def setText(self, text):
        self.widget.setText(text)


class WindowWrapper(ComponentWrapper):

    def _prod(self):
        # This is really a "relative layout manager"...
        # How does one get absolute positioning?
        layout = pyui.layouts.AbsoluteLayoutManager()
        self.widget = pyui.widgets.Frame(10, 10, 100, 100, 'Untitled')
        self.widget.setLayout(layout)

    def setTitle(self, title):
        self.widget.setTitle(title)

    def setParent(self, parent):
        pass # Perhaps allow adding to application object...


def test():

    class Component:
        
        attributes = '''
        x
        y
        width
        height
        visible
        enabled
        parent
        '''.split()

        # Defaults
        visible = 1
        enabled = 1
        parent = None
        
        def __init__(self):
            self._create_wrapper()
            
        def refresh(self):
            kwds = {}
            for attribute in self.attributes:
                value = getattr(self, attribute)
                kwds[attribute] = value
            self.wrapper.set(**kwds)
            

    class Window(Component):

        attributes = Component.attributes + ['title']
        
        def __init__(self):
            Component.__init__(self)
            self.contents = []
            
        def refresh(self):
            Component.refresh(self)
            for child in self.contents:
                child.refresh()
        
        def add(self, child):
            if not child in self.contents:
                self.contents.append(child)
                child.parent = self.wrapper
                child.refresh()

        def _create_wrapper(self):
            self.wrapper = WindowWrapper(self)


    class Button(Component):

        attributes = Component.attributes + ['text']
        
        def _create_wrapper(self):
            self.wrapper = ButtonWrapper(self)

    
    win = Window()
    win.x = 50
    win.y = 50
    win.width = 300
    win.height = 200
    win.title = 'Testing'
    win.refresh() # Not needed with Attrib mixin

    btn = Button()
    btn.x = 10
    btn.y = 10
    btn.width = 100
    btn.height = 50
    btn.text = 'Click me'
    btn.refresh()

    win.add(btn)

    app = Application()
    app.run()


if __name__ == '__main__': test()
