import sys, os
from anygui import *

filename = sys.argv[1]

app = Application()
win = Window(title='chmod '+filename, size=(280,175))

types  = 'Read Write Execute'.split()
people = 'User Group Others '.split()

# Create and place CheckBoxes and Labels
cbx = {}
x, y = 10, 0
for p in people:
    lbl = Label(text=p)
    lbl.geometry = x, y+10, 80, 15
    win.add(lbl)
    cbx[p] = {}
    for t in types:
        y += 35
        cbx[p][t] = CheckBox(text=t)
        cbx[p][t].geometry = x, y, 80, 25
        win.add(cbx[p][t])
    x += 90; y = 0

# Set the CheckBox values
mode, mask = os.stat(filename)[0], 256
for p in people:
    for t in types:
        cbx[p][t].on = mode & mask
        mask = mask >> 1

# Callbacks
def chmod(**kw):
    mode, mask = 0, 256
    for p in people:
        for t in types:
            if cbx[p][t].on:
                mode = mode | mask
            mask = mask >> 1
    os.chmod(filename, mode)
    sys.exit()

def exit(**kw): sys.exit()

opt = Options(y=140, width=80, height=25)

cancel = Button(opt, x=100, text='Cancel')
ok     = Button(opt, x=190, text='OK')

link(cancel, exit)
link(ok, chmod)

win.add(cancel, ok)
app.run()
