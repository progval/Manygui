from anygui.backends import *
import sys

__all__ = '''

  Application
  ButtonWrapper
  WindowWrapper
  LabelWrapper
  TextFieldWrapper
  TextAreaWrapper
  ListBoxWrapper
  RadioButtonWrapper
  CheckBoxWrapper

'''.split()

################################################################

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
        parent = container.wrapper.widget
        try:
            assert parent.isDummy()
        except (AttributeError, AssertionError):
            self.destroy()
            self.create()
            try:
                container = container.contentPane
            except AttributeError: pass
            container.add(self.widget)
            self._container = container # Can this be fetched from the widget (later)?
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
            if hasattr(self.widget, 'dispose'):
            try: comp.dispose()
            except AttributeError: pass
            self._container = None

    def setText(self, text):
        self.widget.text = text

    def getText(self):
        try:
            assert self.widget.isDummy()
        except (AttributeError, AssertionError):
            return self.widget.text
        else:
            return "" # @@@ What would be the best behaviour here? Should there be an exception?

# @@@ -------------------- Continue here --------------------
          
################################################################

class Label(ComponentMixin, AbstractLabel):
    _java_class = swing.JLabel
    _java_style = None

    def _ensure_created(self):
        result = ComponentMixin._ensure_created(self)
        if result:
            self._java_comp.horizontalAlignment = swing.SwingConstants.LEFT
            self._java_comp.verticalAlignment = swing.SwingConstants.TOP
        return result

    def _ensure_text(self):
        if self._java_comp:
            text =  self._get_java_text()
            self._java_comp.text = text

################################################################

class ScrollableListBox(swing.JPanel):
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

class ListBox(ComponentMixin, AbstractListBox):
    _java_class = ScrollableListBox # Jython wrapper

    def _ensure_created(self):
        result = ComponentMixin._ensure_created(self)
        if result:
            self._java_comp.setSelectionMode(swing.ListSelectionModel.SINGLE_SELECTION)
        return result

    def _backend_selection(self):
        if self._java_comp:
            return self._java_comp.getSelectedIndex()

    def _ensure_items(self):
        if self._java_comp:
            items = java.util.Vector()
            for item in self._items:
                items.addElement(str(item))
            self._java_comp.setListData(items)

    def _ensure_selection(self):
        if self._java_comp:
            self._java_comp.setSelectedIndex(self._selection)

    def _ensure_events(self):
        if self._java_comp:
            # Won't work because it (1) reacts to programmatic
            # changes, and (2) reacts to both mouse-down and
            # mouse-up events:
            # self._java_comp.valueChanged = self._java_clicked

            # mlh20011217: Wouldn't it be OK to generate events
            # on programmatic changes?
            
            # This works, however:
            self._java_comp.setMouseReleased(self._java_clicked)

    def _java_clicked(self, event):
        #self.do_action()
        send(self, 'select')

################################################################

class Button(ComponentMixin, AbstractButton):
    _java_class = swing.JButton

    def _ensure_created(self):
        result = ComponentMixin._ensure_created(self)

        # More room for the button text, so it won't be hidden when the
        # button is a bit small.
        insets = awt.Insets(0, 0, 0, 0)
        self._java_comp.margin = insets
        
        return result

    def _ensure_events(self):
        self._java_comp.actionPerformed = self._java_clicked

    def _java_clicked(self, evt):
        send(self, 'click')

class ToggleButtonMixin(ComponentMixin):

    def _ensure_state(self):
        if self._java_comp is not None:
            self._java_comp.selected = self.on

    def _ensure_events(self):
        self._java_comp.actionPerformed = self._java_clicked

    def _java_clicked(self, evt):
        val = self._java_comp.selected
        if val == self.on: # FIXME: this way or == self._on?
            return
        self.modify(on=val)
        send(self, 'click')

class CheckBox(ToggleButtonMixin, AbstractCheckBox):
    _java_class = swing.JCheckBox

class RadioButton(ToggleButtonMixin, AbstractRadioButton):
    _java_class = swing.JRadioButton

    def _java_clicked(self, evt):
        val = self._java_comp.selected
        if val == self.on: # FIXME: this way or == self._on?
            return
        if self.group is not None:
           self.group.modify(value=self.value)
        else: # FIXME: is this branch needed?
          self.modify(on=val)
        send(self, 'click')

################################################################

class TextField(ComponentMixin, AbstractTextField):
    _java_class = swing.JTextField

    def _backend_text(self):
        if self._java_comp:
            return self._java_comp.text

    def _backend_selection(self):
        if self._java_comp:
            return self._java_comp.selectionStart, \
                   self._java_comp.selectionEnd

    def _ensure_selection(self):
        if self._java_comp:
            self._java_comp.selectionStart = self._selection[0]
            self._java_comp.selectionEnd = self._selection[1]

    def _ensure_editable(self):
        if self._java_comp:
            self._java_comp.editable = self._editable

    def _ensure_events(self):
        if self._java_comp:
            self._java_comp.actionPerformed = self._java_enterkey
            self._java_comp.focusLost = self._java_focus_lost

    def _java_enterkey(self, event):
        send(self, 'enterkey')

    def _java_focus_lost(self, event):
        self.modify(text=self._java_comp.text)
        
class ScrollableTextArea(swing.JPanel):
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
class TextArea(ComponentMixin, AbstractTextArea):
    _java_class = ScrollableTextArea

    def _backend_text(self):
        if self._java_comp and hasattr(self._java_comp, '_jtextarea'):
            return self._java_comp.getText()

    def _backend_selection(self):
        if self._java_comp and hasattr(self._java_comp, '_jtextarea'):
            return self._java_comp.getSelectionStart(), \
                   self._java_comp.getSelectionEnd()

    def _ensure_text(self):
        if self._java_comp and hasattr(self._java_comp, '_jtextarea'):
            self._java_comp.setText(self._get_java_text())

    def _ensure_selection(self):
        if self._java_comp and hasattr(self._java_comp, '_jtextarea'):
            self._java_comp.setSelectionStart(self._selection[0])
            self._java_comp.setSelectionEnd(self._selection[1])

    def _ensure_editable(self):
        if self._java_comp and hasattr(self._java_comp, '_jtextarea'):
            self._java_comp.setEditable(self._editable)

    def _ensure_events(self):
        if self._java_comp and hasattr(self._java_comp, '_jtextarea'):
            self._java_comp._jtextarea.focusLost = self._java_focus_lost

    def _java_focus_lost(self, event):
        self.modify(text=self._java_comp.getText())

################################################################

class Frame(ComponentMixin, AbstractFrame):
    _java_class = swing.JPanel

    def _ensure_created(self):
       result = ComponentMixin._ensure_created(self)
       if result:
           self._java_comp.layout=None
       return result
 
################################################################

class Window(ComponentMixin, AbstractWindow):
    _java_class = swing.JFrame
    _java_style = None #wxDEFAULT_FRAME_STYLE

    def _ensure_created(self):
        result = ComponentMixin._ensure_created(self)
        if result:
            self._java_comp.addNotify() # make correct insets vals avail
            self._java_comp.contentPane.layout=None
        return result

    def _ensure_geometry(self):
        if self._java_comp:
            comp = self._java_comp
            insets = comp.insets
            comp.bounds = (self._x,
                           self._y,
                           self._width + insets.left + insets.right,
                           self._height + insets.top + insets.bottom)

    
    def _ensure_events(self):
        self._java_comp.windowClosing = self._java_close_handler
        self._java_comp.componentResized = self._java_resize_handler

    def _ensure_title(self):
        if self._java_comp:
            self._java_comp.title = self._title

    def _java_resize_handler(self,evt):
        w = self._java_comp.width
        h = self._java_comp.height
        insets = self._java_comp.insets
        w -= insets.left + insets.right
        h -= insets.top + insets.bottom
        dw = w - self._width
        dh = h - self._height
        self.modify(width=w)
        self.modify(height=h)
        self.resized(dw, dh)

    def _java_close_handler(self, evt):
        self.destroy()

    def _get_java_text(self):
        return self._title
