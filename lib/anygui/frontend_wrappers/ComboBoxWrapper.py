import anygui
from anygui.Wrappers import AbstractWrapper
from anygui.Events import link, send
from time import sleep

"""
This is a generic implementation of the ComboBox that is provided for
backends that do not provide the ComboBox widget in their respective
toolkits. This also models the creation of Mega-widgets using the
Anygui GUI API.
"""

#==============================================================#
# Factoring out creational code...

class Wrapper(AbstractWrapper):

    def __init__(self, *args, **kwds):
        AbstractWrapper.__init__(self, *args, **kwds)

        # 'container' before everything...
        self.setConstraints('container','x','y','width','height','items','selection')
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

    def rebuild(self): pass

    def rebuildAll(self): pass

#==============================================================#

class ComboBoxWrapper(Wrapper):
    _connected = 0
    _comps     = 0
    _textFld  = None
    _popupBtn = None
    _itemLbx = None
    _currentItem = 0
    _popupOpen = 0
    _visible = 1
    _enabled = 1
    _loop = 0
    _btnWidth = 0
    _lbxHeight = 0
    _cbxHeight = 0


    def _createWidgets(self):
        state = self.proxy.state
        lx = state['x']
        ly = state['y']
        lwidth = state['width']
        lheight = state['height']
        self._btnWidth = state['btnWidth']
        self._lbxHeight = state['lbxHeight']
        self._cbxHeight = state['cbxHeight']
        litems = list(self.proxy.items)
        self._popupBtn = anygui.Button(text = 'v',
                                       geometry = ( lx + lwidth - self._btnWidth,
                                                    ly,
                                                    self._btnWidth,
                                                    self._cbxHeight ))
        self._textFld  = anygui.TextField(geometry = ( lx,
                                                       ly,
                                                       lwidth - self._btnWidth,
                                                       self._cbxHeight ))
        self._itemLbx = anygui.ListBox(visible = 0,
                                       items = litems,
                                       geometry = ( lx,
                                                    ly + lheight,
                                                    lwidth,
                                                    self._lbxHeight ))


    def _setupBtn(self):
        self._popupBtn.container = self.proxy.container
        self.proxy.container.contents.append(self._popupBtn)

    def _setupTxtFld(self):
        self._textFld.container = self.proxy.container
        self.proxy.container.contents.append(self._textFld)

    def _setupLbx(self):
        self._itemLbx.container = self.proxy.container
        self.proxy.container.contents.append(self._itemLbx)

    def widgetFactory(self, *args, **kws):
        print '>> in widgetFactory...'
        self._createWidgets()
        self._comps = 1
        class Class: pass
        widget = Class()
        return widget

    def widgetSetUp(self):
        if self._comps and not self._connected:
            print '>> in widgetSetUp'
            #self._popupBtn._ensure_events()
            link(self._popupBtn, self._handlePopup)
            #self._itemLbx._ensure_events()
            link(self._itemLbx, self._handleSelection)
            self._connected = 1

    def setupChildWidgets(self):
        if self._comps:
            print '>> in setupChildWidgets'
            self._setupTxtFld()
            self._setupBtn()
            self._setupLbx()

    def setContainer(self, container):
        if container is None: return
        parent = container.wrapper.widget
        try:
            assert parent is None
        except (AssertionError):
            self.create(parent)
            self.proxy.push(blocked=['container'])
            self.setupChildWidgets()

    def getSelection(self):
        if self._comps:
            return self._itemLbx.selection

    def setSelection(self, selection):
        if self._comps:
            self._loop = 1
            self._itemLbx.selection = selection
            self._textFld.text = self._itemLbx.items[selection]
            self._loop = 0

    def getItems(self):
        if self._comps:
            return self._itemLbx.items

    def setItems(self, items):
        if self._comps:
            print '>> in setItems(items) -> ', items
            self._loop = 1
            self._itemLbx.items = items
            self._loop = 0

    def _handlePopup(self, event):
        print '>> handling Popup...'
        self._loop = 1
        self._itemLbx.visible = self._popupOpen = not self._popupOpen
        self._loop = 0

    def _handleSelection(self, event):
        print '>> handling Selection...'
        if not self._loop:
            self._loop = 1
            self._textFld.text = self._itemLbx.items[self._itemLbx.selection]
            self._itemLbx.visible = 0
            sleep(0.1)
            self._popupOpen = 0
            send(self.proxy, 'select')
            self._loop = 0

    def setX(self, x):
        if self._comps:
            dummy, y, width, height = self.geometry
            self.setGeometry(x, y, width, height)

    def setY(self, y):
       if self._comps:
            x, dummy, width, height = self.geometry
            self.setGeometry(x, y, width, height)

    def setWidth(self, width):
       if self._comps:
            x, y, dummy, height = self.geometry
            self.setGeometry(x, y, width, height)

    def setHeight(self, height):
       if self._comps:
            x, y, width, dummy = self.geometry
            self.setGeometry(x, y, width, height)

    def setPosition(self, x, y):
       if self._comps:
            dummy, dummy2, width, height = self.geometry
            self.setGeometry(x, y, width, height)

    def setSize(self, width, height):
       if self._comps:
            x, y, dummy, dummy2 = self.geometry
            self.setGeometry(x, y, width, height)

    def getGeometry(self):
        if self._comps:
            x, y, dummy, height = self._textFld.geometry
            d, d1, width, d2   = self._itemLbx.geometry
            return (x, y, height, width)

    def setGeometry(self, x, y, width, height):
        if self._comps:
            self._loop = 1
            self._textFld.geometry  = (x,
                                       y,
                                       width - self._btnWidth,
                                       self._cbxHeight)
            self._popupBtn.geometry = (x + width - self._btnWidth,
                                       y,
                                       self._btnWidth,
                                       self._cbxHeight)
            self._itemLbx.geometry =  (x,
                                       y + self._cbxHeight,
                                       width,
                                       self._lbxHeight)
            self._loop = 0

    def getVisible(self):
        return self._visible

    def setVisibile(self, visible):
        if self._comps:
            self._visible = visible
            self._textFld.visible = visible
            self._popupBtn.visible = visible

    def setEnabled(self, enabled):
        if self._comps:
            self._enabled = enabled
            self._textFld.enabled  = enabled
            self._popupBtn.enabled = enabled

    def getEnabled(self):
        return self._enabled

    def internalDestroy(self):
        if self._comps:
            self._connected = 0
            self._textFld.destroy()
            self._popupBtn.destroy()
            self._itemLbx.destroy()
            self._comps = 0
