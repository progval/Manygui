from __future__ import nested_scopes
from anygui import Window, Label, Button, TextArea, ListBox, Frame, TextField
from anygui import application, link
from anygui.LayoutManagers import SimpleGridManager
import re
import sys, glob, os

PATH_SEPAR=''
ROOT_PATH=''
if sys.platform in ['win32', 'dos', 'ms-dos']:
    PATH_SEPAR = '\\'
    ROOT_PATH  = '[a-zA-Z]:\\\\(?!.)'
elif sys.platform in ['cygwin','linux1', 'linux2', 'sunos5']:
    PATH_SEPAR = '/'
    ROOT_PATH  = '/(?!.)'

DIRS_FIRST=0
def sort_dirs_first(x, y):
    if x.endswith(PATH_SEPAR) and y.endswith(PATH_SEPAR):
        pass
    elif x.endswith(PATH_SEPAR):
        return -1
    elif y.endswith(PATH_SEPAR):
        return 1
    return cmp(x, y)

SORT_RULES={DIRS_FIRST: sort_dirs_first}

class DirManager:

    def __init__(self, dir, filter, sort_rule=DIRS_FIRST):
        print '>> dir    -> ', dir
        print '>> filter -> ', filter
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
        cache = glob.glob(dir + self.filter)
        objCache = [ obj[obj.rfind(PATH_SEPAR)+1:] for obj in cache ]
        for i in range(len(cache)):
            if os.path.isdir(cache[i]):
                objCache[i] += PATH_SEPAR
        objCache.sort(SORT_RULES[self.sortRule])
        return objCache

    def _genDirCaches(self):
        print '>> self.currDir -> ', self.currDir
        self.currDirCache = self.globDir(self.currDir)
        # now generate cache for self.dir/..
        if not self.currDirIsRoot():
            self.oneDirUp = self.dirUp(self.currDir)
            print '>> self.oneDirUp -> ', self.oneDirUp
            self.oneDirUpCache = self.globDir(self.oneDirUp)
            # and the same for self.dir/../..
            if not self.isRootDir(self.oneDirUp):
                self.twoUpDir = self.dirUp(self.oneDirUp)
                print '>> self.twoDirUp -> ', self.twoDirUp
                self.twoDirUpCache = self.globDir(self.twoDirUp) 

class AnyguiOpenFileDlg(Window):

    def __init__(self, dir, filter, sort_rule=DIRS_FIRST):
        Window.__init__(self, title='Open File - ' + application().name + '-' + application().version,\
                        geometry=(250, 200, 420, 350))
        self._updating = 0
        self.dirMngr = DirManager(dir, filter, sort_rule)
        self.initWidgets()

    def initWidgets(self):

        btnDirBack = self.btnDirBack = Button(text='<', size=(50,25))
        if self.dirMngr.currDirIsRoot():
            btnDirBack.enabled = 0
        self.add(btnDirBack, left=10, top=10)
        link(btnDirBack, self.goDirBack)

        btnDirFwd = self.btnDirFwd = Button(text='>', size=(50,25))
        btnDirFwd.enabled = 0
        self.add(btnDirFwd, left=(btnDirBack, 5), top=10)
        link(btnDirFwd, self.goDirFwd)

        frmDirs = self.frmDirs = Frame()
        frmDirs.layout = SimpleGridManager(3,1)
        self.add(frmDirs, left=10, rigth=10, top=(btnDirBack, 5), bottom=75, vstretch=1, hstretch=1)
        
        lbxDirOne = self.lbxDirOne = ListBox()
        lbxDirOne.items = self.dirMngr.currDirCache
        lbxDirOne.selection = 0
        frmDirs.add(lbxDirOne)
        link(lbxDirOne, self.lbxSelect)

        lbxDirTwo = self.lbxDirTwo = ListBox()
        frmDirs.add(lbxDirTwo)
        link(lbxDirTwo, self.lbxSelect)

        lbxDirThree = self.lbxDirThree = ListBox()
        frmDirs.add(lbxDirThree)
        link(lbxDirThree, self.lbxSelect)

        btnCancel = self.btnCancel = Button(text='Cancel')
        self.add(btnCancel, right=10, top=(frmDirs, 5), hmove=1, vmove=1)
        link(self.btnCancel, self.close)        

        btnOpen = self.btnOpen = Button(text='Open')
        self.add(btnOpen, right=10, top=(btnCancel, 5), hmove=1, vmove=1)
        link(self.btnOpen, self.open)

        lblLocation = self.lblLocation = Label(text='Location:', width=55)
        self.add(lblLocation, left=10, top=(frmDirs, 18), vmove=1)

        lblFilter = self.lblFilter = Label(text='Filter:', width=55)
        self.add(lblFilter, left=10, top=(lblLocation, 20), vmove=1)

        txtLocation = self.txtLocation = TextField(text=self.dirMngr.currDir)
        self.add(txtLocation, left=(lblLocation, 5), right=100, top=(frmDirs, 8), hstretch=1, vmove=1)
        link(txtLocation, self.changeDirs)

        txtFilter = self.txtFilter = TextField(text='*.*')
        self.add(txtFilter, left=(lblFilter, 5), right=100, top=(txtLocation, 10), hstretch=1, vmove=1)
        link(txtFilter, self.applyFilter)

    def open(self, event):
        print ">> Got event: ", event
        print ">> event dict: ", event.__dict__        

    def close(self, event):
        self.destroy()

    def lbxSelect(self, event):
        if self._updating: return
        source = event.source
        if source is self.lbxDirOne:
            self.handleLbxDirOneEvent()
        elif source is self.lbxDirTwo:
            self.handleLbxDirTwoEvent()
        elif source is self.lbxDirThree:
            self.handleLbxDirThreeEvent()

    def handleLbxDirOneEvent(self):
        self_updating = 1
        dirMngr = self.dirMngr
        s = self._state()
        obj = dirMngr.currDir + s.dirOne
        if os.path.isdir(obj):
            dirMngr.filter = self.txtFilter.text
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
        self._updating = 0
    
    def handleLbxDirTwoEvent(self):
        self._updating = 1
        dirMngr = self.dirMngr
        s = self._state()
        obj = dirMngr.currDir + s.dirOne + s.dirTwo
        if os.path.isdir(obj):
            dirMngr.filter = self.txtFilter.text
            result = dirMngr.globDir(obj)
            s.lbxThree.items = result
        else:
            s.lbxThree.items = []
        self.txtLocation.text = obj
        self._updating = 0

    def handleLbxDirThreeEvent(self):
        self._updating = 1
        dirMngr  = self.dirMngr
        s = self._state()
        obj = dirMngr.currDir + s.dirOne + s.dirTwo + s.dirThree

        if os.path.isdir(obj):
            dirMngr.currDir += s.dirOne
            dirMngr.update()
            s.lbxOne.items = dirMngr.currDirCache
            s.lbxOne.selection = s.selTwo
            dirMngr.filter = self.txtFilter.text
            s.lbxTwo.items = dirMngr.globDir(dirMngr.currDir + s.dirTwo)
            s.lbxTwo.selection = s.selThree
            s.lbxThree.items = dirMngr.globDir(obj)

            self.btnDirBack.enabled = 1
            
        self.txtLocation.text = obj
        self._updating = 0

    def goDirFwd(self, event):
        print ">> Got event: ", event
        print ">> event dict: ", event.__dict__
        self._updating = 1

        self._updating = 0


    def goDirBack(self, event):
        print ">> Got event: ", event
        print ">> event dict: ", event.__dict__

        self._updating = 1
        
        dirMngr = self.dirMngr
        s = self._state()

        backDir = dirMngr.currDir
        currDir = dirMngr.currDir = dirMngr.oneDirUp
        dirMngr.update()

        s.lbxOne.items = dirMngr.currDirCache
        s.lbxOne.selection = s.lbxOne.items.index(\
            backDir[backDir[:-1].rfind(PATH_SEPAR)+1:]\
        )
        
        s.lbxTwo.items = s.itemsOne
        s.lbxTwo.selection = s.selOne

        s.lbxThree.items = s.itemsTwo
        s.lbxThree.selection = s.selTwo

        if dirMngr.currDirIsRoot():
            self.btnDirBack.enabled = 0

        s = self._state()
        self.txtLocation.text = currDir + s.dirOne + s.dirTwo + s.dirThree
        self._updating = 0
        
    def changeDirs(self, event):
        print ">> Got event: ", event
        print ">> event dict: ", event.__dict__

    def applyFilter(self, event):
        print ">> Got event: ", event
        print ">> event dict: ", event.__dict__

    def _state(self):

        class State:
            def __str__(self):
                return str(self.__dict__)
            pass

        s = State()
        
        s.lbxOne   = self.lbxDirOne
        s.selOne   = s.lbxOne.selection
        s.itemsOne = s.lbxOne.items
        s.dirOne   = s.lbxOne.items[s.selOne]

        try: 
            s.lbxTwo   = self.lbxDirTwo
            s.selTwo   = s.lbxTwo.selection
            s.itemsTwo = s.lbxTwo.items
            s.dirTwo   = s.lbxTwo.items[s.selTwo]

            s.lbxThree   = self.lbxDirThree
            s.selThree   = s.lbxThree.selection
            s.itemsThree = s.lbxThree.items
            s.dirThree   = s.lbxThree.items[s.selThree]
        except (IndexError):
            pass

        return s
