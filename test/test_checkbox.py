from anygui import *

app = Application()

def report(**kw):
    print "Check box set to", box.on

win = Window(width = 140, height = 90)
box = CheckBox(x = 30, y = 30, width = 80, height = 30, 
	       text = "Check Box", on=1)
link(box, 'action', report)

win.add(box)

app.run()
