from anygui.backends import *
import sys

__all__ = '''

  Application
  ButtonWrapper
  CheckBoxWrapper
  LabelWrapper
  ListBoxWrapper
  RadioButtonWrapper
  TextAreaWrapper
  TextFieldWrapper
  WindowWrapper

'''.split()

################################################################

#@@@ FIXME: Implement getGeometry and friends...

#@@@ FIXME: Use isDummy instead of repeated try/except :)
from anygui.Applications import AbstractApplication
from anygui.Wrappers import AbstractWrapper, DummyWidget, isDummy
from anygui.Events import *
from anygui import application
from javax import swing
from java import awt
import java
#from synchronize import apply_synchronized


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
        #FIXME: For LabelWrappers, the following is false, but for ListBoxWrappers, it
        #is true, something which makes ListBoxWrappers sort of ... not work. :P
        #[mlh20020813]
        #assert isDummy(self.proxy.state['container'].wrapper.widget)
        self.proxy.push() 

    def create(self, *args, **kwds):
        
        #FIXME: This does no harm in Jython, since the GUI will run
        #before app.run() anyway. However, this does mean that javagui
        #will behave differently from other back-ends, i.e. the
        #widgets will appear earlier than expected. Also, the reason
        #why this overriding was needed was that
        #AbstractWrapper.create wasn't called after the main loop was
        #entered. That should be fixed, and this method should then
        #probably be removed. [mlh@20020831]

        if self.noWidget():
            self.widget = self.widgetFactory(*args, **kwds)
            self.widgetSetUp()

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
        if self.widget.layout:
            self.widget.validate()

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
            self.proxy.push(blocked=['container'])
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
                if container:
                    bounds = self.widget.bounds
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

################################################################

class ToggleButtonMixin:
                
    def setOn(self, on):
        self.widget.selected = on

    def getOn(self):
        return self.widget.selected

    def widgetSetUp(self): # Should perhaps be in a ButtonMixin superclass?
        self.widget.actionPerformed = self.clickHandler

    def clickHandler(self, event): # Should perhaps be in a ButtonMixin superclass?
        send(self.proxy, 'click')

class CheckBoxWrapper(ToggleButtonMixin, ComponentWrapper):

    def widgetFactory(self, *args, **kwds):
        return swing.JCheckBox()

class RadioButtonWrapper(ToggleButtonMixin, ComponentWrapper):

    def widgetFactory(self, *args, **kwds):
        return swing.JRadioButton()

    #FIXME: This is (semi-)eager behaviour, contrary to the current
    #lazy pull mechanism... [mlh@20020831]
    def clickHandler(self, event):
        val = self.widget.selected
        #FIXME: This doesn't seem right:
        if val == self.proxy.state['on']:
            return
        if self.proxy.group is not None:
            self.group.modify(value=self.value)
        send(self.proxy, 'click')

################################################################

class ButtonWrapper(ComponentWrapper):

    def clickHandler(self, event):
        send(self.proxy, 'click')

    def widgetSetUp(self):
        insets = awt.Insets(0, 0, 0, 0)
        self.widget.margin = insets
        self.widget.actionPerformed = self.clickHandler

    def widgetFactory(self, *args, **kwds):
        return swing.JButton()

################################################################

class LabelWrapper(ComponentWrapper):

    def widgetFactory(self, *args, **kwds):
        widget = swing.JLabel()
        widget.horizontalAlignment = swing.SwingConstants.LEFT # @@@ Should be settable from Proxy
        widget.verticalAlignment = swing.SwingConstants.TOP    # @@@ Should be settable from Proxy
        return widget

################################################################

class TextFieldWrapper(ComponentWrapper):

    def widgetFactory(self, *args, **kwds):
        return swing.JTextField()

    def widgetSetUp(self):
        self.widget.actionPerformed = self.enterHandler

    def enterHandler(self, event):
        send(self, 'enterkey')

    def getSelection(self):
        return self.widget.selectionStart, \
               self.widget.selectionEnd

    def setSelection(self, selection):
        self.widget.selectionStart = selection[0]
        self.widget.selectionStart = selection[1]

    def setEditable(self, editable):
        self.widget.editable = editable

    def setText(self, text):
        self.widget.text = text

    def getText(self):
        return self.widget.text

################################################################

class JScrollableTextArea(swing.JPanel):
    # Replacement for swing.JTextArea

    def __init__(self):
        self._jtextarea = swing.JTextArea()
        self.layout = awt.BorderLayout()
        self._jscrollpane = swing.JScrollPane(self._jtextarea)
        self.add(self._jscrollpane, awt.BorderLayout.CENTER)

    def getText(self):
        return self._jtextarea.text

    def setText(self, text):
        self._jtextarea.text = text

    def getSelectionStart(self):
        return self._jtextarea.selectionStart

    def getSelectionEnd(self):
        return self._jtextarea.selectionEnd

    def setSelectionStart(self, index):
        self._jtextarea.selectionStart = index

    def setSelectionEnd(self, index):
        self._jtextarea.selectionEnd = index

    def setEditable(self, editable):
        self._jtextarea.editable = editable

# FIXME: 'Copy-Paste' inheritance...
class TextAreaWrapper(ComponentWrapper):

    def widgetFactory(self, *args, **kwds):
        return JScrollableTextArea()

    def getSelection(self):
        return self.widget.getSelectionStart(), \
               self.widget.getSelectionEnd()

    def setSelection(self, selection):
        self.widget.setSelectionStart(selection[0])
        self.widget.setSelectionStart(selection[1])

    def setEditable(self, editable):
        self.widget.setEditable(editable)

    def setText(self, text):
        self.widget.setText(text)

    def getText(self):
        return self.widget.getText()


################################################################

class JScrollableListBox(swing.JPanel):
    # Replacement for swing.JList

    def __init__(self):
        self._jlist = swing.JList()
        self.layout = awt.BorderLayout()
        self._jscrollpane = swing.JScrollPane(self._jlist)
        self.add(self._jscrollpane, awt.BorderLayout.CENTER)

    def getModel(self):
        return self._jlist.model

    def setSelectionMode(self, mode):
        self._jlist.selectionMode = mode

    def getSelectedIndex(self):
        return self._jlist.selectedIndex

    def setSelectedIndex(self, index):
        self._jlist.selectedIndex = index

    def setListData(self, items):
        self._jlist.setListData(items)

    def setMouseReleased(self, callback):
        self._jlist.mouseReleased = callback


class ListBoxWrapper(ComponentWrapper):

    def widgetFactory(self, *args, **kwds):
        widget = JScrollableListBox()
        widget.setSelectionMode(swing.ListSelectionModel.SINGLE_SELECTION)
        return widget

    def setSelection(self, selection):
        self.widget.setSelectedIndex(selection)
        
    def getSelection(self):
        # FIXME: This should be handled differently
        if isDummy(self.widget): return 0
        return self.widget.getSelectedIndex()

    def setItems(self, items):
        temp = java.util.Vector()
        for item in items:
            temp.addElement(str(item))
        self.widget.setListData(items)

    def widgetSetUp(self):
        # Won't work because it (1) reacts to programmatic
        # changes, and (2) reacts to both mouse-down and
        # mouse-up events:
        # self._java_comp.valueChanged = self._java_clicked

        # mlh20011217: Wouldn't it be OK to generate events
        # on programmatic changes?
            
        # This works, however:
        self.widget.setMouseReleased(self.clickHandler)

    def clickHandler(self, event):
        send(self.proxy, 'select')
        send(self.proxy, 'click')

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

    def getGeometry(self):
        bounds = self.widget.bounds
        x, y, width, height = bounds.x ,bounds.y, bounds.width, bounds.height
        insets = self.widget.insets
        width -= insets.left + insets.right
        height -= insets.top + insets.bottom
        return x, y, width, height

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

        #ensure proxy state is updated
        self.proxy.height
        self.proxy.width

        self.proxy.resized(dw,dh)

    def closeHandler(self, evt):
        self.destroy()
        application().remove(self.proxy) # @@@ Hm...
