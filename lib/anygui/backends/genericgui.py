#==============================================================#
# Imports
from __future__ import nested_scopes

# For Widgets
import anygui
from anygui.Wrappers import AbstractWrapper
from anygui.Events import link, send
from time import sleep

# For Dialogs
from anygui.Models import ListModel
from anygui.LayoutManagers import SimpleGridManager
from UserList import UserList
import re
import sys, glob, os
import traceback

# End Imports
#==============================================================#

__all__="""

ComboBoxWrapper
AboutDialog
OpenFileDialog

""".split()

#==============================================================#
# Widgets
#--------------------------------------------------------------#
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

#--------------------------------------------------------------#

class ComboBoxWrapper(Wrapper):
    """This is a generic implementation of the ComboBox that is provided for
       backends that do not provide the ComboBox widget in their respective
       toolkits. This also models the creation of Mega-widgets using the
       Anygui GUI API."""

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
        x = state['x']
        y = state['y']
        width = state['width']
        height = state['height']
        self._lbxHeight = state['lbxHeight']
        items = list(self.proxy.items)
        self._textFld  = anygui.TextField(geometry = ( x,
                                                       y,
                                                       width - height,
                                                       height ))
        self._popupBtn = anygui.Button(text = 'v',
                                       geometry = ( x + width - height,
                                                    y,
                                                    height,
                                                    height ))
        self._itemLbx = anygui.ListBox(visible = 0,
                                       items = items,
                                       geometry = ( x,
                                                    y + height,
                                                    width,
                                                    self._lbxHeight ))


    def _setupBtn(self):
        self._popupBtn.container = self.proxy.container

    def _setupTxtFld(self):
        self._textFld.container = self.proxy.container

    def _setupLbx(self):
        self._itemLbx.container = self.proxy.container

    def widgetFactory(self, *args, **kws):
        #print '>> in widgetFactory...'
        self._createWidgets()
        self._comps = 1
        class Class: pass
        widget = Class()
        return widget

    def widgetSetUp(self):
        if self._comps and not self._connected:
            #print '>> in widgetSetUp'
            link(self._popupBtn, self._handlePopup)
            link(self._itemLbx, self._handleSelection)
            self._connected = 1

    def setupChildWidgets(self):
        if self._comps:
            #print '>> in setupChildWidgets'
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

    def _handlePopup(self, event):
        #print '>> handling Popup...'
        self._loop = 1
        self._itemLbx.visible = self._popupOpen = not self._popupOpen
        self._loop = 0

    def _handleSelection(self, event):
        #print '>> handling Selection...'
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
            return (x, y, width, height)

    def setGeometry(self, x, y, width, height):
        if self._comps:
            self._loop = 1
            self._textFld.geometry  = (x,
                                       y,
                                       width - height,
                                       height)
            self._popupBtn.geometry = (x + width - height,
                                       y,
                                       height,
                                       height)
            self._itemLbx.geometry =  (x,
                                       y + height,
                                       width,
                                       self._lbxHeight)
            self._loop = 0

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
            #print '>> in setItems(items) -> ', items
            self._loop = 1
            self._itemLbx.items = items
            self._loop = 0

    def getText(self):
        items = list(self._itemLbx.items)
        text = self._textFld.text
        if text in items:
            return text
        else:
            return items[self._itemLbx.selection]

    def getLbxHeight(self):
        return self._lbxHeight

    def setLbxHeight(self, lbxHeight):
        if self._comps:
            self._lbxHeight = lbxHeight
            x, y, width, height = self.proxy.geometry
            self._itemLbx.geometry = ( x,
                                       y + height,
                                       width,
                                       lbxHeight)

    def getVisible(self):
        return self._visible

    def setVisibile(self, visible):
        if self._comps:
            self._visible = visible
            if self._popupOpen:
                self._itemLbx.visible = visible
                self._popupOpen = visible
            self._textFld.visible = visible
            self._popupBtn.visible = visible

    def getEnabled(self):
        return self._enabled

    def setEnabled(self, enabled):
        if self._comps:
            if self._popupOpen:
                self._itemLbx.visible = 0
                self._popupOpen = 0
            self._enabled = enabled
            self._textFld.enabled  = enabled
            self._popupBtn.enabled = enabled

    def internalDestroy(self):
        if self._comps:
            self._connected = 0
            self._textFld.destroy()
            self._popupBtn.destroy()
            self._itemLbx.destroy()
            self._comps = 0

#==============================================================#
# Dialogs

#--------------------------------------------------------------#
# About Anygui Dialog

ABOUT_TEXT="""
The purpose of the Anygui project is to create an easy-to-use, simple, \
and generic module for making graphical user interfaces in Python. \
Its main feature is that it works transparently with many different \
GUI packages on most platforms.
"""

class AboutDialog(anygui.Window):

    def __init__(self):
        anygui.Window.__init__(self, title='About Anygui', geometry=(250, 200, 300, 225))
        self.initWidgets()

    def initWidgets(self):
        #self.layout = SimpleGridManager(1,3)
        self.label = anygui.Label(text="Anygui info:")
        self.add(self.label, left=10, top=10)
        self.txtAbout = anygui.TextArea(text=ABOUT_TEXT, enabled=0)
        self.add(self.txtAbout, left=10, right=10, top=(self.label,5), \
                 bottom=45, hstretch=1, vstretch=1)
        self.btnOK = anygui.Button(text="OK")
        self.add(self.btnOK, right=10, bottom=10, hmove=1, vmove=1)
        link(self.btnOK, self.close)

    def close(self, event):
        self.destroy()


#--------------------------------------------------------------#
# FileDialog

PATH_SEPAR=''
ROOT_PATH=''
if sys.platform in ['win32', 'dos', 'ms-dos']:
    PATH_SEPAR = '\\'
    ROOT_PATH  = '[a-zA-Z]:\\\\(?!.)'
else:
    PATH_SEPAR = '/'
    ROOT_PATH  = '/(?!.)'

# === SORT_RULES === #

ALPHABETICAL=0
# uses cmp

DIRS_FIRST=1
def sort_dirs_first(x, y):
    if x.endswith(PATH_SEPAR) and y.endswith(PATH_SEPAR):
        pass
    elif x.endswith(PATH_SEPAR):
        return -1
    elif y.endswith(PATH_SEPAR):
        return 1
    return cmp(x, y)

FILES_FIRST=2
def sort_files_first(x, y):
    if x.endswith(PATH_SEPAR) and y.endswith(PATH_SEPAR):
        pass
    elif x.endswith(PATH_SEPAR):
        return 1
    elif y.endswith(PATH_SEPAR):
        return -1
    return cmp(x, y)

SORT_RULES={ALPHABETICAL: cmp, DIRS_FIRST: sort_dirs_first,\
            FILES_FIRST: sort_files_first}

# == END SORT_RULES == #

class DirManager:

    def __init__(self, dir, filter, sort_rule=DIRS_FIRST):
        #print '>> dir    -> ', dir
        #print '>> filter -> ', filter
        assert os.path.isdir(dir), '!! DirManager: ' + dir + ' is not a directory.'
        if not dir.endswith(PATH_SEPAR):
            dir += PATH_SEPAR
        self.currDir = dir
        self.filter = filter
        self.sortRule = sort_rule

        self.currDirCache = []
        self.oneDirUp = ''
        self.oneDirUpCache = []
        self.twoDirUp = ''
        self.twoDirUpCache = []
        self._genDirCaches()

    def update(self):
        self._genDirCaches()

    def isRootDir(self, dir):
        if dir == ROOT_PATH or re.match(ROOT_PATH, dir):
            return 1
        else:
            return 0

    def currDirIsRoot(self):
        return self.isRootDir(self.currDir)

    def dirUp(self, dir):
        return dir[:dir[:-1].rfind(PATH_SEPAR)+1]

    def goDirUp():
        self.currDir = self.oneDirUp
        self._genDirCaches()

    def globDir(self, dir):
        if self.filter == '':
            self.filter = '*'
        cache = glob.glob(dir + self.filter)
        objCache = [ obj[obj.rfind(PATH_SEPAR)+1:] for obj in cache ]
        for i in range(len(cache)):
            if os.path.isdir(cache[i]):
                objCache[i] += PATH_SEPAR
        objCache.sort(SORT_RULES[self.sortRule])
        return objCache

    def _genDirCaches(self):
        #print '>> self.currDir -> ', self.currDir
        self.currDirCache = self.globDir(self.currDir)
        # now generate cache for self.dir/..
        if not self.currDirIsRoot():
            self.oneDirUp = self.dirUp(self.currDir)
            #print '>> self.oneDirUp -> ', self.oneDirUp
            self.oneDirUpCache = self.globDir(self.oneDirUp)
            # and the same for self.dir/../..
            if not self.isRootDir(self.oneDirUp):
                self.twoUpDir = self.dirUp(self.oneDirUp)
                #print '>> self.twoDirUp -> ', self.twoDirUp
                self.twoDirUpCache = self.globDir(self.twoDirUp)


class OpenFileDialog(anygui.Window):

    def __init__(self, dir, filters, sort_rule=DIRS_FIRST):
        anygui.Window.__init__(self, title='Open File - ' + \
                        anygui.application().name + '-' + anygui.application().version, \
                        geometry=(250, 200, 420, 350))
        self._updating = 0
        self.dirMngr = DirManager(dir, filters[0], sort_rule)
        self._priorSelections = []
        #self.createTripaneDirList()
        self.initWidgets(filters)

    #def createTripaneDirList(self):
    #    dirMngr = self.dirMngr
    #    self.dirList = TripanedDoublyLinkedList([dirMngr.currDirCache])
    #    if not dirMngr.currDirIsRoot():
    #        self.dirList.prepend(dirMngr.oneDirUpCache)
    #        if not dirMngr.isRootDir(dirMngr.oneDirUp):
    #            self.dirList.prepend(dirMngr.twoDirUpCache)

    def initWidgets(self, filters):

        dirMngr = self.dirMngr

        btnDirBack = self.btnDirBack = anygui.Button(text='<', size=(50,25))
        if dirMngr.currDirIsRoot():
            btnDirBack.enabled = 0
        self.add(btnDirBack, left=10, top=10)
        link(btnDirBack, self.goDirBack)

        btnDirFwd = self.btnDirFwd = anygui.Button(text='>', size=(50,25))
        btnDirFwd.enabled = 0
        self.add(btnDirFwd, left=(btnDirBack, 5), top=10)
        link(btnDirFwd, self.goDirFwd)

        frmDirs = self.frmDirs = anygui.Frame()
        frmDirs.layout = SimpleGridManager(3,1)
        self.add(frmDirs, left=10, rigth=10, top=(btnDirBack, 5), \
                 bottom=75, vstretch=1, hstretch=1)

        lbxDirOne = self.lbxDirOne = anygui.ListBox()
        #lbxDirOne.items = self.dirList.tripane[0]
        lbxDirOne.items = self.dirMngr.currDirCache
        lbxDirOne.selection = 0
        frmDirs.add(lbxDirOne)
        link(lbxDirOne, self.lbxSelect)

        lbxDirTwo = self.lbxDirTwo = anygui.ListBox()
        frmDirs.add(lbxDirTwo)
        link(lbxDirTwo, self.lbxSelect)

        lbxDirThree = self.lbxDirThree = anygui.ListBox()
        frmDirs.add(lbxDirThree)
        link(lbxDirThree, self.lbxSelect)

        btnCancel = self.btnCancel = anygui.Button(text='Cancel')
        self.add(btnCancel, right=10, top=(frmDirs, 5), hmove=1, vmove=1)
        link(self.btnCancel, self.close)

        btnOpen = self.btnOpen = anygui.Button(text='Open')
        self.add(btnOpen, right=10, top=(btnCancel, 5), hmove=1, vmove=1)
        link(self.btnOpen, self.open)

        lblLocation = self.lblLocation = anygui.Label(text='Location:', width=55)
        self.add(lblLocation, left=10, top=(frmDirs, 18), vmove=1)

        lblFilter = self.lblFilter = anygui.Label(text='Filter:', width=55)
        self.add(lblFilter, left=10, top=(lblLocation, 20), vmove=1)

        txtLocation = self.txtLocation = anygui.TextField(text=dirMngr.currDir)
        self.add(txtLocation, left=(lblLocation, 5), right=100, top=(frmDirs, 8), \
                 hstretch=1, vmove=1)
        link(txtLocation, self.changeDirs)

        cbxFilter = self.cbxFilter = anygui.ComboBox(items=filters)
        #txtFilter = self.txtFilter = TextField(text=dirMngr.filter)
        self.add(cbxFilter, left=(lblFilter, 5), right=100, top=(txtLocation, 10), \
                 hstretch=1, vmove=1)
        link(cbxFilter, self.applyFilter)

    def open(self, event):
        send(self, 'open', file=self.txtLocation.text)
        self.destroy()

    def close(self, event):
        self.destroy()

    def lbxSelect(self, event):
        if self._updating: return
        self_updating = 1
        source = event.source
        if source is self.lbxDirOne:
            self.handleLbxDirOneEvent()
        elif source is self.lbxDirTwo:
            self.handleLbxDirTwoEvent()
        elif source is self.lbxDirThree:
            self.handleLbxDirThreeEvent()
        self.btnDirFwd.enabled = 0
        self._updating = 0

    def handleLbxDirOneEvent(self):
        #print '>> handling lbxDirOne event'
        dirMngr = self.dirMngr
        s = self._state()
        obj = dirMngr.currDir + s.dirOne
        if os.path.isdir(obj):
            dirMngr.filter = self.cbxFilter.text
            result = dirMngr.globDir(obj)
            try:
                s.lbxTwo.items = result
                s.lbxThree.items = []
            except (AttributeError):
                pass
        else:
            try:
                s.lbxTwo.items = []
                s.lbxThree.items = []
            except (AttributeError):
                pass
        self.txtLocation.text = obj

    def handleLbxDirTwoEvent(self):
        #print '>> handling lbxDirTwo event'
        dirMngr = self.dirMngr
        s = self._state()
        obj = dirMngr.currDir + s.dirOne + s.dirTwo
        if os.path.isdir(obj):
            dirMngr.filter = self.cbxFilter.text
            result = dirMngr.globDir(obj)
            s.lbxThree.items = result
        else:
            s.lbxThree.items = []
        self.txtLocation.text = obj

    def handleLbxDirThreeEvent(self):
        #print '>> handling lbxDirThree event'
        dirMngr  = self.dirMngr
        s = self._state()
        obj = dirMngr.currDir + s.dirOne + s.dirTwo + s.dirThree

        if os.path.isdir(obj):
            dirMngr.currDir += s.dirOne
            dirMngr.update()
            s.lbxOne.items = dirMngr.currDirCache
            s.lbxOne.selection = s.selTwo
            dirMngr.filter = self.cbxFilter.text
            s.lbxTwo.items = dirMngr.globDir(dirMngr.currDir + s.dirTwo)
            s.lbxTwo.selection = s.selThree
            s.lbxThree.items = dirMngr.globDir(obj)
            self.btnDirBack.enabled = 1

        self.txtLocation.text = obj

    def goDirFwd(self, event):
        #print ">> Got event: ", event
        #print ">> event dict: ", event.__dict__
        self._updating = 1
        self.handleLbxDirThreeEvent()
        if self._priorSelections:
            priSels = self._priorSelections
            self.lbxDirThree.selection = priSels[0]
            del priSels[0]
        if not self._priorSelections:
            self.btnDirFwd.enabled = 0

        self._updating = 0


    def goDirBack(self, event):
        #print ">> Got event: ", event
        #print ">> event dict: ", event.__dict__

        self._updating = 1

        dirMngr = self.dirMngr
        s = self._state()

        backDir = dirMngr.currDir
        currDir = dirMngr.currDir = dirMngr.oneDirUp
        dirMngr.update()

        s.lbxOne.items = dirMngr.currDirCache
        s.lbxOne.selection = dirMngr.currDirCache.index(\
            backDir[backDir[:-1].rfind(PATH_SEPAR)+1:]\
        )

        s.lbxTwo.items = s.itemsOne
        s.lbxTwo.selection = s.selOne

        s.lbxThree.items = s.itemsTwo
        s.lbxThree.selection = s.selTwo

        self._priorSelections.append(s.selThree)
        self.btnDirFwd.enabled = 1
        if dirMngr.currDirIsRoot():
            self.btnDirBack.enabled = 0

        s = self._state()
        self.txtLocation.text = currDir + s.dirOne + s.dirTwo + s.dirThree

        self._updating = 0

    def changeDirs(self, event):
        print ">> Got event: ", event
        print ">> event dict: ", event.__dict__

    def applyFilter(self, event):
        #print ">> Got event: ", event
        #print ">> event dict: ", event.__dict__
        self._update = 1

        dirMngr = self.dirMngr
        s = self._state()

        try:
            s.dirThree
            #print '>> filtering lbxThree'
            self.handleLbxDirTwoEvent()
            return
        except (AttributeError):
            pass

        try:
            s.dirTwo
            #print '>> filtering lbxTwo'
            self.handleLbxDirOneEvent()
            return
        except (AttributeError):
            pass

        #print '>> filtering lbxOne'
        dirMngr.filter = self.cbxFilter.text
        dirMngr.update()

        s.lbxOne.items = dirMngr.currDirCache
        try:
            selection = s.lbxOne.selection = dirMngr.currDirCache.index(s.dirOne)
            self.txtLocation.text = dirMngr.currDir + dirMngr.currDirCache[selection]
        except (AttributeError, ValueError):
            traceback.print_exc()
            self.txtLocation.text = dirMngr.currDir

        self.btnDirFwd.enabled = 0

        self._update = 0

    def _state(self):

        class State:
            def __str__(self):
                return str(self.__dict__)
            pass

        s = State()

        s.lbxOne   = self.lbxDirOne
        s.itemsOne = s.lbxOne.items
        s.selOne   = s.lbxOne.selection

        try:
            s.dirOne   = s.lbxOne.items[s.selOne]

            s.lbxTwo   = self.lbxDirTwo
            s.itemsTwo = s.lbxTwo.items
            s.selTwo   = s.lbxTwo.selection
            s.dirTwo   = s.lbxTwo.items[s.selTwo]

            s.lbxThree   = self.lbxDirThree
            s.itemsThree = s.lbxThree.items
            s.selThree   = s.lbxThree.selection
            s.dirThree   = s.lbxThree.items[s.selThree]
        except (IndexError):
            pass

        return s
