#==============================================================#
# Imports

try:
    # Anygui specific imports
    from anygui.backends import *
    from anygui.Applications import AbstractApplication
    from anygui.Wrappers import AbstractWrapper
    from anygui.Events import *
    from anygui.Windows import Window
    from anygui import application
    from anygui.Menus import Menu, MenuCommand, MenuCheck, MenuSeparator

    # qtgui specific imports        
    import sys
    from weakref import ref as wr
    from qt import *
except:
    import traceback
    traceback.print_exc()

#==============================================================#
# Exports

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
# Local Constants

TRUE = 1
FALSE = 0

DEBUG = 1
TMP_DBG = 0

#==============================================================#
# Factoring out creational code...

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

    def enterMainLoop(self):
        self.proxy.push()

    def internalDestroy(self):
        if DEBUG: print "in internalDestroy of: ", self
        self.widget.destroy()

    def rebuild(self): pass

    def rebuildAll(self): pass

#==============================================================#
# Base class for all Widgets

class ComponentWrapper(Wrapper):

    visible=1

    def __init__(self, *args, **kwds):
        Wrapper.__init__(self, *args, **kwds)

    def setX(self, x):
        if self.widget:
            g = self.widget.geometry()
            self.setGeometry(x, g.y(), g.width(), g.height())

    def setY(self, y):
        if self.widget:
            g = self.widget.geometry()
            self.setGeometry(g.x(), y, g.width(), g.height())

    def setWidth(self, width):
        if self.widget:
            g = self.widget.geometry()
            self.setGeometry(g.x(), g.y(), width, g.height())

    def setHeight(self, height):
        if self.widget:
            g = self.widget.geometry()
            self.setGeometry(g.x() ,g.y(), g.width(), height)

    def setPosition(self, x, y):
        if self.widget:
            g = self.widget.geometry()
            self.setGeometry(x, y, g.width(), g.height())

    def setSize(self, width, height):
        if self.widget:
            g = self.widget.geometry()
            self.setGeometry(g.x(), g.y(), width, height)

    def setGeometry(self, x, y, width, height):
        if self.widget:
            self.widget.setGeometry(x,y,width,height)

    def getGeometry(self):
        if self.widget:
            r = self.widget.geometry()
            return (r.x(), r.y(), r.width(), r.height())

    def setVisible(self, visible):
        if self.widget:
            if visible:
                self.widget.show()
            else:
                self.widget.hide()

    def setContainer(self, container):
        if container is None: return
        parent = container.wrapper.widget
        try:
            assert parent is None
        except (AssertionError):
            self.create(parent)
            self.proxy.push(blocked=['container'])
            self.setupChildWidgets()

    def setEnabled(self, enabled):
        if self.widget:
            self.widget.setEnabled(enabled)

    def setText(self, text):
        if self.widget:
            try:
                self.widget.setText(QString(str(text)))
            except:
                pass

    def getText(self):
        if self.widget:
            try:
                return str(self.widget.text())
            except:
                # Widget has no text.
                return ""
            
    def setupChildWidgets(self):
        pass

#==============================================================#

class EventFilter(QObject):
    """
    This class is used as a generic event filter
    for Qt based widgets. This is really only a
    temp fix for some slight problems with PyQt.
    """
    
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
# Label

class LabelWrapper(ComponentWrapper):

    def __init__(self, *args, **kwds):
        ComponentWrapper.__init__(self, *args, **kwds)

    def widgetFactory(self, *args, **kws):
        widget = QLabel(*args, **kws)
        widget.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        return widget

#==============================================================#
# ListBox

class ListBoxWrapper(ComponentWrapper):
    connected = 0

    def __init__(self, *args, **kws):
        ComponentWrapper.__init__(self, *args, **kws)
        self.items = []

    def widgetFactory(self, *args, **kws):
        return QListBox(*args, **kws)

    def widgetSetUp(self):
        if not self.connected:
            qApp.connect(self.widget, SIGNAL('highlighted(int)'),
                         self.selectHandler)
            self.connected = 1

    def setItems(self, items):
        if self.widget:
            self.widget.clear()
            self.items = items[:]
            for item in self.items:
                self.widget.insertItem(QString(str(item)),-1)

    def getItems(self):
        if self.widget:
            return self.items

    def setSelection(self, selection):
        if self.widget:
            self.widget.setCurrentItem(int(selection))

    def getSelection(self):
        if self.widget:
            selection = int(self.widget.currentItem())
            return selection

    def selectHandler(self, index):
        # self.selection = int(index)
        send(self.proxy, 'select')

#==============================================================#
# Base class for Button widgets

class ButtonWrapperBase(ComponentWrapper):
    connected = 0

    def __init__(self, *args, **kws):
        ComponentWrapper.__init__(self, *args, **kws)

    def widgetSetUp(self):
        if not self.connected:
            qApp.connect(self.widget,SIGNAL('clicked()'),self.clickHandler)
            self.connected = 1

    def clickHandler(self):
        send(self.proxy,'click')

#==============================================================#
# Button

class ButtonWrapper(ButtonWrapperBase):

    def __init__(self, *args, **kws):
        ButtonWrapperBase.__init__(self, *args, **kws)

    def widgetFactory(self, *args, **kwds):
        return QPushButton(*args, **kwds)

#==============================================================#
# Base class for Toggle widgets

class ToggleButtonWrapperBase(ButtonWrapperBase):

    def __init__(self, *args, **kws):
        ButtonWrapperBase.__init__(self, *args, **kws)

    def setOn(self, on):
        if self.widget:
            self.widget.setChecked(bool(on))

    def getOn(self):
        if self.widget:
            return bool(self.widget.isChecked())

#==============================================================#
# CheckBox

class CheckBoxWrapper(ToggleButtonWrapperBase):

    def __init__(self, *args, **kws):
        ToggleButtonWrapperBase.__init__(self, *args, **kws)

    def widgetFactory(self, *args, **kwds):
        return QCheckBox(*args, **kwds)

#==============================================================#
# RadioButton

class RadioButtonWrapper(ToggleButtonWrapperBase):
    groupMap = {}

    def __init__(self, *args, **kws):
        ComponentWrapper.__init__(self, *args, **kws)

    def widgetFactory(self, *args, **kwds):
        return QRadioButton(*args, **kwds)

    def setGroup(self, group):
        if group:
            if not group._items:
                if self.proxy.container:
                    group._items.append(self.proxy)
                    container = self.proxy.container
                    btnGroup = QButtonGroup(container.wrapper.widget)
                    RadioButtonWrapper.groupMap[group] = btnGroup
                    btnGroup.insert(self.widget)
            elif self.proxy not in group._items:
                group._items.append(self.proxy)
                btnGroup = RadioButtonWrapper.groupMap[group]
                btnGroup.insert(self.widget)

    def setValue(self, value):
        self.widget.setChecked(bool(value))

    def getValue(self):
        return bool(self.widget.isChecked())

#==============================================================#
# Base class for Text widgets

class TextWrapperBase(ComponentWrapper):
    connected = 0

    def __init__(self, *args, **kws):
        ComponentWrapper.__init__(self, *args, **kws)

    def widgetSetUp(self):
        if not self.connected:
            events = {QEvent.KeyRelease: self.keyReleaseHandler.im_func,
                      QEvent.FocusIn:    self.gotFocusHandler.im_func,
                      QEvent.FocusOut:   self.lostFocusHandler.im_func}
            self.eventFilter = EventFilter(self, events)
            self.widget.installEventFilter(self.eventFilter)
            self.connected = 1

    def setEditable(self, editable):
        if self.widget:
            self.widget.setReadOnly(not editable)

    def qtText(self):
        return QString(str(self.text))

    def keyReleaseHandler(self, event):
        if DEBUG: print 'in keyReleaseHandler of: ', self.widget
        self.proxy.pull('text')
        if int(event.key()) == 0x1004: #Qt Return Key Code
            if DEBUG: print 'enter key was pressed in ', self 
            send(self.proxy, 'enterkey')
        return 1

    def gotFocusHandler(self, event):
        if DEBUG: print 'in gotFocusHandler of: ', self.widget
        return 1
        #   send(self.proxy, 'gotfocus')

    def lostFocusHandler(self, event):
        if DEBUG: print 'in lostFocusHandler of: ', self.widget
        return 1
        #   send(self.proxy, 'lostfocus')

#    def qtCalcStartEnd(self, text, mtxt, pos):
#        start, idx = 0, -1
#        for n in range(text.count(mtxt)):
#            idx = text.find(mtxt, idx+1)
#            if idx <= pos <= idx + len(mtxt):
#                start = idx
#                break
#        end = start + len(mtxt)
#        if DEBUG: print 'returning => start: %s | end: %s' %(start,end)
#        return start,  end

#==============================================================#
# TextField

class TextFieldWrapper(TextWrapperBase):

    def __init__(self, *args, **kws):
        TextWrapperBase.__init__(self, *args, **kws)

    def widgetFactory(self, *args, **kwds):
        return QLineEdit(*args, **kwds)

    def setSelection(self, selection):
        if self.widget:
            if DEBUG: print 'in setSelection of: ', self.widget
            start, end = selection
            self.widget.setSelection(start, end-start)
        
    def getSelection(self):
        if self.widget:
            if DEBUG: print 'in getSelection of: ', self.widget
            pos = self.widget.cursorPosition()
            if self.widget.hasSelectedText():
                return self.widget.getSelection()[1:] #ignore bool
            else:
                return pos, pos

#==============================================================#
# TextArea

class TextAreaWrapper(TextWrapperBase):

    def __init__(self, *args, **kws):
        TextWrapperBase.__init__(self, *args, **kws)

    def widgetFactory(self, *args, **kwds):
        return QTextEdit(*args, **kwds)

    def setSelection(self, selection):
        if DEBUG: print 'in setSelection of: ', self.widget
        if self.widget is not None:
            start, end = selection
            spara, sidx = self.qtTranslateParaIdx(start)
            epara, eidx = self.qtTranslateParaIdx(end)
            self.widget.setSelection(spara, sidx, epara, eidx)

    def getSelection(self):
        if DEBUG: print 'in getSelection of: ', self.widget
        para, idx = self.widget.getCursorPosition()
        if DEBUG: print 'cursor -> para: %s| idx: %s' %(para,idx)
        pos = self.qtTranslatePosition(para, idx)
        if DEBUG: print 'pos of cursor is: ', pos
        if self.widget.hasSelectedText():
            spara, sidx, epara, eidx = self.widget.getSelection()
            spos = self.qtTranslatePosition(spara, sidx)
            epos = self.qtTranslatePosition(epara, eidx)
            return spos, epos
        else:
            return pos, pos

    def qtGetParagraphs(self):
        paras = []
        if self.widget is not None:
            for n in range(self.widget.paragraphs()):
                paras.append(str(self.widget.text(n)))
        if DEBUG:
            print 'paragraphs are: \n'
            for para in paras:
                print para
        return paras

    def qtTranslateParaIdx(self, pos):
        if DEBUG: print 'translating pos to para/idx...'
        para, idx, currPara, totLen = 0, 0, 0, 0
        for prg in self.qtGetParagraphs():
            if pos <= len(prg) + totLen:
                para = currPara
                idx  = pos - totLen
                if DEBUG: print 'returning => para: %s| idx: %s' %(para,idx)
                return para, idx
            else:
                currPara += 1
                totLen   += len(prg)
        if DEBUG: print 'returning => para: %s| idx: %s' %(para,idx)
        return para, idx

    def qtTranslatePosition(self, para, idx):
        if DEBUG: print 'translating para/idx to pos...'
        paras = self.qtGetParagraphs()
        pos = 0
        for n in range(len(paras)):
            if para != n:
                pos += len(paras[n])
            else:
                pos += idx
                break
        if DEBUG: print 'returning pos => ', pos
        return pos

#==============================================================#
# Frame

class FrameWrapper(ComponentWrapper):

    def __init__(self, *args, **kws):
        ComponentWrapper.__init__(self, *args, **kws)

    def widgetFactory(self, *args, **kws):
        widget = QFrame(*args, **kws)
        widget.setFrameStyle(QFrame.Plain)
        return widget

    def setupChildWidgets(self):
        for component in self.proxy.contents:
            component.container = self.proxy


#==============================================================#
# Window

class WindowWrapper(ComponentWrapper):
    connected = 0
    destroyingSelf = 0
    mainWindow = None

    def __init__(self, proxy):
        ComponentWrapper.__init__(self, proxy)

    def setText(self, text):
        if self.widget:
            self.mainWindow.setCaption(QString(str(text)))

    def setTitle(self, title):
        if self.widget:
            self.mainWindow.setCaption(QString(str(title)))

    def widgetSetUp(self):
        if not self.connected:
            events = {QEvent.Resize: self.resizeHandler.im_func,
                      QEvent.Move:   self.moveHandler.im_func}
            self.eventFilter = EventFilter(self, events)
            self.widget.installEventFilter(self.eventFilter)
            self.mainWinEventFilter = EventFilter(self,
                                                  {QEvent.Close:
                                                   self.closeHandler.im_func})
            self.mainWindow.installEventFilter(self.mainWinEventFilter)
            self.connected = 1

    def getTitle(self):
        return str(self.widget.title())

    def resizeHandler(self, event):
        if DEBUG: print 'in resizeHandler of: ', self.widget

        x, y, w, h = self.getGeometry()
        dw = w - self.proxy.state['width'] # @@@ With lazy semantics, these will be fetched from the widget!
        dh = h - self.proxy.state['height'] # @@@ (and therefore will tell us nothing!)

        self.proxy.height
        self.proxy.width

        self.proxy.resized(dw, dh)
        return 1

    def moveHandler(self, event):
        if DEBUG: print 'in moveHandler of: ', self.widget
        nx = self.widget.x()
        ny = self.widget.y()
        dx = nx - self.proxy.state['x']
        dy = ny - self.proxy.state['y']

        self.proxy.x
        self.proxy.y

        #self.proxy.moved(dx, dy)
        return 1

    def closeHandler(self, event):
        if DEBUG: print 'in closeHandler of: ', self.widget
        # What follows is a dirty hack, but PyQt will seg-fault the
        # interpreter if a call onto QWidget.destroy() is made after
        # the Widget has been closed. It is also necessary to inform
        # the front-end of self being closed.
        self.destroyingSelf = 1
        self.destroy()
        self.destroyingSelf = 0
        self.connected = 0
        self.widget = None
        self.mainWindow = None
        application().remove(self.proxy)
        return 1

    def setContainer(self, container):
        if container is None: return
        try:
            assert(self.widget is None)
            self.create()
        except (AttributeError):
            self.create()
        except (AssertionError):
            pass
        self.proxy.push(blocked=['container'])
        self.setupChildWidgets()

    def widgetFactory(self, *args, **kwds):
        self.mainWindow = QMainWindow(*args, **kwds)
        widget = QFrame(self.mainWindow)
        widget.setFrameStyle(QFrame.Plain)
        self.mainWindow.setCentralWidget(widget)
        return widget

    def setVisible(self, visible):
        if self.mainWindow:
            if visible:
                self.mainWindow.show()
            else:
                self.mainWindow.hide()

    def setupChildWidgets(self):
        for component in self.proxy.contents:
            component.container = self.proxy

    def internalDestroy(self):
        if DEBUG: print "in internalDestroy of: ", self
        self.mainWindow.destroy()
        application().remove(self.proxy)

    def setGeometry(self, x, y, width, height):
        if self.widget:
             self.mainWindow.setGeometry(x, y, width, height)

    def getGeometry(self):
        if self.widget:
            r = self.widget.geometry()
            p = self.widget.mapToGlobal(QPoint(r.x(), r.y()))
            return (p.x(), p.y(), r.width(), r.height())
        else:
            return (0, 0, 0, 0)


#==============================================================#
# GroupBox

class GroupBoxWrapper(ComponentWrapper):

    def __init__(self, *args, **kws):
        ComponentWrapper.__init__(self, *args, **kws)

    def widgetFactory(self, *args, **kws):
        widget = QButtonGroup(*args, **kws)
        # widget.setFrameStyle(QFrame.Plain)
        return widget

    def setupChildWidgets(self):
        for component in self.proxy.contents:
            component.container = self.proxy

#==============================================================#
# Menu

class MenuItemMixin:

    itemId = -1
    parentWidget = None

    def widgetFactory(self,*args,**kws):
        return None

    def createIfNeeded(self):
        if self.widget is None: self.create()

    def setEnabled(self,enabled):
        if self.proxy.container is not None \
		   and self.proxy.container.wrapper.widget is not None:
            self.proxy.container.wrapper.rebuild()

    def setContainer(self,container):
        if not container:
            if self.proxy.container is not None:
                if self.proxy in self.proxy.container.contents:
                    self.proxy.container.contents.remove(self.proxy)
                self.widget = None
                self.proxy.container.wrapper.rebuild()
        else:
            self.createIfNeeded()
            self.proxy.container.wrapper.rebuild()

    def setText(self,text):
        if self.proxy.container is not None \
            and self.proxy.container.wrapper.widget is not None:
            self.proxy.container.wrapper.rebuild()

    def getText(self):
        return self.proxy.text

    def enterMainLoop(self): # ...
        pass

    def internalDestroy(self):
        pass

class MenuWrapper(MenuItemMixin, ComponentWrapper):

    def widgetFactory(self,*args,**kws):
        return QPopupMenu(*args,**kws)

    def setContainer(self,container):
        if container is None:
            if self.widget is not None:
                if self.proxy in self.proxy.container.contents:
                    self.proxy.container.contents.remove(self.proxy)
                #print "DESTROYING",self
                self.widget.destroy()
                self.widget = None
                self.proxy.container.wrapper.rebuild()
        else:
            if container.wrapper.widget is not None:
                self.rebuild()

    def setContents(self,contents):
        self.rebuild()

    def rebuildAll(self):
        """
        Rebuild the entire menu structure starting from the toplevel menu.
        """
        if self.proxy.container is not None and self.widget is not None and \
           self.proxy.container.wrapper.widget is not None:
            proxies = [self.proxy]
            while not isinstance(proxies[-1],Window):
                proxies.append(proxies[-1].container)
                proxies[-2].wrapper.rebuild()

    def rebuild(self):
        """
        Rebuild the menu structure of self and all children; re-add
        self to parent.
        """
        if self.proxy.container is not None and \
		   self.proxy.container.wrapper.widget is not None:
            parent = self.proxy.container.wrapper.widget
            if DEBUG: print "\nREBUILDING: ", self,self.proxy.contents
            if self.widget is not None:
                self.widget.clear()
            else:
                if isinstance(self.proxy.container, Window):
                    self.create(parent)
                else:
                    self.create(None)
            
            for item in self.proxy.contents:
                item.wrapper.createIfNeeded()
                item.wrapper.insertInto(self.widget)
                if item.wrapper.itemId != -1:
                    self.widget.setItemEnabled(item.wrapper.itemId, item.enabled)

    def enterMainLoop(self): # ...
        self.proxy.push() # FIXME: Why is this needed when push
		                  # is called in internalProd (by prod)?

    def insertInto(self, widget):
        self.rebuild()
        self.itemId = widget.insertItem(self.proxy.text, self.widget)

class MenuBarWrapper(MenuWrapper):
    def widgetFactory(self,*args,**kws):
        parent = args[0].parent()
        widget = parent.menuBar()
        widget.clear()
        return widget
    

class MenuCommandWrapper(MenuItemMixin, AbstractWrapper):

    def insertInto(self, widget):
        self.parentWidget = widget
        self.itemId = widget.insertItem(self.proxy.text, self.clickHandler)

    def clickHandler(self,*args,**kws):
        if DEBUG: print "CLICKED: ", self
        send(self.proxy,'click',text=self.proxy.text)

class MenuCheckWrapper(MenuCommandWrapper):
    checked = 0

    def insertInto(self, widget):
        MenuCommandWrapper.insertInto(self, widget)
        self.parentWidget.setItemChecked(self.itemId, self.checked)

    def setOn(self,on):
        self.checked = on
        if self.parentWidget:
            self.parentWidget.setItemChecked(self.itemId, on)

    def getOn(self):
        return self.checked

    def clickHandler(self,*args,**kws):
        self.setOn(not self.getOn())
        MenuCommandWrapper.clickHandler(self,*args,**kws) 


class MenuSeparatorWrapper(MenuItemMixin, AbstractWrapper):
    
    def insertInto(self, widget):
        widget.insertSeparator()

#==============================================================#

class Application(AbstractApplication, QApplication):

    def __init__(self, **kwds):
        AbstractApplication.__init__(self, **kwds)
        QApplication.__init__(self,[])

    def internalRun(self):
        qApp.exec_loop()

    def internalRemove(self):
        if not self._windows:
            qApp.quit()

    def quit(self):
        qApp.quit()

#==============================================================#
