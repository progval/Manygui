from anygui import Window, RadioButton, application

def report():
  print "Radio button clicked"
  btn.on = not btn.on

win = Window(width = 160, height = 90)
btn = RadioButton(x = 30, y = 30, width = 100, height = 30, 
		  title = "Radio Button", action = report)
win.add(btn)
win.show()

application().run()
