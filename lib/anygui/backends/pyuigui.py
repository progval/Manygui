'''
Experimental backend using the new 0.2 backend API.

Magnus Lie Hetland, 2002-02-09
'''

import pyui

# TODO: Ensure conversion of values if necessary

# FIXME: The refresh mechanism doesn't seem quite correct yet... (Anyway, the
#        button never appears ;)

# Move this to application object?
wrappers = []

class Application:
    
    def run(self):
        done = 1
        pyui.init(800, 600)
        for wrapper in wrappers:
            wrapper.awake()
        
        while done:
            pyui.draw()
            done = pyui.update()

        pyui.quit()


class DummyWidget:
    """
    A dummy object used when a wrapper currently has no native widget
    instantiated.
    """
    def dummyMethod(self, *args, **kwds): pass

    def __getattr__(self, name): return self.dummyMethod

    def __setattr__(self, name): pass

    def __str__(self): return '<DummyWidget>'


class Wrapper:

    widget = DummyWidget()
    
    def __init__(self, proxy):
        if not self in wrappers: wrappers.append(self)
        self.proxy = proxy

    def awake(self):
        self.widget.destroy()
        self._awake()
        self.proxy.refresh()

    def destroy(self):
        if self in wrappers: wrappers.remove(self)
        self.widget.destroy()


class ComponentWrapper(Wrapper):

    _x, _y, _width, _height = 0, 0, 0, 0

    def setX(self, x):
        self._x = x
        self.widget.moveto(x, self._y)

    def setY(self, y):
        self._y = y
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
            self.widget.setParent(widget)


class ButtonWrapper(ComponentWrapper):

    def _handler(self):
        # Add call to send()
        pass

    def _awake(self):
        self.widget = pyui.widgets.Button('Button', self._handler)        

    def setText(self, text):
        self.widget.setText(text)


class WindowWrapper(ComponentWrapper):

    # FIXME: Must pack() be called somewhere?

    def _awake(self):
        self.widget = pyui.widgets.Frame(10, 10, 100, 100, 'Untitled')

    def setTitle(self, title):
        self.widget.setTitle(title)

    def setParent(self, parent):
        pass # ?


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
            for attribute in self.attributes:
                setter = getattr(self.wrapper, 'set' + attribute.capitalize())
                value = getattr(self, attribute)
                setter(value)


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
