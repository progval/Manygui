from anygui import *

app = Application()

btn = Button()
cbx = CheckBox()
lbl = Label()
lst = ListBox()
rdb = RadioButton()
txa = TextArea()
txf = TextField()

win = Window(size=(120,405))
win.place(btn, cbx, lbl, lst, rdb, txa, txf,
          direction='down',
          left=10, top=10)

app.run()