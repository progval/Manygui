from anygui import *

app = Application()

btn = Button()
cbx = CheckBox()
lbl = Label()
lst = ListBox()
rdb = RadioButton()
txa = TextArea()
txf = TextField()
win = Window()

win.place(btn, cbx, lbl, lst, rdb, txa, txf, direction='down')

app.run()
