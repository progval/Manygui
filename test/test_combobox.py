from anygui import *
from anygui.Utils import log

class SelectionPrinter:

    def __init__(self, cb):
        self._cb = cb
        link(cb, self.print_selection)

    def print_selection(self, event):
        log('Item selected:', self._cb.selection, '(%s)' % self._cb.items[self._cb.selection])

app = Application()

cb = ComboBox()

sp = SelectionPrinter(cb)

cb.installItemsModel(ListModel('There was a wee cooper of county Fyfe, Nickety, nockety, noo, noo, noo'.split()))
cb.selection = 2

win = Window(title='ComboBox test', width=200, height=200)
win.add(cb, left=25, top=25, right=25, hstretch=1)

app.add(win)

app.run()
