'''
Experimental backend using the new 0.2 backend API.

Magnus Lie Hetland, 2002-02-09, 2002-02-11

'''

__version__ = '$Revision$'[11:-2]


from anygui.backends import *
__all__ = '''

  Application
  ButtonWrapper
  WindowWrapper

'''.split()

################################################################

import pyui
from anygui.Applications import AbstractApplication
from anygui.Events import *
from anygui import application

wrappers = []

class Application(AbstractApplication):

    running = 0
    
    def run(self):
        
        self.running = 1
        not_done = 1

        pyui.init(800, 600, fullscreen=1)

        for wrapper in wrappers:
            wrapper.prod()
        
        while not_done:
            pyui.draw()
            not_done = pyui.update()

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

class ReallyAbsoluteLayoutManager(pyui.layouts.LayoutManager):
    '''
    A layout manager which is more absolute than the pyui.layouts.AbsoluteLayoutManager.
    '''
    def setPanel(self, panel):
        self.panel = panel

    def begin(self):
        pass

    def end(self):
        pass

    def placeChild(self, child, option):
        child.moveto(option[0], option[1])

    def canResize(self):
        return 1

class Wrapper:

    widget = DummyWidget()
    
    def __init__(self, proxy):
        if not self in wrappers: wrappers.append(self)
        #self.makeSetterMap()
        self.proxy = proxy
        if application().running:
            self.prod()

    def prod(self):
        try: assert self.widget.isDummy()
        except: pass
        else:
            self.widget.destroy()
            self._prod()
        self.proxy.refresh()

    def destroy(self):
        if self in wrappers: wrappers.remove(self)
        self.widget.destroy()

    def stateUpdate(self, state):
        # Should be more "intelligent":
        for key, val in state.iteritems():
            setter = getattr(self, 'set'+key[1:].capitalize(), None)
            if setter: setter(val)

class ComponentWrapper(Wrapper):

    _x, _y, _width, _height = 0, 0, 0, 0
    _enabled = 1 # HACK

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
        # What is PyUI equivalent?
        # HACK:
        self._enabled = enabled

    def setContainer(self, container):
        wrapper = getattr(container, '_dependant', None)
        widget = getattr(wrapper, 'widget', None)
        if widget is not None:
            try: assert self.widget.isDummy()
            except:
                widget.addChild(self.widget, (self._x, self._y)) # ... How about moving it later?


class ButtonWrapper(ComponentWrapper):

    def _handler(self, evt):
        if self._enabled: # HACK
            send(self.proxy, 'click')

    def _prod(self):
        self.widget = pyui.widgets.Button('Button', self._handler)

    def setText(self, text):
        self.widget.setText(text)


class WindowWrapper(ComponentWrapper):

    def _prod(self):
        layout = ReallyAbsoluteLayoutManager()
        self.widget = pyui.widgets.Frame(10, 10, 100, 100, 'Untitled')
        self.widget.setLayout(layout)

    def setTitle(self, title):
        self.widget.setTitle(title)

    def setContainer(self, container):
        pass # Perhaps allow adding to application object...

if __name__ == '__main__': test()
