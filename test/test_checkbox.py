from anygui import Window, CheckBox, Application, BooleanModel

app = Application()

def report():
  print "Check box set to", box.on

win = Window(width = 140, height = 90)
box = CheckBox(x = 30, y = 30, width = 80, height = 30, 
	       text = "Check Box", action = report, on=1)

win.add(box)

app.run()
