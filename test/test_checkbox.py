from anygui import Window, CheckBox, Application, BooleanModel

app = Application()

def report():
  print "Check box set to", box.model.value

m = BooleanModel(value=1)

win = Window(width = 140, height = 90)
box = CheckBox(x = 30, y = 30, width = 80, height = 30, 
	       text = "Check Box", action = report, model=m)

win.add(box)
win.show()

app.run()
