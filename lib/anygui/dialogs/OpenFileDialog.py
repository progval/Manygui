from __future__ import nested_scopes

from anygui import Window, Label, Button, TextArea, ListBox, Frame, TextField
from anygui import application, link
from anygui.Models import ListModel
from anygui.LayoutManagers import SimpleGridManager

from UserList import UserList
import re
import sys, glob, os

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

class DirListModel(ListModel):

    def __init__(self, *arg, **kw):
        try:
            self.sortRule = kw['sort_rule']
        except:
            self.sortRule = DIRS_FIRST
        assert kw.has_key('filter'), \
               '!! cannot create a DirListModel without a filter.'
        ListModel.__init__(self, **kw)

    def setValue(self, value):
        value.sort(SORT_RULES[self.sortRule])
        self.data = value
        self.send()

class DirListNode:

    def __init__(self, dir_list):
        self.dirList = dir_list
        self.prev = None
        self.next = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.dirList)

class TripanedDoublyLinkedList:

    def __init__(self, dirs):
        assert isintance(dirs, list) and len(dirs)>=1, \
               '!! must construct with at least one dir.'
        tripane = self.tripane = [None,None,None]
        self.head = tripane[0] = DirListNode(dirs[0])
        try:
            node = tripane[1] = DirListNode(dirs[1])
            self.appendNode(node)
        except:
            return
        try:
            node = tripane[2] = DirListNode(dirs[2])
            self.appendNode(node)
        except:
            return

    def __str__(self):
        nlist = []
        node = self.head
        while node:
            if node in self.tripane:
                nlist.append([node])
            else:
                nlist.append(node)
            node = node.next
        return str(nlist)

    def prepend(self, dir):
        node = DirListNode(dir)
        self.prependNode(node)

    def prependNode(self, node):            
        head = self.head
        head.prev = node
        node.next = head
        self.head = node
        if not hasattr(self, 'tail'):
            self.tail = head

    def append(self, dir):
        node = DirListNode(dir)
        self.appendNode(node)

    def appendNode(self, node):
        if hasattr(self, 'tail'):
            tail = self.tail
            tail.next = node
            node.prev = tail
            self.tail = node
            if self.tripane[2] is None:
                self.tripane[2] = node
        else:
            self.tripane[1] = self.tail = node
            self.head.next = node
            node.prev = self.head

    def pop(self):
        assert hasattr(self, 'tail'), '!! cannot pop last node.'
        if self.tail.prev == self.head:
            tail = self.tail
            del self.tail 
            tail.prev = None
            self.head.next = None
            if tail in self.tripane:
                self.tripane[self.tripane.index(tail)] = None
            return tail
        tail = self.tail
        self.tail = tail.prev
        self.tail.next = None
        tail.prev = None
        if tail in self.tripane:
            self.tripane[self.tripane.index(tail)] = None
        return tail

    def count(self):
        node = self.head
        count = 0
        while node:
            count += 1
            node = node.next
        return count

    def shiftPaneBack(self, nbr):
        for i in range(nbr):
            try:
                self.tripane[0] = self.tripane[0].prev
                self.tripane[1] = self.tripane[1].prev
                self.tripane[2] = self.tripane[2].prev
            except:
                break

    def shiftPaneFwd(self, nbr):
        for i in range(nbr):
            try:
                self.tripane[0] = self.tripane[0].next
                self.tripane[1] = self.tripane[1].next
                self.tripane[2] = self.tripane[2].next
            except:
                break

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

class OpenFileDialog(Window):

    def __init__(self, dir, filter, sort_rule=DIRS_FIRST):
        Window.__init__(self, title='Open File - ' + \
                        application().name + '-' + application().version, \
                        geometry=(250, 200, 420, 350))
        self._updating = 0
        dirMngr = self.dirMngr = DirManager(dir, filter, sort_rule)
        self._priorSelections = []
        #self.createTripaneDirList()
        self.initWidgets()

    #def createTripaneDirList(self):
    #    dirMngr = self.dirMngr
    #    self.dirList = TripanedDoublyLinkedList([dirMngr.currDirCache])
    #    if not dirMngr.currDirIsRoot():
    #        self.dirList.prepend(dirMngr.oneDirUpCache)
    #        if not dirMngr.isRootDir(dirMngr.oneDirUp):
    #            self.dirList.prepend(dirMngr.twoDirUpCache)

    def initWidgets(self):

        dirMngr = self.dirMngr

        btnDirBack = self.btnDirBack = Button(text='<', size=(50,25))
        if dirMngr.currDirIsRoot():
            btnDirBack.enabled = 0
        self.add(btnDirBack, left=10, top=10)
        link(btnDirBack, self.goDirBack)

        btnDirFwd = self.btnDirFwd = Button(text='>', size=(50,25))
        btnDirFwd.enabled = 0
        self.add(btnDirFwd, left=(btnDirBack, 5), top=10)
        link(btnDirFwd, self.goDirFwd)

        frmDirs = self.frmDirs = Frame()
        frmDirs.layout = SimpleGridManager(3,1)
        self.add(frmDirs, left=10, rigth=10, top=(btnDirBack, 5), \
                 bottom=75, vstretch=1, hstretch=1)

        lbxDirOne = self.lbxDirOne = ListBox()
        #lbxDirOne.items = self.dirList.tripane[0]
        lbxDirOne.items = self.dirMngr.currDirCache
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

        txtLocation = self.txtLocation = TextField(text=dirMngr.currDir)
        self.add(txtLocation, left=(lblLocation, 5), right=100, top=(frmDirs, 8), \
                 hstretch=1, vmove=1)
        link(txtLocation, self.changeDirs)

        txtFilter = self.txtFilter = TextField(text=dirMngr.filter)
        self.add(txtFilter, left=(lblFilter, 5), right=100, top=(txtLocation, 10), \
                 hstretch=1, vmove=1)
        link(txtFilter, self.applyFilter)

    def open(self, event):
        print ">> Got event: ", event
        print ">> event dict: ", event.__dict__

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
        print '>> handling lbxDirOne event'
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

    def handleLbxDirTwoEvent(self):
        print '>> handling lbxDirTwo event'
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

    def handleLbxDirThreeEvent(self):
        print '>> handling lbxDirThree event'
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

    def goDirFwd(self, event):
        print ">> Got event: ", event
        print ">> event dict: ", event.__dict__
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
        print ">> Got event: ", event
        print ">> event dict: ", event.__dict__

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
        print ">> Got event: ", event
        print ">> event dict: ", event.__dict__
        self._update = 1

        dirMngr = self.dirMngr
        s = self._state()

        try:
            s.dirThree
            print '>> filtering lbxThree'
            self.handleLbxDirTwoEvent()
            return
        except (AttributeError):
            pass

        try:
            s.dirTwo
            print '>> filtering lbxTwo'
            self.handleLbxDirOneEvent()
            return
        except (AttributeError):
            pass

        print '>> filtering lbxOne'
        dirMngr.filter = self.txtFilter.text
        dirMngr.update()

        s.lbxOne.items = dirMngr.currDirCache
        try:
            selection = s.lbxOne.selection = dirMngr.currDirCache.index(s.dirOne)
            self.txtLocation.text = dirMngr.currDir + dirMngr.currDirCache[selection]
        except (AttributeError, ValueError):
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
