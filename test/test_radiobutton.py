from anygui import *
from anygui.Utils import log

app = Application()

def report(**kw):
    log("Radio button clicked")
    btn.on = not btn.on

win = Window(width = 160, height = 90)
app.add(win)
btn = RadioButton(x = 30, y = 30, width = 100, height = 30, 
		  title = "Radio Button")
link(btn, report)
win.add(btn)

app.run()
