
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
    _java_container = None
    _java_id = None
    _java_style = 0

    def _is_created(self):
        return self._java_comp is not None

    def _ensure_created(self):
        if self._java_comp is None:
            if self._container is not None:
                parent = self._container._java_comp
            else:
                parent = None
            frame = self._java_class()
            if parent:
                frame.visible = 0
                if parent.__class__ == swing.JFrame:
                    self._java_container = parent.contentPane
                else:
                    self._java_container = parent
                self._java_container.add(frame)
            self._java_comp = frame
            return 1
        return 0

    def _ensure_events(self):
        pass

    def _ensure_geometry(self):
        if self._java_comp:
            self._java_comp.bounds = (self._x,
                                      self._y,
                                      self._width,
                                      self._height)
	    if self._java_comp.layout:
                self._java_comp.validate()

    def _ensure_visibility(self):
        if self._java_comp:
            self._java_comp.visible = self._visible

    def _ensure_enabled_state(self):
        if self._java_comp:
            self._java_comp.enabled = self._enabled

    def _ensure_destroyed(self):
        if self._java_comp:
            comp = self._java_comp
            container = self._java_container
            if container:
                bounds = comp.bounds
                container.remove(comp)
                container.repaint(bounds)
            if hasattr(comp, 'dispose'):
                comp.dispose()
            self._java_container = None
            self._java_comp = None

    def _get_java_text(self):
        # helper function for creation
        # returns the text required for creation.
        # This may be the _text property, or _title, ...,
        # depending on the subclass
        return str(self._text)

    def _ensure_text(self):
        if self._java_comp and hasattr(self._java_comp, 'text'):
            self._java_comp.text = self._get_java_text()

################################################################

class JavaCanvasWrapper(awt.Canvas):

    def __init__(self):
        awt.Canvas.__init__(self)
        self.background = awt.Color.white

    def paint(self, g2):
        img = self.canvas._offscreen
        h = img.height
        w = img.width
        g2.drawImage(img, 0, 0, w, h, self)        

class Canvas(ComponentMixin, AbstractCanvas):

    # TODO: Implement native versions of other drawing methods,
    #       e.g. Béziers etc.
    
    # FIXME: Needs to be invalidated when resized,
    #        while retaining the graphics...
    
    _java_class = JavaCanvasWrapper
    _img_type = awt.image.BufferedImage.TYPE_INT_RGB
    _path_type = awt.geom.GeneralPath.WIND_EVEN_ODD

    def __init__(self, *args, **kwds):
        AbstractCanvas.__init__(self, *args, **kwds)
        self.clear()

    def _ensure_created(self):
        result = ComponentMixin._ensure_created(self)
        self._java_comp.canvas = self
        return result

    def _ensure_events(self):
        if self._java_comp:
            self._java_comp.mouseReleased = self._java_clicked

    def _java_clicked(self, event):
        send(self, 'click', x=event.x, y=event.y)

    def clear(self):
        img = awt.image.BufferedImage(self._width,
                                      self._height,
                                      self._img_type)
        g2 = img.createGraphics()
        w, h = img.width, img.height
        rect = awt.geom.Rectangle2D.Double(0, 0, w, h)
        p = g2.getPaint()
        g2.setPaint(awt.Color.white)
        g2.fill(rect)
        g2.setPaint(p)
        self._offscreen = img

    def flush(self): # FIXME: Do something useful :)
        pass

    def drawPolygon(self, pointlist,
                    edgeColor=None, edgeWidth=None, fillColor=None, closed=0):
        if edgeColor is None:
            edgeColor = self.defaultLineColor
        if edgeWidth is None:
            edgeWidth = self.defaultLineWidth
        if fillColor is None:
            fillColor = self.defaultFillColor

        g2 = self._offscreen.createGraphics()
        
        g2.setStroke(awt.BasicStroke(edgeWidth))
        
        polygon = awt.geom.GeneralPath(self._path_type, int(len(pointlist)/2))
        polygon.moveTo(*pointlist[0])
        for pt in pointlist[1:]:
            polygon.lineTo(*pt)
        if closed:
            polygon.closePath()

        if fillColor is not Colors.transparent:
            c = _convert_color(fillColor)
            g2.setPaint(c)
            g2.fill(polygon)

        if edgeColor is not Colors.transparent:
            c = _convert_color(edgeColor)
            g2.setPaint(c)
            g2.draw(polygon)

def _convert_color(c):
    # Hack to appease Jython polymorphism
    c = int(c.red*255) << 16 | int(c.green*255) << 8 | int(c.blue*255)
    return awt.Color(c)
          
################################################################

class Label(ComponentMixin, AbstractLabel):
    #_width = 100 # auto ?
    #_height = 32 # auto ?
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
            #text = cgi.escape(text)
            #text = text.replace('\n', '<br>')
            #text = text.replace('\r', '<br>')
            #text = '<html>' + text + '</html>'
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
