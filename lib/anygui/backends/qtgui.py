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
  MenuWrapper
  MenuCommandWrapper
  MenuCheckWrapper
  MenuSeparatorWrapper
  MenuBarWrapper

'''.split()


#==============================================================#
from weakref import ref as wr
from qt import *
from anygui.Applications import AbstractApplication
from anygui.Wrappers import AbstractWrapper, DummyWidget, isDummy
from anygui.Events import *
from anygui.Windows import Window
from anygui import application
from anygui.Menus import Menu, MenuCommand, MenuCheck, MenuSeparator

TRUE = 1
FALSE = 0

DEBUG = 0
TMP_DBG = 1

#==============================================================#

class Application(AbstractApplication, QApplication):

    def __init__(self):
        AbstractApplication.__init__(self)
        QApplication.__init__(self,[])
        self.connect(qApp, SIGNAL('lastWindowClosed()'), qApp, SLOT('quit()'))

    def internalRun(self):
        qApp.exec_loop()

    def internalRemove(self):
        if not self._windows:
            qApp.quit()

#==============================================================#

class Wrapper(AbstractWrapper):

    def __init__(self, *args, **kwds):
        AbstractWrapper.__init__(self, *args, **kwds)

        # 'container' before everything...
        self.setConstraints('container','x','y','width','height','text','selection')
        # Note: x,y,width, and height probably have no effect here, due to
        # the way getSetters() works. I'm not sure if that's something
        # that needs fixing or not... - jak

        self.addConstraint('geometry', 'visible')
        # FIXME: Is this the right place to put it? Make sure
        # 'geometry' implies 'x', 'y', etc. too (see Wrappers.py)
        # Also, this scheme will cause flashing... (place before
        # place_forget)

    def enterMainLoop(self): # ...
        #if not isDummy(self.widget):
        #    self.widget.destroy()
        #    sys.stdout.flush()
        self.proxy.push() # FIXME: Why is this needed when push is called in internalProd (by prod)?

    def internalDestroy(self):
        self.widget.destroy()

#==============================================================#

# FIXME: It seems that layout stuff (e.g. hstretch and vmove) is set
# directly as state variables/attributes... Why is that? (There is a
# layout_data attribute too... Hm.)
class ComponentWrapper(Wrapper):

    visible=1

    def setX(self, x):
        self.widget.setGeometry(x,self.y,self.width,self.heigth)

    def setY(self, y):
        self.widget.setGeometry(self.x,y,self.width,self.heigth)

    def setWidth(self, width):
        self.widget.setGeometry(self.x,self.y,width,self.heigth)

    def setHeight(self, height):
        self.widget.setGeometry(self.x,self.y,self.width,heigth)

    def setPosition(self, x, y):
        self.widget.setGeometry(x,y,self.width,self.heigth)

    def setSize(self, width, height):
        self.widget.setGeometry(self.x,self.y,width,heigth)

    def setGeometry(self, x, y, width, height):
        self.widget.setGeometry(x,y,width,heigth)

    def setVisible(self, visible):
        if visible:
            self.widget.show()
        else:
            self.widget.hide()

    def setContainer(self, container):
        if container is None:
            try:
                self.destroy()
            except:
                pass
            return
        parent = container.wrapper.widget
        try:
            assert parent.isDummy()
        except (AttributeError, AssertionError):
            self.destroy()
            self.create(parent)
            self.proxy.push(blocked=['container'])

    def setEnabled(self, enabled):
           self.widget.setEnabled(enabled)


    def setText(self, text):
        try:
            self.widget.setText(QString(text))

    def getText(self):
        try:
            return str(self.widget.text())
        except:
            # Widget has no text.
            return ""


#==============================================================#

class EventFilter(QObject):
    _comp = None
    _events = {}

    def __init__(self, parent, events):
        QObject.__init__(self, parent.widget)
        self._comp = wr(parent)
        self._events = events

    def eventFilter(self, object, event):
        #if DEBUG: print 'in eventFilter of: ', self._window_obj().widget
        type = event.type()
        if not type in self._events.keys():
            return 0
        return self._events[type](self._comp(), event)

#==============================================================#

class LabelWrapper(ComponentWrapper):

    def widgetFactory(self, *args, **kws):
        widget = QLabel(*args, **kws)
        self.widget.self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        return widget

#==============================================================#

class ListBox(ComponentWrapper):
    connected = 0

    def __init__(self, *args, **kws):
        ComponentWrapper.__init__(self, *args, **kws)
        self.items = []

    def widgetFactory(self, *args, **kws):
        widget= QListbox(*args, **kws)
        if not self.connected:
            qApp.connect(self.widget, SIGNAL('highlighted(int)'),
                         self.clickHandler)
            self.connected = 1
        return widget

    def setItems(self, items):
        self.widget.clear()
        self.items = items[:]
        for item in self.items:
            self.widget.insertItem(QString(str(item)),-1)

    def getItems(self):
        return self.items

    def setSelection(self, selection):
        self.widget.setCurrentItem(int(selection))

    def getSelection(self):
        selection = int(self.widget.currentItem())
        return selection

    def clickHandler(self, index):
        # self.selection = int(index)
        send(self.proxy, 'select')

#==============================================================#

class ButtonWrapperBase(ComponentWrapper):
    connected = 0

    def widgetSetUp(self):
        if not self._connected:
            qApp.connect(self.widget,SIGNAL('clicked()'),self.clickHandler)
            self.connected = 1

#--------------------------------------------------------------#

class ButtonWrapper(ButtonWrapperBase):

    def widgetFactory(self, *args, **kwds):
        return QPushButton(*args, **kwds)

    def clickHandler(self):
        send(self,'click')

#--------------------------------------------------------------#

class ToggleButtonWrapperBase(ButtonWrapperBase):

    def setOn(self, on):
        self.widget.setChecked(on)

    def getOn(self):
        return self.widget.isChecked()

    def clickHandler(self, *args, **kws): # Should perhaps be in a ButtonMixin superclass?
        send(self.proxy, 'click')

#--------------------------------------------------------------#

class CheckBox(ToggleButtonWrapperBase):

    def widgetFactory(self, *args, **kwds):
        return QCheckBox(*args, **kwds)

#--------------------------------------------------------------#

class RadioButtonWrapper(ToggleButtonWrapperBase):
    groupMap = {}

    def __init__(self, *args, **kws):
        ComponentWrapper.__init__(self, *args, **kws)
        ToggleButtonMixin.__init__(self)

    def widgetFactory(self, *args, **kwds):
        return QCheckBox(*args, **kwds)

    def setGroup(self, group):
        if not group._items:
            group._items.append(self.proxy)
            btnGroup = QButtonGroup(self.text, self.container.widget)
            RadioButtonWrapper.groupMap[group] = btnGroup
            btnGroup.insert(this.widget)
        elif self.proxy not in group._items:
            group._items.append(self.proxy)
            btnGroup = RadioButtonWrapper.groupMap[group]
            btnGroup.insert(this.widget)

    def setValue(self, value):
        self.widget.setChecked(int(value))

    def getValue(self):
        return int(self.widget.isChecked())

#==============================================================#

class TextWrapperBase(ComponentWrapper):
    connected = 0

    def widgetSetUp(self):
        if not self._connected:
            events = {QEvent.KeyRelease: self.keyPressHandler.im_func,
                      QEvent.FocusIn:    self.gotFocusHandler.im_func,
                      QEvent.FocusOut:   self.lostFocusHandler.im_func}
            self.eventFilter = EventFilter(self, events)
            self.widget.installEventFilter(self.eventFilter)
            self.connected = 1

    def setEditable(self, editable):
        self.widget.setReadOnly(not editable)

    def qtText(self):
        return QString(self.text)

    def keyPressHandler(self, event):
        if DEBUG: print 'in keyPressHandler of: ', self.widget
        self.text = self.text()
        #self.modify(text=self._backend_text())
        if int(event.key()) == 0x1004: #Qt Return Key Code
            send(self, 'enterkey')
        return 1


    def gotFocusHandler(self, event):
        if DEBUG: print 'in gotFocusHandler of: ', self.widget
        return 1
        #   send(self, 'gotfocus')

    def lostFocusHandler(self, event):
        if DEBUG: print 'in lostFocusHandler of: ', self.widget
        return 1
        #   send(self, 'lostfocus')

    def qtCalcStartEnd(self, text, mtxt, pos):
        start, idx = 0, -1
        for n in range(text.count(mtxt)):
            idx = text.find(mtxt, idx+1)
            if idx == pos or idx == pos - len(mtxt):
                start = idx
                break
        end = start + len(mtxt)
        if DEBUG: print 'returning => start: %s | end: %s' %(start,end)
        return start,  end

#--------------------------------------------------------------#

class TextFieldWrapper(TextWrapperBase):

    def widgetFactory(self, *args, **kwds):
        return QLineEdit(*args, **kwds)

    def setSelection(self, selection):
        if DEBUG: print 'in _ensure_selection of: ', self.widget
        start, end = selection
        self.widget.setSelection(start, end-start)
        self.widget.setCursorPosition(end)

    def getSelection(self):
        if DEBUG: print 'in _backend_selection of: ', self.widget
        pos = self.widget.cursorPosition()
        if self.widget.hasMarkedText():
            text = self.text()
            mtxt = str(self.widget.markedText())
            return self.qtCalcStartEnd(text,mtxt,pos)
        else:
            return pos, pos

#--------------------------------------------------------------#

class TextAreaWrapper(TextWrapperBase):

    def widgetFactory(self, *args, **kwds):
        return QMultiLineEdit(*args, **kwds)

    def setSelection(self, selection):
        #QMultiLineEdit.setSelection is yet to be implemented...
        #Hacked it so that it will work until the proper method can be used.
        if DEBUG: print 'in _ensure_selection of: ', self.widget
        start, end = selection
        srow, scol = self.qtTranslateRowCol(start)
        erow, ecol = self.qtTranslateRowCol(end)
        #Enter hack...
        self.widget.setCursorPosition(srow, scol, FALSE)
        self.widget.setCursorPosition(erow, ecol, TRUE)
        #Exit hack...
        #self.widget.setSelection(srow, scol, erow, ecol)
        #self.widget.setCursorPosition(erow,ecol)

    def getSelection(self):
        if DEBUG: print 'in _backend_selection of: ', self.widget
        row, col = self.widget.getCursorPosition()
        if DEBUG: print 'cursor -> row: %s| col: %s' %(row,col)
        pos = self.qtTranslatePosition(row, col)
        if DEBUG: print 'pos of cursor is: ', pos
        if self.widget.hasMarkedText():
            text = self.text()
            mtxt = str(self.widget.markedText())
            return self.qtCalcStartEnd(text,mtxt,pos)
        else:
            return pos, pos

    def qtGetLines(self):
        lines = []
        for n in range(0,self.widget.numLines()):
            lines.append(str(self.widget.textLine(n)) + '\n')
        if DEBUG: print 'lines are: \n', lines
        return lines

    def qtTranslateRowCol(self, pos):
        if DEBUG: print 'translating pos to row/col...'
        row, col, currRow, totLen = 0, 0, 0, 0
        for ln in self.qtGetLines():
            if pos <= len(str(ln)) + tot_len:
                row = currRow
                col = pos - totLen
                if DEBUG: print 'returning => row: %s| col: %s' %(row,col)
                return row, col
            else:
                currRow += 1
                totLen += len(str(ln))
        if DEBUG: print 'returning => row: %s| col: %s' %(row,col)
        return row, col

    def qtTranslatePosition(self, row, col):
        if DEBUG: print 'translating row/col to pos...'
        lines = self.qtGetLines()
        pos = 0
        for n in range(len(lines)):
            if row != n:
                pos += len(lines[n])
            else:
                pos += col
                break
        if DEBUG: print 'returning pos => ', pos
        return pos

#==============================================================#

class FrameWrapper(ComponentWrapper):

    def widgetFactory(self, *args, **kws):
        widget = QFrame(*args, **kws)
        widget.setFrameStyle(QFrame.Plain)
        return widget

#==============================================================#

class QWindow(QWidget): pass #Alias for clarity

class Window(ComponentMixin, AbstractWindow):
    connected = 0
    destroyingSelf = 0

    def setTitle(self, title):
        if self.widget:
            self.widget.setCaption(QString(title))

    def widgetSetUp(self):
        if not self.connected:
            events = {QEvent.Resize: self.resizeHandler.im_func,
                      QEvent.Move:   self.moveHandler.im_func,
                      QEvent.Close:  self.closeHandler.im_func}
            self.eventFilter = EventFilter(self, events)
            self.widget.installEventFilter(self.eventFilter)
            self.connected = 1


    def getTitle(self):
        return str(self.widget.title())

    def resizeHandler(self, event):
        if DEBUG: print 'in _qt_resize_handler of: ', self.widget

        x, y, w, h = self.getGeometry()
        dw = w - self.proxy.state['width'] # @@@ With lazy semantics, these will be fetched from the widget!
        dh = h - self.proxy.state['height'] # @@@ (and therefore will tell us nothing!)

        self.proxy.height
        self.proxy.width

        self.proxy.resized(dw, dh)
        return 1

    def moveHandler(self, event):
        if DEBUG: print 'in _qt_move_handler of: ', self.widget
        nx = self.widget.x()
        ny = self.widget.y()
        dx = nx - self.proxy.state['x']
        dy = ny - self.proxy.state['y']

        self.proxy.x
        self.proxy.y

        #self.proxy.moved(dx, dy)
        return 1

    def closeHandler(self, event):
        if DEBUG: print 'in _qt_close_handler of: ', self.widget
        # What follows is a dirty hack, but PyQt will seg-fault the
        # interpreter if a call onto QWidget.destroy() is made after
        # the Widget has been closed. It is also necessary to inform
        # the front-end of self being closed.
        self.destroyingSelf = 1
        self.destroy()
        self.destroyingSelf = 0
        self.connected = 0
        self.widget = None
        application().remove(self.proxy)
        return 0


#==============================================================#
