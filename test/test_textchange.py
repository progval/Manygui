from anygui import *
from anygui.Utils import log

app = Application()
btn = Button(text='Before')
cbx = CheckBox(text='Before')
rbn = RadioButton(text='Before')
lbl = Label(text='Before')

cng = Button(text='Change')

cmps = btn, cbx, rbn, lbl

def change(**kw):
    for cmp in cmps:
        cmp.text = 'After'

link(cng, change)

win = Window(width=btn.width, height=145)
app.add(win)
win.add(cmps+(cng,), direction='down')
app.run()
