
from anygui.backends import *
__all__ = anygui.__all__

################################################################

from javax import swing
from java import awt
import cgi, jarray, java

# Set the "look-and-feel":
swing.UIManager.setLookAndFeel(swing.UIManager.getSystemLookAndFeelClassName())

class ComponentMixin:

    _java_comp = None
    _java_id = None
    _java_style = 0 # FIXME: Is this applicable in Java?
    
    def _is_created(self):
        return self._java_comp is not None

    def _ensure_created(self):
        if self._java_comp is None:
            if self._container is not None:
                parent = self._container._java_comp
            else:
                parent = None
            frame = self._java_class(
                #parent,
                #self._java_id,
                #self._get_java_text(),
                #style=self._java_style
                )
            if parent:
                if parent.__class__ == swing.JFrame:
                    parent.contentPane.add(frame)
                else:
                    parent.add(frame)
            if frame.__class__ == swing.JFrame:
                frame.contentPane.layout = JavaGUILayoutManager(self)
            elif hasattr(frame, 'layout'):
                frame.layout = JavaGUILayoutManager(self)
            # Aren't _ensure_text and _ensure_title called?
            if hasattr(frame, 'title'):
                frame.title = self._get_java_text()
            elif hasattr(frame, 'text'):
                # FIXME: This shouldn't be necessary (especially given the call to
                # _ensure_text below), but without it, buttons don't get their
                # text set properly.
                frame.text = self._get_java_text()
            self._java_comp = frame
            if hasattr(self, '_ensure_text'):
                self._ensure_text() # FIXME: Should be called by anygui
            return 1
        return 0

    def _ensure_events(self):
        pass

    def _ensure_geometry(self): # FIXME: Default handling
        if self._java_comp:
            comp = self._java_comp
            if comp.__class__ == swing.JFrame:
                comp.pack() # To make insets available
                insets = comp.insets
                comp.bounds = (self._x,
                               self._y,
                               self._width + insets.left + insets.right,
                               self._height + insets.top + insets.bottom)
            else:
                comp.bounds = (self._x,
                               self._y,
                               self._width,
                               self._height)

    def _ensure_visibility(self):
        if self._java_comp:
            self._java_comp.visible = self._visible

    def _ensure_enabled_state(self):
        if self._java_comp:
            self._java_comp.enabled = self._enabled

    def _ensure_destroyed(self):
        if self._java_comp:
            if hasattr(self._java_comp, 'dispose'):
                self._java_comp.dispose()
            self._java_comp = None

    def _get_java_text(self):
        # helper function for creation
        # returns the text required for creation.
        # This may be the _text property, or _title, ...,
        # depending on the subclass
        return self._text

    def _ensure_text(self):
        pass

class JavaGUILayoutManager(awt.LayoutManager):

    '''A custom layout manager for anygui. For more information
    about implementing custom Java layout managers, see
    "Creating a Custom Layout Manager" [1] from the Java Tutorial.

    [1] http://java.sun.com/docs/books/tutorial/uiswing/layout/custom.html'''

    def __init__(self, python_parent):
        self.components = []
        self.parent = python_parent
        self.first_time = 1

    def addLayoutComponent(self, name, java_component):
        self.components.append(component)

    def removeLayoutComponent(self, java_component):
        if component in self.components:
            self.components.remove(java_component)
        
    def minimumLayoutSize(self, java_parent):
        return awt.Dimension(0,0) # FIXME: Is this OK?

    def preferredLayoutSize(self, java_parent):
        return awt.Dimension(0,0) # FIXME: Is this OK?

    def layoutContainer(self, java_parent):
        'Called when the panel is first displayed and on every resize.'
        if self.first_time: # FIXME: Ugly hack
            self.first_time = 0
        else:
            w = java_parent.width
            h = java_parent.height
            dw = w - self.parent._width
            dh = h - self.parent._height
            self.parent._width = w
            self.parent._height = h
            if hasattr(self.parent, 'resized'): # FIXME: Ugly hack
                self.parent.resized(dw, dh)
            
################################################################

class Label(ComponentMixin, AbstractLabel):
    #_width = 100 # auto ?
    #_height = 32 # auto ?
    _java_class = swing.JLabel
    _text = "JLabel"
    _java_style = None

    def _ensure_text(self):
        # FIXME: HTML may cause unwanted text wrapping
        if self._java_comp:
            text = self._text
            text = cgi.escape(text)
            text = text.replace('\n', '<br>')
            text = text.replace('\r', '<br>')
            text = '<html>' + text + '</html>'
            self._java_comp.text = text
            self.horizontalAlignment = swing.SwingConstants.LEFT # FIXME: Wrong place
            self.verticalAlignment = swing.SwingConstants.TOP # FIXME: Wrong place

################################################################

class ScrollableListBox(swing.JPanel):
    # Replacement for swing.JList

    # FIXME: Constructor doesn't seem to work right, so an explicit
    # method is needed.
    def init(self):
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
            self._java_comp.init()
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
            
            # This works, however:
            self._java_comp.setMouseReleased(self._java_clicked)

    def _java_clicked(self, event):
        #self.do_action()
        send(self, 'click', loop=1)

################################################################

class Button(ComponentMixin, AbstractButton):
    _java_class = swing.JButton
    _text = "JButton"

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
        #self.do_action()
        send(self, 'click', loop=1)

class ToggleButtonMixin(ComponentMixin):

    def _ensure_state(self):
        if self._java_comp is not None:
            self._java_comp.selected = self.on
    
    def _java_clicked(self, evt):
        val = self._java_comp.selected
        if val == self.on:
            return
        self.model.value = val
        #self.do_action()
        send(self, 'click', loop=1)

class CheckBox(ToggleButtonMixin, AbstractCheckBox):
    _java_class = swing.JCheckBox
    _text = "JCheckBox"

    def _ensure_events(self):
        # FIXME: This could be inherited from Button...
        self._java_comp.actionPerformed = self._java_clicked

class RadioButton(ToggleButtonMixin, AbstractRadioButton):
    _java_class = swing.JRadioButton
    _text = "JRadioButton"
    
    def _ensure_created(self):
        # The groups is stored in self._group... But what is that?
        #if self._group and 0 == self._group._items.index(self):
        return ToggleButtonMixin._ensure_created(self)

    def _ensure_events(self):
        # FIXME: Again, straight from Button...
        self._java_comp.actionPerformed = self._java_clicked
        #EVT_RADIOBUTTON(self._java_comp, self._java_id, self._java_clicked)

################################################################

class TextField(ComponentMixin, AbstractTextField):
    _java_class = swing.JTextField

    #def _backend_text(self):
    #    if self._java_comp:
    #        return self._java_comp.text

    def _backend_selection(self):
        if self._java_comp:
            return self._java_comp.selectionStart, \
                   self._java_comp.selectionEnd

    def _ensure_text(self):
        if self._java_comp:
            self._java_comp.text = self._text

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
        #self.do_action()
        send(self, 'enterkey', loop=1)

    def _java_focus_lost(self, event):
        if self.model.value != self._java_comp.text:
            self.model.value = self._java_comp.text # FIXME: Will cause self-update

class ScrollableTextArea(swing.JPanel):
    # Replacement for swing.JTextArea

    # FIXME: Constructor doesn't seem to work right, so an
    # explicit method is needed. (May not be the case...)
    def init(self):
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

    def _ensure_created(self):
        result = ComponentMixin._ensure_created(self)
        if result:
            self._java_comp.init()
        return result
    
    def _backend_text(self):
        # FIXME: Ugly hack!
        if self._java_comp and hasattr(self._java_comp, '_jtextarea'):
            return self._java_comp.getText()

    def _backend_selection(self):
        # FIXME: Ugly hack!
        if self._java_comp and hasattr(self._java_comp, '_jtextarea'):
            return self._java_comp.getSelectionStart(), \
                   self._java_comp.getSelectionEnd()

    def _ensure_text(self):
        # FIXME: Ugly hack!
        if self._java_comp and hasattr(self._java_comp, '_jtextarea'):
            self._java_comp.setText(self._text)

    def _ensure_selection(self):
        # FIXME: Ugly hack!
        if self._java_comp and hasattr(self._java_comp, '_jtextarea'):
            self._java_comp.setSelectionStart(self._selection[0])
            self._java_comp.setSelectionEnd(self._selection[1])

    def _ensure_editable(self):
        # FIXME: Ugly hack!
        if self._java_comp and hasattr(self._java_comp, '_jtextarea'):
            self._java_comp.setEditable(self._editable)

    def _ensure_events(self):
        # FIXME: Ugly hack!
        if self._java_comp and hasattr(self._java_comp, '_jtextarea'):
            self._java_comp._jtextarea.focusLost = self._java_focus_lost

    def _java_focus_lost(self, event):
        self.model.value = self._java_comp.getText() # FIXME: Will cause self-update

################################################################

class Frame(ComponentMixin, AbstractFrame):
    _java_class = swing.JPanel

################################################################

class Window(ComponentMixin, AbstractWindow):
    _java_class = swing.JFrame
    _java_style = None #wxDEFAULT_FRAME_STYLE

    def _ensure_created(self):
        result = ComponentMixin._ensure_created(self)
        return result
    
    def _ensure_events(self):
        self._java_comp.windowClosing = self._java_close_handler

    def _ensure_title(self):
        if self._java_comp:
            self._java_comp.title = self._title

    def _java_close_handler(self, evt):
        self.destroy()

    def _get_java_text(self):
        return self._title

################################################################

class Application(AbstractApplication):
    
    def _mainloop(self):
        from java.lang import Thread
        curthread = Thread.currentThread()

        threads = jarray.zeros(curthread.activeCount(), Thread)
        #@@@ Risky - activeCount may change here...
        curthread.enumerate(threads)

        for thread in threads:
            #@@@ Shaky condition (platform dependent?):
            if thread.name.find('AWT-EventQueue') != -1:
                thread.join() # Wait for AWT thread to finish
                break
        else:
            raise RuntimeError, 'unable to find AWT thread'

################################################################
