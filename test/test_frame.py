from anygui import *

app = Application()
win = Window()
num = 1
fms = [Frame() for i in range(1)]
for frm, i in zip(fms,range(1)):
    lbl = Label(text='This is Frame number %s.' % i, width=200)
    frm.add(lbl)
    win.add(frm)
app.run()
