from anygui import *
from anygui.Colors import *

# Only javagui implements this so far:
from anygui.backends.javagui import Canvas

app = Application()
win = Window()
cvs = Canvas(size=win.size)
win.add(cvs)

x, y = win.width/2, win.height/2
r = 100

# Doesn't look quite right, for some reason :P
cvs.drawEllipse(x-r, y-r, x+r, y+r,
                edgeColor=red,
                fillColor=green,
                edgeWidth=30)

app.run()
