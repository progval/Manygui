from anygui import *
from anygui.Utils import log

class SelectionPrinter(ListBox):

    def __init__(self, lb):
        self._lb = lb
        link(lb, self.print_selection)

    def print_selection(self, **kw):
        log('Item selected:', self._lb.selection, '(%s)' % self._lb.items[self._lb.selection])

app = Application()

lb = ListBox()

sp = SelectionPrinter(lb)

lb.items = ListModel('There was a wee cooper of county Fyfe, Nickety, nockety, noo, noo, noo'.split())
lb.items.value = 'There was a wee cooper of county Fyfe, Nickety, nockety, noo, noo, noo'.split()
lb.selection = 2

win = Window(title='ListBox test', width=200, height=200)
app.add(win)

win.add(lb, left=25, top=25, right=25, bottom=25,
          vstretch=1, hstretch=1)

app.run()
