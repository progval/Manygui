from anygui import *
from anygui.Utils import log

app = Application()

def report(event):
    log("Check box set to", box.on)

win = Window(width = 140, height = 90)
app.add(win)
box = CheckBox(x = 30, y = 30, width = 100, height = 30, 
	       text = "Check Box", on=1)
link(box, report)

win.add(box)

app.run()
