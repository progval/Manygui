from anygui import *

app = Application()

def report(**kw):
    print "Radio button clicked"
    btn.on = not btn.on

win = Window(width = 160, height = 90)
btn = RadioButton(x = 30, y = 30, width = 100, height = 30, 
		  title = "Radio Button")
link(btn, 'action', report)
win.add(btn)

app.run()
