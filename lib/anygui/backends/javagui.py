from anygui.backends import *
import sys

__all__ = '''

  Application
  WindowWrapper
  LabelWrapper

'''.split()

#__all__ = '''
#
#  Application
#  ButtonWrapper
#  WindowWrapper
#  LabelWrapper
#  TextFieldWrapper
#  TextAreaWrapper
#  ListBoxWrapper
#  RadioButtonWrapper
#  CheckBoxWrapper
#
#'''.split()

################################################################

#@@@ FIXME: Implement getGeometry and friends...

#@@@ FIXME: Use isDummy instead of repeated try/except :)
from anygui.Applications import AbstractApplication
from anygui.Wrappers import AbstractWrapper, DummyWidget, isDummy
from anygui.Events import *
from anygui import application
from javax import swing
from java import awt
import cgi, jarray, java

# Set the "look-and-feel":
swing.UIManager.setLookAndFeel(swing.UIManager.getSystemLookAndFeelClassName())

################################################################

class Application(AbstractApplication):
    
    def internalRun(self):
        # Ignores the possibility of delayed window-creating events:
        from time import sleep
        while self._windows:
            sleep(0.5)

          
################################################################

class Wrapper(AbstractWrapper):

    def __init__(self, *args, **kwds):
        AbstractWrapper.__init__(self, *args, **kwds)
        # @@@ Cookie-cutter from tkgui
        self.setConstraints('container','x','y','width','height','text','selection')

    # @@@ Cookie-cutter from tkgui
    def enterMainLoop(self):
        self.proxy.push() 

    # internalDestroy?

################################################################

class ComponentWrapper(Wrapper):

    def setX(self, x):
        self.widget.x = x

    def setY(self, y):
        self.widget.y = y

    def setWidth(self, width):
        self.widget.width = width

    def setHeight(self, height):
        self.widget.height = height

    def setPosition(self, x, y):
        self.widget.position = x, y

    def setSize(self, width, height):
        self.widget.size = width, height

    def setGeometry(self, x, y, width, height):
        self.widget.bounds = x, y, width, height
        self.widget.validate() # Needed? Needed in others?

    def setVisible(self, visible):
        self.widget.visible = visible

    def setContainer(self, container):
        # Factor out the conditional destruction?
        if container is None:
            self.destroy()
            return
        try:
            parent = container.wrapper.widget
        except AttributeError:
            # FIXME: Handle Application containers differently...
            self.create()
            return
        try:
            assert parent.isDummy()
        except (AttributeError, AssertionError):
            self.destroy()
            self.create()
            try:
                parent = parent.contentPane
            except AttributeError: pass
            parent.add(self.widget)
            self._container = parent # Can this be fetched from the widget (later)?
            self.proxy.push(blocked=['container'])

    def setEnabled(self, enabled):
        self.widget.enabled = enabled

    def internalDestroy(self): # Move to Wrapper?
        try:
            assert self.widget.isDummy()
        except (AttributeError, AssertionError):
            try:
                container = self._container
            except AttributeError: pass
            else:
                bounds = comp.bounds
                container.remove(self.widget)
                container.repaint(bounds)
            try: self.widget.dispose()
            except AttributeError: pass
            self._container = None

    def setText(self, text):
        try:
            self.widget.setText(text)
        except AttributeError: pass # FIXME! When does this happen?
        #self.widget.text = text # FIXME!

    def getText(self):
        try:
            assert self.widget.isDummy()
        except (AttributeError, AssertionError):
            return self.widget.text
        else:
            return "" # @@@ What would be the best behaviour here? Should there be an exception?

# @@@ -------------------- Continue here --------------------
          
################################################################

class LabelWrapper(ComponentWrapper):

    def widgetFactory(self, *args, **kwds):
        widget = swing.JLabel()
        widget.horizontalAlignment = swing.SwingConstants.LEFT # @@@ Should be settable from Proxy
        widget.verticalAlignment = swing.SwingConstants.TOP    # @@@ Should be settable from Proxy
        return widget

################################################################

class WindowWrapper(ComponentWrapper):

    def widgetFactory(self, *args, **kwds):
        widget = swing.JFrame() # Title...
        widget.addNotify() # Make correct insets values available
        widget.contentPane.layout = None
        return widget

    def setGeometry(self, x, y, width, height):
        if not isDummy(self.widget):
            insets = self.widget.insets
            width += insets.left + insets.right
            height += insets.top + insets.bottom
            ComponentWrapper.setGeometry(self, x, y, width, height)

    def widgetSetUp(self):
        self.widget.windowClosing = self.closeHandler
        self.widget.componentResized = self.resizeHandler

    def setTitle(self, title):
        self.widget.title = title

    def getTitle(self):
        return self.widget.title

    def resizeHandler(self, evt):
        w = self.widget.width
        h = self.widget.height
        insets = self.widget.insets
        w -= insets.left + insets.right
        h -= insets.top + insets.bottom
        dw = w - self.proxy.state['width'] # @@@ Avoid invoking pull()...
        dh = h - self.proxy.state['height'] # @@@ Avoid invoking pull()...
        self.proxy.resized(dw, dh)

    def closeHandler(self, evt):
        self.destroy()
        application().remove(self.proxy) # @@@ Hm...
