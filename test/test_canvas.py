from anygui import *

# Only javagui implements this so far:
from anygui.backends.javagui import Canvas

app = Application()
win = Window()
cvs = Canvas(size=win.size)
win.add(cvs)
app.run()
